# GIF IT - Create GIF & MP4 animations from a folder of images

**GIF IT v0.6.1 Beta** — Code by C1t1zen with AI assistance

> BETA RELEASE — Always make backups of your images first!

## About

GIF IT creates GIF and MP4 animations from a folder of sequentially named images.
Built for making memes and quick animations — designed to be intuitive and fast.

**Supported image formats:** PNG, JPG, JPEG, BMP, WebP

### What's New in v0.6.0

- **Modern UI** — Rebuilt with CustomTkinter for a clean, modern look
- **Frame Preview** — Browse loaded frames with arrow keys or buttons before creating
- **MP4 Export** — Output as MP4 (H.264 or H.265) in addition to GIF
- **Expandable Layout** — Controls panel + preview panel that appears when a folder is loaded
- **Guided Tour** — First-run walkthrough highlights every feature step by step
- **Hover Tooltips** — Hints on every control (toggle on/off)
- **Cross-Platform** — Runs on Windows, Linux, and macOS
- **Bug Fixes** — Fixed dithering, duplicate image loading, progress tracking, and more

### Changelog

- v0.6.0 — Modern UI, frame preview, MP4 export, tutorial system, cross-platform
- v0.5.2 — Toggle to open after creation, type size/color values directly
- v0.3.8 — Dissolve between frames, resize output, limit colors
- v0.2.3 — Dithering, drag-and-drop, auto-name from folder
- v0.1.3 — Initial release

## Setup (from source)

```bash
pip install -r requirements.txt
python GIF_IT_v_beta_060.py
```

## Build Standalone Executable

```bash
pip install pyinstaller
pyinstaller GIF_IT.spec
```

The executable will be in the `dist/` folder.

## Usage

### Controls

1. **NAME IT** — Name for the output file. Leave blank to use the folder name.
2. **TIME IT** — Frame duration in milliseconds (1000 ms = 1 second per frame).
3. **DISSOLVE IT** — Number of cross-fade frames between each image (0 = none).
4. **SIZE** — Scale output from 0.1x to 8x original size.
5. **COLORS** — Limit palette from 1 to 256 colors.
6. **OPEN IT** — Auto-open the output file when done.
7. **DITHER** — Dithering algorithm: NONE, FLOYDSTEINBERG, ORDERED, or RASTERIZE.
8. **FORMAT** — Output as GIF, MP4 (H.264), or MP4 (H.265).

### Creating an Animation

- Click **LOAD FOLDER** to browse and preview frames, then click **GIF IT UP** to create.
- Or click **GIF IT UP** directly to select a folder and create in one step.
- Or **drag and drop** a folder onto the GIF IT UP button.
- Use **Left/Right arrow keys** or the **< Prev / Next >** buttons to step through frames.

A progress bar tracks the conversion. Once complete, the status shows "Great Success!"
The output file is saved in the parent directory of the image folder.

## Notes

- Images should be the same dimensions for best results.
- Name files sequentially (e.g., `frame_001.png`, `frame_002.png`, etc.).
- MP4 export requires ffmpeg (auto-provided via `imageio[ffmpeg]`, or install system ffmpeg).
- If the output name is not changed, the previous file will be overwritten.

## Links

- https://c1t1zen.com/

Happy animating! :)
