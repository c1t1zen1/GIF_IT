# GIF IT v0.6.0 Release Notes

## 🎉 Major Update - Complete UI Overhaul & New Features

### ✨ New Features
- **🎨 Modern UI with Dark/Light Themes**
  - Beautiful new interface using CustomTkinter
  - Toggle between light (default cyan/baby blue) and dark themes
  - Expandable layout with controls on left, preview on right
  - Window size increased to 950x850px for better usability

- **🖼️ Image Preview System**
  - Real-time frame preview panel
  - Navigate with Left/Right arrow keys or on-screen buttons
  - Visual feedback for selected frames

- **📋 Image Reordering**
  - Drag-and-drop file list management
  - Move frames up/down with dedicated buttons
  - Delete unwanted frames
  - Add new frames to existing projects

- **🎬 Dual Export Formats**
  - **GIF**: Classic animated GIF format
  - **MP4**: H.265 video format for better quality/size ratio

### 🔧 Technical Improvements
- **Class-based Architecture**: Complete rewrite from procedural to object-oriented design
- **Tooltip System**: Helpful hints with toggle option
- **First-run Tour**: Guided introduction for new users
- **Config Persistence**: Saves user preferences (theme, tooltips, etc.)
- **Cross-platform Support**: Windows, Linux, and macOS compatibility

### ⚠️ Important Note - MP4 Export
For **MP4 export functionality**, FFmpeg is required:
- **First MP4 export only**: You'll be prompted to download FFmpeg separately
- **Automatic detection**: App will guide you through the process
- **One-time setup**: After installation, MP4 export works seamlessly

### 📦 Installation & Dependencies
- Updated requirements with CustomTkinter, imageio[ffmpeg], and tkinterdnd2
- PyInstaller build configuration included for standalone executables
- FFmpeg handled gracefully with system fallback options

### 🐛 Bug Fixes
- Improved file handling and error recovery
- Better memory management for large image sets
- Enhanced stability across different operating systems

---

**Upgrade from v0.5.5**: This is a major rewrite with breaking changes. All previous configurations will be reset to accommodate the new architecture.

**Download**: Get the latest version from the Releases section or build from source using the provided requirements.txt and GIF_IT.spec file.
