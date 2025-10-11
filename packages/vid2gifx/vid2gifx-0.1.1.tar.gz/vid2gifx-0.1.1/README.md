# vi2gifx — FFmpeg-only video → GIF converter

A clean, configurable Python CLI that converts and optimizes videos to GIFs using FFmpeg’s **palettegen → paletteuse** workflow.
Includes optional **size targeting** (stay under a byte budget), **frame-accurate seek**, and **VFR preservation**.

---

## Installation (from PyPI)

```bash
# 1) Have FFmpeg installed and on your PATH
#    macOS:  brew install ffmpeg
#    Ubuntu: sudo apt-get install ffmpeg
#    Windows: winget install ffmpeg  (or download from gyan.dev)
#    Verify:  ffmpeg -version

# 2) Install the CLI
pip install vi2gifx
```

> After install you’ll have a shell command named **`vi2gifx`**.

---

## Quick start

```bash
vi2gifx input.mp4 output.gif
```

Converts the whole video using a good default FPS and an adaptive palette for quality colors.

---

## Common recipes (copy-paste friendly)

> Each example includes what it does.

1. **Social-ready (smaller, crisp)**

```bash
vi2gifx in.mp4 out.gif --preset social
```

`fps=12`, `width=480` — great balance of size & clarity.

2. **Tiny footprint (docs, PRs, chats)**

```bash
vi2gifx in.mp4 out.gif --preset tiny
```

`fps=8`, `width=360`, `colors=64` — aggressively small.

3. **High-quality demo**

```bash
vi2gifx in.mp4 out.gif --preset hq
```

Higher FPS/width; larger files.

4. **Cap width (keep aspect)**

```bash
vi2gifx in.mp4 out.gif --width 480
```

5. **Fixed dimensions (may change aspect)**

```bash
vi2gifx in.mp4 out.gif --width 640 --height 360
```

6. **Lower FPS for size**

```bash
vi2gifx in.mp4 out.gif --fps 10
```

7. **Limit colors for size**

```bash
vi2gifx in.mp4 out.gif --colors 96
```

8. **Change dithering style**

```bash
vi2gifx in.mp4 out.gif --dither floyd_steinberg
```

9. **Trim a segment**

```bash
vi2gifx in.mp4 out.gif --start 3.2 --duration 6.5
```

10. **Frame-accurate trimming (avoid keyframe snap)**

```bash
vi2gifx in.mp4 out.gif --start 3.2 --duration 6.5 --seek-accurate
```

11. **Preserve original timing (VFR)**

```bash
vi2gifx in.mp4 out.gif --keep-vfr
```

Skips the `fps` filter; uses per-frame delays.

12. **Crop before scaling**

```bash
vi2gifx in.mp4 out.gif --crop 480:480:100:60 --width 480
```

13. **Deinterlace first**

```bash
vi2gifx in.mp4 out.gif --deinterlace
```

14. **Control loop count**

```bash
vi2gifx in.mp4 out.gif --loop 0   # infinite (default)
vi2gifx in.mp4 out.gif --loop 1   # play once
```

15. **Hard cap the final size (size targeting)**

```bash
vi2gifx in.mp4 out.gif --max-bytes 4_000_000
```

Iteratively shrinks **colors → fps → width** until ≤ 4 MB (respects floors).

16. **Size cap with quality floors**

```bash
vi2gifx in.mp4 out.gif --max-bytes 3_000_000 --min-colors 48 --min-fps 8 --min-width 320
```

17. **Motion-first preference**

```bash
vi2gifx in.mp4 out.gif --max-bytes 4_000_000 --min-fps 12
```

Keeps FPS higher; reduces colors/width instead.

---

## How size targeting works (brief)

When you pass `--max-bytes`, **vi2gifx** performs first-fit trials that reduce **colors → fps → width** along gentle ladders (e.g., colors 256→128→96→64, fps 12→…→6, width 720→…→min) and stops at the first result under your byte budget. If nothing fits, it writes a **best-effort** file using the floors and warns that it’s over budget. Steer trade-offs with `--min-colors`, `--min-fps`, `--min-width`.

---

## CLI reference

```text
usage: vi2gifx INPUT OUTPUT [options]

positional arguments:
  INPUT                  Input video file
  OUTPUT                 Output GIF path (e.g., out.gif)

core quality/size:
  --fps INT              Frames per second (default 12 unless --keep-vfr)
  --width INT            Scale to this width (keeps aspect unless height also set)
  --height INT           Scale to this height (keeps aspect unless width also set)
  --colors INT           Palette colors (2–256). Fewer = smaller

advanced tuning:
  --dither {none,bayer,floyd_steinberg,sierra2,sierra2_4a}
                        Dither algorithm (default: sierra2_4a)
  --stats-mode {full,diff}
                        palettegen statistics mode (default: full)

trim/crop/deinterlace:
  --start FLOAT          Start time in seconds
  --duration FLOAT       Duration in seconds
  --crop W:H:X:Y         Crop region before scaling
  --deinterlace          Apply yadif for interlaced sources

timing/mux:
  --keep-vfr             Preserve source timing (omit fps filter; per-frame delays)
  --seek-accurate        Put -ss/-t after -i for frame-accurate trimming
  --loop INT             GIF loop count (0=infinite, 1=once, ...)

presets:
  --preset {social,tiny,hq}
                        Convenience starting points you can still override

size targeting:
  --max-bytes INT        Try to keep final GIF ≤ this many bytes
  --min-fps INT          Floor when shrinking FPS (default: 6)
  --min-width INT        Floor when shrinking width (default: 240)
  --min-colors INT       Floor when shrinking colors (default: 32)
```

---

## Quality tips

* Tiny yet readable: `--fps 10 --width 360 --colors 64`
* Keep text/UI sharp: prefer lowering **colors** before **width**
* Preserve pacing: `--keep-vfr` (if viewers act weird, go back to fixed `--fps`)
* Trim aggressively: `--start` / `--duration` save more bytes than any other knob

---

## Troubleshooting

* **“ffmpeg not found”** → Install FFmpeg and ensure it’s on your PATH (`ffmpeg -version`).
* **Starts a bit early** → Use `--seek-accurate` for frame-accurate trims.
* **Choppy playback** → Increase `--fps`, or relax size floors so FPS doesn’t drop too low.
* **Persistent banding with low colors** → Try a different `--dither` (e.g., `floyd_steinberg`).

---

## License

MIT
