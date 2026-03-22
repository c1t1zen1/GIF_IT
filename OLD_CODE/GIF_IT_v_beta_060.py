import os
import sys
import json
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ---------------------------------------------------------------------------
# Try to import tkinterdnd2 for drag-and-drop support
# ---------------------------------------------------------------------------
HAS_DND = False
try:
    import tkinterdnd2
    HAS_DND = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Try to import imageio for MP4 / H.264 / H.265 export
# ---------------------------------------------------------------------------
try:
    import imageio.v3 as iio
    from imageio_ffmpeg import get_ffmpeg_exe as _iio_ffmpeg
    HAS_IMAGEIO_FFMPEG = True
except ImportError:
    HAS_IMAGEIO_FFMPEG = False

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

# ---------------------------------------------------------------------------
# Paths & Config
# ---------------------------------------------------------------------------
CONFIG_DIR = Path.home() / ".gif_it"
CONFIG_FILE = CONFIG_DIR / "gif_it_config.json"

DEFAULT_CONFIG = {
    "first_run_done": False,
    "tooltips_enabled": True,
    "theme": "Light",
}


def resource_path(relative: str) -> str:
    """Return absolute path to a bundled resource (works with PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def open_file_cross_platform(filepath: str):
    """Open a file with the default application on any OS."""
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])


def find_ffmpeg() -> str | None:
    """Return path to ffmpeg binary, or None."""
    if HAS_IMAGEIO_FFMPEG:
        try:
            return _iio_ffmpeg()
        except Exception:
            pass
    # Fallback: system PATH
    return shutil.which("ffmpeg")


# ---------------------------------------------------------------------------
# Tooltip helper
# ---------------------------------------------------------------------------
class ToolTip:
    """Hover tooltip for any widget. Reliably hides when mouse leaves."""

    def __init__(self, widget, text: str, enabled_var=None):
        self.widget = widget
        self.text = text
        self.enabled_var = enabled_var
        self.tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule_show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule_show(self, _event=None):
        self._cancel_schedule()
        self._after_id = self.widget.after(400, self._show)

    def _cancel_schedule(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self, _event=None):
        self._after_id = None
        if self.enabled_var and not self.enabled_var.get():
            return
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        # Prevent the tooltip from grabbing focus
        tw.wm_attributes("-disabled", True)
        label = ctk.CTkLabel(tw, text=self.text, corner_radius=6,
                             fg_color=("#e0e0e0", "#333333"),
                             text_color=("#000000", "#ffffff"),
                             padx=8, pady=4)
        label.pack()

    def _hide(self, _event=None):
        self._cancel_schedule()
        tw = self.tip_window
        self.tip_window = None
        if tw:
            try:
                tw.destroy()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Guided Tour
# ---------------------------------------------------------------------------
class GuidedTour:
    """First-run step-by-step walkthrough."""

    def __init__(self, app: "GifItApp"):
        self.app = app
        self.steps: list[tuple[ctk.CTkBaseClass, str]] = []
        self.current = 0
        self.overlay = None

    def add_step(self, widget, text: str):
        self.steps.append((widget, text))

    def start(self):
        if not self.steps:
            return
        self.current = 0
        self._show_step()

    def _show_step(self):
        if self.overlay:
            self.overlay.destroy()
        widget, text = self.steps[self.current]
        self.app.update_idletasks()

        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 6

        self.overlay = ov = ctk.CTkToplevel(self.app)
        ov.wm_overrideredirect(True)
        ov.attributes("-topmost", True)
        ov.configure(fg_color=("#dff0ff", "#1a2a3a"))

        frame = ctk.CTkFrame(ov, fg_color="transparent")
        frame.pack(padx=10, pady=10)

        step_label = ctk.CTkLabel(frame, text=f"Step {self.current + 1}/{len(self.steps)}",
                                  font=ctk.CTkFont(size=11, weight="bold"))
        step_label.pack(anchor="w")

        msg = ctk.CTkLabel(frame, text=text, wraplength=250, justify="left")
        msg.pack(pady=(4, 8))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        if self.current < len(self.steps) - 1:
            ctk.CTkButton(btn_frame, text="Next", width=70, command=self._next).pack(side="right", padx=2)
        else:
            ctk.CTkButton(btn_frame, text="Done", width=70, command=self._finish).pack(side="right", padx=2)
        ctk.CTkButton(btn_frame, text="Skip", width=70, fg_color="gray",
                       command=self._finish).pack(side="right", padx=2)

        ov.update_idletasks()
        ow = ov.winfo_width()
        ox = max(0, x - ow // 2)
        ov.wm_geometry(f"+{ox}+{y}")

    def _next(self):
        self.current += 1
        self._show_step()

    def _finish(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        cfg = self.app.config
        cfg["first_run_done"] = True
        save_config(cfg)


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------
class GifItApp(ctk.CTk):
    """GIF IT — Create GIF & MP4 animations from a folder of images."""

    COMPACT_WIDTH = 280
    EXPANDED_WIDTH = 950
    WINDOW_HEIGHT = 850

    def __init__(self):
        super().__init__()

        # ---- DnD init ----
        self._dnd_loaded = False
        if HAS_DND:
            try:
                tkdnd_dir = os.path.join(
                    os.path.dirname(tkinterdnd2.__file__), "tkdnd"
                )
                self.tk.eval(f'lappend auto_path {{{tkdnd_dir}}}')
                self.tk.eval('package require tkdnd')
                self._dnd_loaded = True
            except Exception:
                pass

        # ---- Config ----
        self.config = load_config()
        self.tooltips_enabled = ctk.BooleanVar(value=self.config.get("tooltips_enabled", True))

        # ---- Theme ----
        self._theme = self.config.get("theme", "Light")
        ctk.set_appearance_mode(self._theme)
        ctk.set_default_color_theme("blue")

        # ---- Window setup ----
        self.title("GIF IT")
        self._set_icon()
        self.geometry(f"{self.COMPACT_WIDTH}x{self.WINDOW_HEIGHT}+300+200")
        self.minsize(self.COMPACT_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(False, False)
        self._apply_bg_color()

        # ---- State ----
        self.folder_path: str | None = None
        self.image_files: list[str] = []
        self.preview_index = 0
        self.preview_photo = None  # prevent GC
        self._preview_expanded = False

        # ---- Build UI ----
        self._build_controls_panel()
        self._build_preview_panel()

        # ---- Keyboard bindings ----
        self.bind("<Left>", lambda e: self._prev_frame())
        self.bind("<Right>", lambda e: self._next_frame())

        # ---- Guided tour ----
        self.tour = GuidedTour(self)
        self._register_tour_steps()
        self.after(600, self._maybe_show_tour)

    # ------------------------------------------------------------------
    # Window background color (powder blue in light mode)
    # ------------------------------------------------------------------
    def _apply_bg_color(self):
        """Set the main window background to powder blue in Light mode."""
        if self._theme == "Light":
            self.configure(fg_color="#B0E0E6")
        else:
            self.configure(fg_color="#1a1a1a")

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------
    def _set_icon(self):
        try:
            if sys.platform == "win32":
                self.iconbitmap(resource_path("GIF_IT_ICON2.ico"))
            else:
                icon = ImageTk.PhotoImage(Image.open(resource_path("icon_32.png")))
                self.wm_iconphoto(True, icon)
                self._icon_ref = icon  # prevent GC
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Drag & Drop support (low-level tkdnd for CTk widgets)
    # ------------------------------------------------------------------
    def _setup_dnd(self, widget):
        """Register a widget (or the whole window) as a DnD drop target."""
        if not self._dnd_loaded:
            return
        try:
            # CTkButton uses an internal canvas; target that for DnD
            target = widget
            if hasattr(widget, "_canvas"):
                target = widget._canvas
            widget_path = str(target)
            self.tk.call("tkdnd::drop_target", "register", widget_path, "DND_Files")
            target.bind("<<Drop>>", self._on_drop_tk)
        except Exception:
            pass

    def _on_drop_tk(self, event):
        """Handle raw tkdnd drop event."""
        path = event.data.strip("{}")
        if os.path.isdir(path):
            self._load_folder(path)

    # ------------------------------------------------------------------
    # Controls (left panel)
    # ------------------------------------------------------------------
    def _build_controls_panel(self):
        # powder blue light / dark bg
        self.controls = ctk.CTkFrame(self, width=self.COMPACT_WIDTH,
                                      fg_color=("#B0E0E6", "#2b2b2b"))
        self.controls.pack(side="left", fill="y", padx=10, pady=10)
        self.controls.pack_propagate(False)

        # Logo
        try:
            logo_img = Image.open(resource_path("GIF_IT.png"))
            self._logo = ctk.CTkImage(light_image=logo_img, size=(200, 80))
            ctk.CTkLabel(self.controls, image=self._logo, text="").pack(pady=(0, 6))
        except Exception:
            ctk.CTkLabel(self.controls, text="GIF IT", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 6))

        # -- NAME IT --
        ctk.CTkLabel(self.controls, text="NAME IT", font=ctk.CTkFont(weight="bold")).pack(pady=(4, 0))
        self.name_entry = ctk.CTkEntry(self.controls, placeholder_text="output name", justify="center")
        self.name_entry.pack(pady=2, fill="x")

        # -- TIME IT --
        ctk.CTkLabel(self.controls, text="TIME IT (ms)", font=ctk.CTkFont(weight="bold")).pack(pady=(4, 0))
        self.speed_entry = ctk.CTkEntry(self.controls, justify="center")
        self.speed_entry.insert(0, "100")
        self.speed_entry.pack(pady=2, fill="x")

        # -- DISSOLVE IT --
        ctk.CTkLabel(self.controls, text="DISSOLVE IT (Frames)", font=ctk.CTkFont(weight="bold")).pack(pady=(4, 0))
        self.dissolve_entry = ctk.CTkEntry(self.controls, justify="center")
        self.dissolve_entry.insert(0, "0")
        self.dissolve_entry.pack(pady=2, fill="x")

        # -- SIZE --
        size_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        size_frame.pack(pady=(4, 0), fill="x")
        ctk.CTkLabel(size_frame, text="SIZE", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.size_var = ctk.StringVar(value="1.00")
        self.size_display = ctk.CTkLabel(size_frame, textvariable=self.size_var, width=50)
        self.size_display.pack(side="right")
        ctk.CTkLabel(size_frame, text="X").pack(side="right", padx=2)

        self.size_slider = ctk.CTkSlider(self.controls, from_=0.1, to=8.0, number_of_steps=79,
                                          command=lambda v: self.size_var.set(f"{v:.2f}"))
        self.size_slider.set(1.0)
        self.size_slider.pack(pady=2, fill="x")

        # -- COLORS --
        colors_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        colors_frame.pack(pady=(4, 0), fill="x")
        ctk.CTkLabel(colors_frame, text="COLORS", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.colors_var = ctk.StringVar(value="256")
        self.colors_display = ctk.CTkLabel(colors_frame, textvariable=self.colors_var, width=50)
        self.colors_display.pack(side="right")

        self.colors_slider = ctk.CTkSlider(self.controls, from_=1, to=256, number_of_steps=255,
                                            command=lambda v: self.colors_var.set(f"{int(v)}"))
        self.colors_slider.set(256)
        self.colors_slider.pack(pady=2, fill="x")

        # -- OPEN IT --
        self.open_after = ctk.BooleanVar(value=False)
        self.open_check = ctk.CTkCheckBox(self.controls, text="Open When Done", variable=self.open_after,
                                           font=ctk.CTkFont(weight="bold"))
        self.open_check.pack(pady=4)

        # -- DITHER --
        self.dither_methods = ["NONE", "FLOYDSTEINBERG", "ORDERED", "RASTERIZE"]
        self.dither_var = ctk.StringVar(value="NONE")
        ctk.CTkLabel(self.controls, text="DITHER", font=ctk.CTkFont(weight="bold")).pack(pady=(4, 0))
        self.dither_menu = ctk.CTkOptionMenu(self.controls, values=self.dither_methods,
                                              variable=self.dither_var)
        self.dither_menu.pack(pady=2, fill="x")

        # -- FORMAT --
        self.format_options = ["GIF", "MP4 (H.264)", "MP4 (H.265)"]
        self.format_var = ctk.StringVar(value="GIF")
        ctk.CTkLabel(self.controls, text="FORMAT", font=ctk.CTkFont(weight="bold")).pack(pady=(4, 0))
        self.format_menu = ctk.CTkOptionMenu(self.controls, values=self.format_options,
                                              variable=self.format_var)
        self.format_menu.pack(pady=2, fill="x")

        # -- Buttons --
        btn_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        btn_frame.pack(pady=6, fill="x")

        self.load_btn = ctk.CTkButton(btn_frame, text="LOAD FOLDER", command=self._browse_folder,
                                       fg_color="#4a9ecc", hover_color="#3788b4")
        self.load_btn.pack(fill="x", pady=2)

        # Button bg matches the controls panel so the image blends in.
        # Only the border highlights on hover (fg_color == hover_color = static).
        _btn_bg = ("#B0E0E6", "#B0E0E6")  # powder blue in both themes
        _btn_border     = ("#B0E0E6", "#B0E0E6")  # invisible at rest
        _btn_border_hov = ("#3788b4", "#4a9ecc")  # visible on hover
        try:
            gif_btn_img = Image.open(resource_path("GIF_IT_UP.png"))
            self._gif_btn_photo = ctk.CTkImage(light_image=gif_btn_img, size=(gif_btn_img.width, gif_btn_img.height))
            self.create_btn = ctk.CTkButton(btn_frame, text="", image=self._gif_btn_photo,
                                             command=self._on_create,
                                             fg_color=_btn_bg,
                                             hover_color=_btn_bg,
                                             border_width=2,
                                             border_color=_btn_border,
                                             height=44, hover=False)
        except Exception:
            self.create_btn = ctk.CTkButton(btn_frame, text="GIF IT UP", command=self._on_create,
                                             fg_color=_btn_bg,
                                             hover_color=_btn_bg,
                                             border_width=2,
                                             border_color=_btn_border,
                                             text_color=("#1a4a5a", "#ffffff"),
                                             height=44, hover=False,
                                             font=ctk.CTkFont(size=14, weight="bold"))
        self.create_btn.pack(fill="x", pady=2)
        # Hover effect: only change the border outline
        self._gif_btn_border = _btn_border
        self._gif_btn_border_hov = _btn_border_hov
        self.create_btn.bind("<Enter>",
            lambda e: self.create_btn.configure(border_color=self._gif_btn_border_hov), add="+")
        self.create_btn.bind("<Leave>",
            lambda e: self.create_btn.configure(border_color=self._gif_btn_border), add="+")

        # -- Drag & Drop --
        self._setup_dnd(self.create_btn)

        # -- Progress --
        self.progress = ctk.CTkProgressBar(self.controls, mode="determinate")
        self.progress.set(0)
        self.progress.pack(pady=(6, 0), fill="x")

        self.progress_label = ctk.CTkLabel(self.controls, text="")
        self.progress_label.pack()

        self.status_label = ctk.CTkLabel(self.controls, text="")
        self.status_label.pack()

        # -- Credits --
        ctk.CTkLabel(self.controls, text="Code by C1t1zen & AI",
                      font=ctk.CTkFont(size=10), text_color="gray").pack(side="bottom", pady=(0, 2))

        # -- Bottom bar: theme toggle + hints --
        bottom_bar = ctk.CTkFrame(self.controls, fg_color="transparent")
        bottom_bar.pack(side="bottom", fill="x", pady=(0, 2))

        self.theme_btn = ctk.CTkButton(
            bottom_bar, text="☀ Light" if self._theme == "Light" else "🌙 Dark",
            width=70, height=26, font=ctk.CTkFont(size=11),
            fg_color=("#89CFF0", "#3a3a3a"),
            hover_color=("#6bb8e0", "#555555"),
            text_color=("#1a3a4a", "#dddddd"),
            border_width=1,
            border_color=("#5ba0c0", "#555555"),
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(4, 0))

        self.tooltips_check = ctk.CTkCheckBox(bottom_bar, text="Hints", variable=self.tooltips_enabled,
                                               font=ctk.CTkFont(size=10),
                                               command=self._save_tooltip_pref, width=20)
        self.tooltips_check.pack(side="right", padx=(0, 4))

        # ---- Register tooltips ----
        self._register_tooltips()

    # ------------------------------------------------------------------
    # Preview panel (right side): image preview + file list
    # ------------------------------------------------------------------
    def _build_preview_panel(self):
        self.preview_frame = ctk.CTkFrame(self, fg_color=("#f0f0f0", "#1a1a1a"))
        # Not packed yet — shown when folder loaded

        # --- Left sub-panel: image preview ---
        self._preview_left = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self._preview_left.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)

        self.preview_label = ctk.CTkLabel(self._preview_left, text="No frames loaded",
                                           font=ctk.CTkFont(size=14))
        self.preview_label.pack(expand=True, fill="both", padx=4, pady=(4, 2))

        nav_frame = ctk.CTkFrame(self._preview_left, fg_color="transparent")
        nav_frame.pack(pady=(0, 2))

        self.prev_btn = ctk.CTkButton(nav_frame, text="◀ Prev", width=80, command=self._prev_frame)
        self.prev_btn.pack(side="left", padx=4)

        self.frame_info = ctk.CTkLabel(nav_frame, text="0 / 0", width=100)
        self.frame_info.pack(side="left", padx=4)

        self.next_btn = ctk.CTkButton(nav_frame, text="Next ▶", width=80, command=self._next_frame)
        self.next_btn.pack(side="left", padx=4)

        self.filename_label = ctk.CTkLabel(self._preview_left, text="", font=ctk.CTkFont(size=10),
                                            text_color="gray")
        self.filename_label.pack(pady=(0, 4))

        # Resize handler
        self.preview_label.bind("<Configure>", self._on_preview_resize)

        # --- Right sub-panel: file list ---
        self._filelist_panel = ctk.CTkFrame(self.preview_frame, width=220,
                                             fg_color=("#e8f4f8", "#222222"))
        self._filelist_panel.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self._filelist_panel.pack_propagate(False)

        ctk.CTkLabel(self._filelist_panel, text="FRAME LIST",
                      font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(6, 2))

        # Scrollable list of filenames
        self.filelist_scroll = ctk.CTkScrollableFrame(
            self._filelist_panel, fg_color=("#dceef5", "#2a2a2a"))
        self.filelist_scroll.pack(fill="both", expand=True, padx=4, pady=2)

        # File list action buttons
        fl_btn_frame = ctk.CTkFrame(self._filelist_panel, fg_color="transparent")
        fl_btn_frame.pack(fill="x", padx=4, pady=(2, 6))

        self._fl_up_btn = ctk.CTkButton(fl_btn_frame, text="▲", width=36, height=28,
                                          command=self._filelist_move_up)
        self._fl_up_btn.pack(side="left", padx=1)

        self._fl_down_btn = ctk.CTkButton(fl_btn_frame, text="▼", width=36, height=28,
                                            command=self._filelist_move_down)
        self._fl_down_btn.pack(side="left", padx=1)

        self._fl_del_btn = ctk.CTkButton(fl_btn_frame, text="✕", width=36, height=28,
                                           fg_color="#cc4444", hover_color="#aa3333",
                                           command=self._filelist_delete)
        self._fl_del_btn.pack(side="left", padx=1)

        self._fl_add_btn = ctk.CTkButton(fl_btn_frame, text="+ Add", width=60, height=28,
                                           command=self._filelist_add)
        self._fl_add_btn.pack(side="right", padx=1)

        # Track file list button widgets
        self._fl_buttons: list[ctk.CTkButton] = []

    # ------------------------------------------------------------------
    # Expand / collapse preview
    # ------------------------------------------------------------------
    def _expand_preview(self):
        if self._preview_expanded:
            return
        self._preview_expanded = True
        self.geometry(f"{self.EXPANDED_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.EXPANDED_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(True, True)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

    def _collapse_preview(self):
        if not self._preview_expanded:
            return
        self._preview_expanded = False
        self.preview_frame.pack_forget()
        self.resizable(False, False)
        self.geometry(f"{self.COMPACT_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.COMPACT_WIDTH, self.WINDOW_HEIGHT)

    # ------------------------------------------------------------------
    # Folder loading
    # ------------------------------------------------------------------
    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select Image Folder")
        if path:
            self._load_folder(path)

    def _load_folder(self, folder_path: str):
        self.folder_path = folder_path
        self.image_files = sorted(
            f for f in os.listdir(folder_path)
            if f.lower().endswith(SUPPORTED_EXTENSIONS)
        )
        if not self.image_files:
            self.status_label.configure(text="No images found in folder!")
            self._collapse_preview()
            return
        self.preview_index = 0
        self._expand_preview()
        self._rebuild_filelist()
        self._show_preview()
        self.status_label.configure(text=f"Loaded {len(self.image_files)} frames")

    # ------------------------------------------------------------------
    # File list management
    # ------------------------------------------------------------------
    def _rebuild_filelist(self):
        """Rebuild the scrollable file list from self.image_files."""
        # Clear existing buttons
        for btn in self._fl_buttons:
            btn.destroy()
        self._fl_buttons.clear()

        for i, fname in enumerate(self.image_files):
            btn = ctk.CTkButton(
                self.filelist_scroll, text=fname, anchor="w",
                font=ctk.CTkFont(size=11), height=24,
                fg_color="transparent",
                text_color=("#000000", "#cccccc"),
                hover_color=("#c0dfe8", "#3a3a3a"),
                command=lambda idx=i: self._filelist_select(idx)
            )
            btn.pack(fill="x", padx=2, pady=1)
            self._fl_buttons.append(btn)
        self._highlight_filelist()

    def _highlight_filelist(self):
        """Highlight the currently selected frame in the file list."""
        for i, btn in enumerate(self._fl_buttons):
            if i == self.preview_index:
                btn.configure(fg_color=("#a0d0e0", "#3a5a6a"))
            else:
                btn.configure(fg_color="transparent")

    def _filelist_select(self, idx: int):
        """Select a frame by clicking its name in the list."""
        if 0 <= idx < len(self.image_files):
            self.preview_index = idx
            self._show_preview()

    def _filelist_move_up(self):
        """Move the selected frame one position earlier in the sequence."""
        idx = self.preview_index
        if idx <= 0 or not self.image_files:
            return
        self.image_files[idx], self.image_files[idx - 1] = (
            self.image_files[idx - 1], self.image_files[idx]
        )
        self.preview_index = idx - 1
        self._rebuild_filelist()
        self._show_preview()

    def _filelist_move_down(self):
        """Move the selected frame one position later in the sequence."""
        idx = self.preview_index
        if idx >= len(self.image_files) - 1 or not self.image_files:
            return
        self.image_files[idx], self.image_files[idx + 1] = (
            self.image_files[idx + 1], self.image_files[idx]
        )
        self.preview_index = idx + 1
        self._rebuild_filelist()
        self._show_preview()

    def _filelist_delete(self):
        """Remove the selected frame from the sequence."""
        if not self.image_files:
            return
        idx = self.preview_index
        self.image_files.pop(idx)
        if not self.image_files:
            self.preview_index = 0
            self._rebuild_filelist()
            self.preview_label.configure(image=None, text="No frames")
            self.frame_info.configure(text="0 / 0")
            self.filename_label.configure(text="")
            return
        if idx >= len(self.image_files):
            self.preview_index = len(self.image_files) - 1
        self._rebuild_filelist()
        self._show_preview()
        self.status_label.configure(text=f"{len(self.image_files)} frames")

    def _filelist_add(self):
        """Add more images to the sequence via file dialog."""
        filepaths = filedialog.askopenfilenames(
            title="Add Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All files", "*.*"),
            ]
        )
        if not filepaths:
            return
        # If no folder loaded yet, use the directory of the first file
        if not self.folder_path:
            self.folder_path = os.path.dirname(filepaths[0])
        for fp in filepaths:
            fname = os.path.basename(fp)
            # Copy file to the working folder if it's from elsewhere
            dest = os.path.join(self.folder_path, fname)
            if os.path.abspath(fp) != os.path.abspath(dest):
                shutil.copy2(fp, dest)
            if fname in self.image_files:
                # Ask user if they want to import a duplicate
                proceed = messagebox.askyesno(
                    "Duplicate Frame",
                    f"'{fname}' is already in the sequence.\n\nImport it again?",
                    parent=self
                )
                if not proceed:
                    continue
            self.image_files.append(fname)
        if not self._preview_expanded:
            self._expand_preview()
        self._rebuild_filelist()
        self._show_preview()
        self.status_label.configure(text=f"{len(self.image_files)} frames")

    # ------------------------------------------------------------------
    # Frame preview navigation
    # ------------------------------------------------------------------
    def _prev_frame(self):
        if not self.image_files:
            return
        self.preview_index = (self.preview_index - 1) % len(self.image_files)
        self._show_preview()

    def _next_frame(self):
        if not self.image_files:
            return
        self.preview_index = (self.preview_index + 1) % len(self.image_files)
        self._show_preview()

    def _show_preview(self):
        if not self.image_files or self.folder_path is None:
            return
        filename = self.image_files[self.preview_index]
        filepath = os.path.join(self.folder_path, filename)
        try:
            img = Image.open(filepath)
            img = self._fit_image(img)
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=self.preview_photo, text="")
        except Exception as e:
            self.preview_label.configure(image=None, text=f"Error: {e}")
        self.frame_info.configure(text=f"{self.preview_index + 1} / {len(self.image_files)}")
        self.filename_label.configure(text=filename)
        self._highlight_filelist()

    def _fit_image(self, img: Image.Image) -> Image.Image:
        """Scale image to fit the preview panel while maintaining aspect ratio."""
        max_w = max(self.preview_label.winfo_width() - 20, 200)
        max_h = max(self.preview_label.winfo_height() - 20, 200)
        ratio = min(max_w / img.width, max_h / img.height)
        if ratio != 1.0:
            new_size = (max(1, int(img.width * ratio)), max(1, int(img.height * ratio)))
            img = img.resize(new_size, Image.LANCZOS)
        return img

    def _on_preview_resize(self, _event=None):
        """Re-render preview when panel is resized (debounced)."""
        if hasattr(self, "_resize_after_id"):
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(150, self._deferred_preview_update)

    def _deferred_preview_update(self):
        if self.image_files:
            self._show_preview()

    # ------------------------------------------------------------------
    # Creation pipeline
    # ------------------------------------------------------------------
    def _on_create(self):
        if not self.folder_path and not self.image_files:
            # No folder loaded yet — open dialog
            path = filedialog.askdirectory(title="Select Image Folder")
            if not path:
                return
            self._load_folder(path)
        if not self.image_files:
            return
        # Run in thread to keep UI responsive
        self.create_btn.configure(state="disabled")
        self.status_label.configure(text="Creating...")
        threading.Thread(target=self._create_animation, daemon=True).start()

    def _create_animation(self):
        try:
            folder = self.folder_path
            output_name = self.name_entry.get().strip() or os.path.basename(folder)
            gif_speed = int(self.speed_entry.get())
            dissolve = int(self.dissolve_entry.get())
            resample = self.size_slider.get()
            num_colors = int(self.colors_slider.get())
            dither_method = self.dither_var.get().strip()
            fmt = self.format_var.get()

            total = len(self.image_files)
            images: list[Image.Image] = []

            # ---- Load & process images ----
            for i, filename in enumerate(self.image_files):
                img_path = os.path.join(folder, filename)
                img = Image.open(img_path).convert("RGBA")

                # Resize
                if resample != 1.0:
                    new_size = (int(img.width * resample), int(img.height * resample))
                    img = img.resize(new_size, Image.LANCZOS)

                # Color quantization
                if num_colors < 256:
                    img = img.quantize(colors=num_colors).convert("RGBA")

                # Dithering
                dither_map = {
                    "NONE": Image.Dither.NONE,
                    "FLOYDSTEINBERG": Image.Dither.FLOYDSTEINBERG,
                    "ORDERED": Image.Dither.ORDERED,
                    "RASTERIZE": Image.Dither.RASTERIZE,
                }
                pil_dither = dither_map.get(dither_method, Image.Dither.NONE)
                img_dithered = img.convert("P", dither=pil_dither).convert("RGBA")
                images.append(img_dithered)

                # Progress
                pct = (i + 1) / total
                self.after(0, self._update_progress, pct)

            # ---- Dissolve ----
            if dissolve > 0:
                dissolved: list[Image.Image] = []
                for i in range(len(images) - 1):
                    for j in range(dissolve):
                        alpha = j / dissolve
                        blend = Image.blend(images[i], images[i + 1], alpha)
                        dissolved.append(blend)
                dissolved.append(images[-1])
                images = dissolved

            # ---- Output ----
            output_folder = os.path.dirname(folder)
            output_path = self._save_output(images, output_folder, output_name, gif_speed, fmt)

            self.after(0, self._creation_done, output_path)

        except Exception as e:
            self.after(0, self._creation_error, str(e))

    def _save_output(self, images: list[Image.Image], output_folder: str,
                     output_name: str, speed_ms: int, fmt: str) -> str:
        """Save images as GIF or MP4."""
        if fmt == "GIF":
            path = os.path.join(output_folder, output_name + ".gif")
            # Check overwrite
            if os.path.exists(path):
                pass  # TODO: could prompt, but keeping simple for now
            frames = [img.convert("RGBA") for img in images]
            frames[0].save(
                path, save_all=True, append_images=frames[1:],
                duration=speed_ms, loop=0, optimize=True
            )
            return path
        else:
            # MP4 (H.264 or H.265)
            codec = "libx265" if "H.265" in fmt else "libx264"
            ext = ".mp4"
            path = os.path.join(output_folder, output_name + ext)
            ffmpeg_exe = find_ffmpeg()
            if ffmpeg_exe is None:
                raise RuntimeError(
                    "ffmpeg not found. Install imageio[ffmpeg] or add ffmpeg to PATH."
                )
            fps = max(1, round(1000 / speed_ms))
            # Convert PIL images to RGB numpy arrays
            if not HAS_NUMPY:
                raise RuntimeError("numpy is required for MP4 export. Install with: pip install numpy")
            rgb_frames = []
            for img in images:
                arr = np.array(img.convert("RGB"))
                # Ensure even dimensions (required by H.264/H.265)
                h, w = arr.shape[:2]
                if h % 2 != 0:
                    arr = arr[:h - 1, :, :]
                if w % 2 != 0:
                    arr = arr[:, :w - 1, :]
                rgb_frames.append(arr)

            # Write frames to temp PNGs and encode via ffmpeg
            tmpdir = tempfile.mkdtemp(prefix="gifit_")
            try:
                for idx, frame_arr in enumerate(rgb_frames):
                    Image.fromarray(frame_arr).save(
                        os.path.join(tmpdir, f"frame_{idx:06d}.png")
                    )
                subprocess.run([
                    ffmpeg_exe, "-y", "-framerate", str(fps),
                    "-i", os.path.join(tmpdir, "frame_%06d.png"),
                    "-c:v", codec, "-pix_fmt", "yuv420p", path
                ], check=True, capture_output=True)
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
            return path

    def _update_progress(self, pct: float):
        self.progress.set(pct)
        self.progress_label.configure(text=f"{int(pct * 100)}%")

    def _creation_done(self, output_path: str):
        self.progress.set(1.0)
        self.progress_label.configure(text="100%")
        self.status_label.configure(text="Great Success!")
        self.create_btn.configure(state="normal")
        if self.open_after.get():
            open_file_cross_platform(output_path)
        # Reset progress after 8s
        self.after(8000, self._reset_progress)

    def _creation_error(self, msg: str):
        self.status_label.configure(text=f"Error: {msg}")
        self.create_btn.configure(state="normal")
        self._reset_progress()

    def _reset_progress(self):
        self.progress.set(0)
        self.progress_label.configure(text="")
        self.status_label.configure(text="")

    # ------------------------------------------------------------------
    # Tooltips
    # ------------------------------------------------------------------
    def _register_tooltips(self):
        tips = {
            self.name_entry: "Name for the output file. Leave blank to use the folder name.",
            self.speed_entry: "Time per frame in milliseconds. 1000 ms = 1 second.",
            self.dissolve_entry: "Number of blend frames between each image (0 = none).",
            self.size_slider: "Scale factor: 1.0 = original, <1 shrinks, >1 enlarges.",
            self.colors_slider: "Max colors (GIF supports up to 256).",
            self.open_check: "Open the output file after creation.",
            self.dither_menu: "Dithering algorithm for color reduction.",
            self.format_menu: "Output format: GIF or MP4 video.",
            self.load_btn: "Browse for a folder of sequentially-named images.",
            self.create_btn: "Create the animation! You can also drag & drop a folder here.",
        }
        for widget, text in tips.items():
            ToolTip(widget, text, enabled_var=self.tooltips_enabled)

    def _save_tooltip_pref(self):
        self.config["tooltips_enabled"] = self.tooltips_enabled.get()
        save_config(self.config)

    # ------------------------------------------------------------------
    # Theme toggle
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        if self._theme == "Light":
            self._theme = "Dark"
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 Dark")
        else:
            self._theme = "Light"
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀ Light")
        self._apply_bg_color()
        self.config["theme"] = self._theme
        save_config(self.config)

    # ------------------------------------------------------------------
    # Guided tour
    # ------------------------------------------------------------------
    def _register_tour_steps(self):
        self.tour.add_step(self.name_entry,
                           "NAME IT — Type a name for your animation. Leave blank to use the folder name.")
        self.tour.add_step(self.speed_entry,
                           "TIME IT — Frame duration in milliseconds. 100 ms is a good start.")
        self.tour.add_step(self.dissolve_entry,
                           "DISSOLVE IT — Add cross-fade frames between each image (0 = off).")
        self.tour.add_step(self.size_slider,
                           "SIZE — Scale the output. Drag to shrink or enlarge.")
        self.tour.add_step(self.colors_slider,
                           "COLORS — Limit the palette (mainly affects GIF).")
        self.tour.add_step(self.dither_menu,
                           "DITHER — Choose a dithering style for color reduction.")
        self.tour.add_step(self.format_menu,
                           "FORMAT — Export as GIF, MP4 (H.264), or MP4 (H.265).")
        self.tour.add_step(self.load_btn,
                           "LOAD FOLDER — Pick a folder of images to preview frames before creating.")
        self.tour.add_step(self.create_btn,
                           "GIF IT UP — Create your animation! You can also drag & drop a folder here.")

    def _maybe_show_tour(self):
        if not self.config.get("first_run_done", False):
            self.tour.start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = GifItApp()
    app.mainloop()
