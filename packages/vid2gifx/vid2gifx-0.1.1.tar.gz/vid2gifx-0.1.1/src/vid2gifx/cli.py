#!/usr/bin/env python3
"""
video2gif.py — Convert & optimize a video to GIF using FFmpeg only (no gifsicle).

Highlights
- Two-pass palette workflow (palettegen + paletteuse) for quality and compact size.
- Optional size targeting (--max-bytes): iteratively reduces colors → fps → width.
- Optional accurate seeking (--seek-accurate) and VFR preservation (--keep-vfr).
- All common controls: crop, scale, deinterlace, dither, loop.

Examples
  # Quick default
  python video2gif.py in.mp4 out.gif

  # Smaller: cap width and FPS
  python video2gif.py in.mp4 out.gif --width 480 --fps 12

  # Trim & crop
  python video2gif.py in.mp4 out.gif --start 2.5 --duration 6 --crop 480:480:100:60

  # Size target (~4 MB), allow shrinking until floors
  python video2gif.py in.mp4 out.gif --preset social --max-bytes 4_000_000

  # Preserve original timing (no FPS resample) + accurate seek
  python video2gif.py in.mp4 out.gif --keep-vfr --seek-accurate
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

# ---------------------------- shell helpers ----------------------------

def which_or_die(name):
    path = shutil.which(name)
    if not path:
        sys.exit(f"Error: {name} not found in PATH.")
    return path

def run(cmd, label):
    try:
        print(f"Running {label}…", file=sys.stderr)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{label} failed (exit {e.returncode})", file=sys.stderr)
        # Uncomment to debug:
        # print("Command:", " ".join(cmd), file=sys.stderr)
        return False

# ---------------------------- media introspection ----------------------------

def probe_width(input_path):
    """Return source width via ffprobe or fallback to 720 if unavailable."""
    if not shutil.which("ffprobe"):
        return 720
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width",
            "-of", "csv=p=0",
            str(input_path)
        ], stderr=subprocess.STDOUT).decode().strip()
        w = int(out)
        return w if w > 0 else 720
    except Exception:
        return 720

# ---------------------------- filter building ----------------------------

def build_filter_chain(args):
    """
    Returns a filter string for the video stream prior to paletteuse.
    Order: deinterlace -> crop -> fps (unless keep-vfr) -> scale
    """
    filters = []

    if args.deinterlace:
        filters.append("yadif=0:-1:0")

    if args.crop:
        filters.append(f"crop={args.crop}")

    if not args.keep_vfr:
        filters.append(f"fps={args.fps}")

    # Scaling — preserve aspect unless both width & height provided
    if args.width and args.height:
        filters.append(f"scale={args.width}:{args.height}:flags=lanczos")
    elif args.width:
        filters.append(f"scale={args.width}:-2:flags=lanczos")
    elif args.height:
        filters.append(f"scale=-2:{args.height}:flags=lanczos")

    return ",".join(filters)

# ---------------------------- seek placement ----------------------------

def seek_args(args, before_input=True):
    """
    Build -ss/-t arguments either before (-fast, keyframe-aligned)
    or after input (-accurate).
    """
    pre, post = [], []
    if args.start is not None:
        (pre if before_input else post).extend(["-ss", str(args.start)])
    if args.duration is not None:
        (pre if before_input else post).extend(["-t", str(args.duration)])
    return pre, post

# ---------------------------- encoding passes ----------------------------

def pass_palettegen(input_path, palette_path, vf, args):
    # palettegen options
    opts = [f"stats_mode={args.stats_mode}"]
    if args.colors:
        opts.append(f"max_colors={args.colors}")
    palettegen = "palettegen=" + ":".join(opts)

    pre, post = seek_args(args, before_input=not args.seek_accurate)
    # Single input, single -vf
    vf_full = f"{vf},{palettegen}" if vf else palettegen

    cmd = [
        "ffmpeg",
        *pre,
        "-i", str(input_path),
        *post,
        "-vf", vf_full,
        "-y", str(palette_path)
    ]
    return run(cmd, "palette generation")

def pass_paletteuse(input_path, output_path, palette_path, vf, args):
    # Use filter_complex to wire [0:v] and [1:v] into paletteuse explicitly
    dither = args.dither
    if vf:
        graph = f"[0:v]{vf}[v];[v][1:v]paletteuse=dither={dither}[gif]"
    else:
        graph = f"[0:v][1:v]paletteuse=dither={dither}[gif]"

    pre, post = seek_args(args, before_input=not args.seek_accurate)
    cmd = [
        "ffmpeg",
        *pre,
        "-i", str(input_path),
        "-i", str(palette_path),
        *post,
        "-filter_complex", graph,
        "-map", "[gif]",
        "-gifflags", "+transdiff",
        "-loop", str(args.loop),
    ]
    if args.keep_vfr:
        cmd += ["-vsync", "vfr"]
    cmd += ["-y", str(output_path)]
    return run(cmd, "GIF encoding")

def encode_once(input_path, temp_dir, base_args):
    """
    Perform the two-pass encode once with the provided args object.
    Returns Path to staged GIF or None on failure.
    """
    args = base_args
    vf = build_filter_chain(args)
    palette_path = Path(temp_dir) / "palette.png"
    out_gif = Path(temp_dir) / "stage.gif"

    if not pass_palettegen(input_path, palette_path, vf, args) or not palette_path.exists():
        return None
    if not pass_paletteuse(input_path, out_gif, palette_path, vf, args):
        return None
    return out_gif

# ---------------------------- size targeting ----------------------------

def clone_args(args):
    return SimpleNamespace(**vars(args))

def try_fit_under_budget(input_path, final_output, args):
    """
    Shrink in quality-preserving order: colors → fps → width until file <= max_bytes.
    Uses gentle ladders and stops at the first that fits (first-fit strategy).
    """
    src_width = probe_width(input_path)
    with tempfile.TemporaryDirectory() as td:
        # Build ladders
        min_colors = args.min_colors
        min_fps    = args.min_fps
        min_width  = args.min_width

        # Colors: high → low, include user-provided if any
        color_steps = [256, 192, 160, 128, 96, 80, 64, 56, 48, 40, 32]
        if args.colors:
            color_steps.append(args.colors)
        color_steps = sorted({c for c in color_steps if c >= min_colors}, reverse=True)

        # FPS: start from chosen fps (or 12 default), go down to floor
        fps_start = args.fps
        fps_steps = sorted({fps_start, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6}, reverse=True)
        fps_steps = [f for f in fps_steps if f >= min_fps]

        # Width: start at user width if set else min(src_width, 720), step ~10% down
        w0 = args.width if args.width else min(src_width, 720)
        width_steps = []
        w = int(w0)
        while w >= min_width:
            width_steps.append(w)
            w = int(w * 0.9)
            if w == 0 or (width_steps and w == width_steps[-1]):  # guard
                break

        tried = set()

        for c in color_steps:
            for f in fps_steps:
                for w in width_steps:
                    key = (c, f, w)
                    if key in tried:
                        continue
                    tried.add(key)

                    trial = clone_args(args)
                    trial.colors = c
                    trial.fps    = f
                    trial.width  = w
                    # important: to preserve aspect while shrinking width, ignore an explicit height
                    trial.height = None

                    tmp_gif = encode_once(input_path, td, trial)
                    if not tmp_gif:
                        continue

                    size = tmp_gif.stat().st_size
                    print(f"→ Trial colors={c}, fps={f}, width={w} → {size} bytes", file=sys.stderr)
                    if size <= args.max_bytes:
                        Path(final_output).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(tmp_gif, final_output)
                        return True

        # Best-effort fallback at floors
        fallback = clone_args(args)
        fallback.colors = min_colors
        fallback.fps    = min_fps
        fallback.width  = min_width
        fallback.height = None

        tmp_gif = encode_once(input_path, td, fallback)
        if tmp_gif:
            shutil.copy2(tmp_gif, final_output)
        return False

# ---------------------------- presets & CLI ----------------------------

def apply_preset(args):
    presets = {
        "social": dict(fps=12, width=480),
        "tiny":   dict(fps=8,  width=360, colors=64),
        "hq":     dict(fps=15, width=720, dither="sierra2_4a", stats_mode="full"),
    }
    if not args.preset:
        return args
    p = presets[args.preset]
    # Only fill fields the user didn't set explicitly
    if args.fps is None and "fps" in p: args.fps = p["fps"]
    if args.width is None and "width" in p: args.width = p["width"]
    if args.height is None and "height" in p: args.height = p.get("height")
    if args.colors is None and "colors" in p: args.colors = p["colors"]
    if args.dither == "sierra2_4a" and "dither" in p: args.dither = p["dither"]
    if args.stats_mode == "full" and "stats_mode" in p: args.stats_mode = p["stats_mode"]
    return args

def parse_args():
    ap = argparse.ArgumentParser(
        description="Convert & optimize a video to GIF using FFmpeg (palettegen + paletteuse)."
    )
    ap.add_argument("input", type=Path, help="Input video file")
    ap.add_argument("output", type=Path, help="Output GIF path (e.g., out.gif)")

    # Core quality/size knobs
    ap.add_argument("--fps", type=int, default=None, help="Frames per second (default 12 unless --keep-vfr)")
    ap.add_argument("--width", type=int, help="Scale to this width (keeps aspect unless height also set)")
    ap.add_argument("--height", type=int, help="Scale to this height (keeps aspect unless width also set)")
    ap.add_argument("--colors", type=int, help="Palette colors (2–256). Fewer = smaller")

    # Advanced tuning
    ap.add_argument("--dither",
                    choices=["none", "bayer", "floyd_steinberg", "sierra2", "sierra2_4a"],
                    default="sierra2_4a",
                    help="Dither algorithm (default: sierra2_4a)")
    ap.add_argument("--stats-mode", choices=["full", "diff"], default="full",
                    help="palettegen stats mode (full tends to yield smoother gradients)")

    # Trimming / cropping / deinterlace
    ap.add_argument("--start", type=float, help="Start time in seconds")
    ap.add_argument("--duration", type=float, help="Duration in seconds")
    ap.add_argument("--crop", help="Crop as width:height:x:y")
    ap.add_argument("--deinterlace", action="store_true", help="Apply yadif deinterlace first")

    # Timing / mux
    ap.add_argument("--keep-vfr", action="store_true",
                    help="Keep variable frame rate (omit fps filter; use GIF per-frame delays)")
    ap.add_argument("--seek-accurate", action="store_true",
                    help="Place -ss/-t after -i for frame-accurate trimming (slower)")
    ap.add_argument("--loop", type=int, default=0, help="GIF loop count (0=infinite)")

    # Presets
    ap.add_argument("--preset", choices=["social", "tiny", "hq"], help="Convenience presets")

    # Size target mode (FFmpeg-only)
    ap.add_argument("--max-bytes", type=int, help="Try to keep final GIF ≤ this many bytes")
    ap.add_argument("--min-fps", type=int, default=6, help="Floor when shrinking FPS (default 6)")
    ap.add_argument("--min-width", type=int, default=240, help="Floor when shrinking width (default 240)")
    ap.add_argument("--min-colors", type=int, default=32, help="Floor when shrinking colors (default 32)")

    args = ap.parse_args()

    # Defaults
    if args.fps is None:
        args.fps = 12

    # Apply preset (user flags still win)
    if args.preset:
        args = apply_preset(args)

    return args

# ---------------------------- main ----------------------------

def main():
    args = parse_args()
    which_or_die("ffmpeg")

    if not args.input.exists():
        sys.exit(f"Input not found: {args.input}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.max_bytes:
        ok = try_fit_under_budget(args.input, args.output, args)
        final_size = args.output.stat().st_size if args.output.exists() else 0
        if ok:
            print(f"✅ Done (under budget): {args.output} ({final_size} bytes)")
        else:
            print(f"⚠️ Best-effort written: {args.output} ({final_size} bytes) — still over budget",
                  file=sys.stderr)
        return

    # One-shot encode (no size targeting)
    with tempfile.TemporaryDirectory() as td:
        staged = encode_once(args.input, td, args)
        if not staged:
            sys.exit("Failed to encode GIF.")
        shutil.copy2(staged, args.output)
    print(f"✅ Done: {args.output} ({args.output.stat().st_size} bytes)")

if __name__ == "__main__":
    main()

