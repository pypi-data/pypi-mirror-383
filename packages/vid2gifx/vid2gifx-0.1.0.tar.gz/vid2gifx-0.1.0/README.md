# video2gif — FFmpeg-only video → GIF converter

A clean, configurable Python CLI that converts and optimizes videos to GIFs using FFmpeg’s **palettegen → paletteuse** workflow.
Includes optional **size targeting** (stay under a byte budget), **frame-accurate seek**, and **VFR preservation**.

---

## Quick start

```bash
# Install ffmpeg first (macOS: brew install ffmpeg, Ubuntu: apt-get install ffmpeg, Windows: winget install ffmpeg)
python video2gif.py input.mp4 output.gif
```

---

## How this script can be used (common recipes)

> Each example includes a short description of what it does.

### 1) Default high-quality conversion

```bash
python video2gif.py in.mp4 out.gif
```

Converts using a good default FPS and palette workflow. No resizing, full clip.

### 2) Social-ready (smaller, crisp)

```bash
python video2gif.py in.mp4 out.gif --preset social
```

Sensible default for previews (`fps=12`, `width=480`), good balance of size and quality.

### 3) Tiny footprint (docs, chats)

```bash
python video2gif.py in.mp4 out.gif --preset tiny
```

Aggressively smaller (`fps=8`, `width=360`, `colors=64`) for inline docs/PRs.

### 4) High-quality demo

```bash
python video2gif.py in.mp4 out.gif --preset hq
```

Higher FPS and width for smoother playback; bigger files.

### 5) Cap width (keep aspect)

```bash
python video2gif.py in.mp4 out.gif --width 480
```

Resizes by width (height auto-computed) with high-quality Lanczos scaling.

### 6) Fixed size (both dimensions)

```bash
python video2gif.py in.mp4 out.gif --width 640 --height 360
```

Forces exact dimensions (may change aspect).

### 7) Lower the FPS

```bash
python video2gif.py in.mp4 out.gif --fps 10
```

Reduces temporal density → much smaller files.

### 8) Limit color palette

```bash
python video2gif.py in.mp4 out.gif --colors 96
```

Fewer colors = smaller GIF; quality still decent with dithering.

### 9) Change dithering style

```bash
python video2gif.py in.mp4 out.gif --dither floyd_steinberg
```

Controls how colors are approximated; default `sierra2_4a` is usually best.

### 10) Trim a segment

```bash
python video2gif.py in.mp4 out.gif --start 3.2 --duration 6.5
```

Encodes only a portion of the video.

### 11) Frame-accurate trimming

```bash
python video2gif.py in.mp4 out.gif --start 3.2 --duration 6.5 --seek-accurate
```

Places `-ss/-t` after `-i` to avoid keyframe-aligned “early start” artifacts (slower).

### 12) Preserve original timing (VFR)

```bash
python video2gif.py in.mp4 out.gif --keep-vfr
```

Skips the `fps` filter; uses per-frame delays to keep source pacing.

### 13) Crop before scaling

```bash
python video2gif.py in.mp4 out.gif --crop 480:480:100:60 --width 480
```

Cuts to a region (`width:height:x:y`), then scales. Great for removing borders/UIs.

### 14) Deinterlace first

```bash
python video2gif.py in.mp4 out.gif --deinterlace
```

Applies `yadif` for interlaced sources.

### 15) Control loop count

```bash
python video2gif.py in.mp4 out.gif --loop 0     # infinite (default)
python video2gif.py in.mp4 out.gif --loop 1     # play once
```

Sets the repeat behavior for the GIF.

### 16) Enforce a max file size (size targeting)

```bash
python video2gif.py in.mp4 out.gif --max-bytes 4_000_000
```

Iteratively shrinks **colors → fps → width** until the GIF fits under 4 MB
(uses floors to protect quality; see next examples).

### 17) Size targeting with quality floors

```bash
python video2gif.py in.mp4 out.gif --max-bytes 3_000_000 --min-colors 48 --min-fps 8 --min-width 320
```

Keeps at least 48 colors, 8 FPS, and 320px width while trying to meet 3 MB.

### 18) Combine preset + size cap

```bash
python video2gif.py in.mp4 out.gif --preset social --max-bytes 4_000_000
```

Starts from a reasonable baseline, then shrinks only if needed.

### 19) Crisp UI/text with fewer colors

```bash
python video2gif.py in.mp4 out.gif --width 480 --fps 12 --colors 64
```

Keeps resolution and motion; reduces palette for significant size savings.

### 20) Motion-first preference

```bash
python video2gif.py in.mp4 out.gif --max-bytes 4_000_000 --min-fps 12
```

Tells the search to avoid dropping FPS much; it will reduce colors/width instead.

---

## Full CLI

```text
positional arguments:
  input                   Input video file
  output                  Output GIF path (e.g., out.gif)

core quality/size:
  --fps INT               Frames per second (default 12 unless --keep-vfr)
  --width INT             Scale to this width (keeps aspect unless height also set)
  --height INT            Scale to this height (keeps aspect unless width also set)
  --colors INT            Palette colors (2–256). Fewer = smaller

advanced tuning:
  --dither {none,bayer,floyd_steinberg,sierra2,sierra2_4a}
                          Dither algorithm (default: sierra2_4a)
  --stats-mode {full,diff}
                          palettegen statistics mode (default: full)

trim/crop/deinterlace:
  --start FLOAT           Start time in seconds
  --duration FLOAT        Duration in seconds
  --crop W:H:X:Y          Crop before scaling (e.g., 480:480:100:60)
  --deinterlace           Apply yadif deinterlace

timing/mux:
  --keep-vfr              Preserve source timing (omit fps filter; per-frame delays)
  --seek-accurate         Place -ss/-t after -i for frame-accurate trimming
  --loop INT              GIF loop count (0=infinite, 1=once, ...)

presets:
  --preset {social,tiny,hq}
                          Convenience starting points you can still override

size targeting:
  --max-bytes INT         Try to keep final GIF ≤ this many bytes
  --min-fps INT           Floor when shrinking FPS (default: 6)
  --min-width INT         Floor when shrinking width (default: 240)
  --min-colors INT        Floor when shrinking colors (default: 32)
```

---

## How size targeting works (in one paragraph)

When `--max-bytes` is set, the script does **first-fit** trials that progressively reduce **colors → fps → width** along gentle “ladder” values (e.g., colors 256→128→96→64, fps 12→11→10→…, width 720→648→… until `--min-*` floors). After each trial it measures the actual GIF and stops at the first that’s ≤ budget. If none fit, it writes a **best-effort** file using the floors and prints a warning.

---

## Quality tips

* For tiny but readable: `--fps 10 --width 360 --colors 64`
* Keep text/UI sharp: prefer reducing **colors** before reducing **width**
* Preserve pacing: `--keep-vfr` (if viewers show odd timing, go back to fixed `--fps`)
* Trim aggressively: `--start` / `--duration` save more size than any other knob

---

## Troubleshooting

* **“ffmpeg not found”** → Install FFmpeg and ensure it’s in your PATH.
* **Starts a bit early** → Use `--seek-accurate` for frame-accurate trims.
* **Choppy playback** → Increase `--fps`, or avoid size targeting floors that force low FPS.
* **Big file** even after targeting → Raise the budget or allow lower floors (`--min-*`).
* **Banding** with low colors → Try a different `--dither` (e.g., `floyd_steinberg`).

---

## License

MIT
