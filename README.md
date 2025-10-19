# 💰 LiteFinPad v3.4

<div align="center">

**A lightweight, offline-first Windows expense tracker with modern UI and powerful features**

![Version](https://img.shields.io/badge/version-3.4-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

</div>

---

## 📖 Overview

**LiteFinPad** is a streamlined Windows application for tracking monthly personal expenses. Built with Python and Tkinter, it offers a clean interface, system tray integration, and powerful analytics—all while keeping your data 100% offline and under your control.

**Perfect for**:
- 💼 Personal finance tracking
- 📊 Monthly budget monitoring  
- 🚀 Quick expense logging without opening apps
- 🔒 Users who want complete data privacy (no cloud, no accounts)

---

## ✨ Key Features

### Core Functionality
- 📝 **Quick Expense Entry**: Three ways to add expenses (inline, dialog, tray icon)
- 📊 **Real-time Analytics**: Monthly totals, weekly/daily averages, trends
- 🗂️ **Organized Data Storage**: Automatic monthly folders, JSON-based
- 🔍 **Full Expense Management**: View, edit, delete, and search expenses
- 📤 **Export Options**: Excel (.xlsx) and PDF formats with professional styling

### User Experience
- 🎨 **Modern Interface**: Clean, professional design with intuitive navigation
- ⌨️ **Keyboard Shortcuts**: Enter for navigation, Escape to close dialogs
- 🖼️ **System Tray Integration**: Always accessible, minimal screen footprint
- ↗️ **Stay on Top Mode**: Keep tracker visible while working
- 🎯 **Smart Dialogs**: Auto-focus, intelligent positioning, number pad support

### Technical Highlights
- 🔒 **Fully Offline**: No internet required, no tracking, no cloud sync
- 💾 **Automatic Backups**: Monthly archives with zero data loss
- ⚡ **Lightweight**: ~23 MB distribution, fast startup
- 🛡️ **Data Validation**: Real-time input validation prevents errors
- 📦 **Single Executable**: No Python installation required

---

## 🚀 Quick Start

### Option 1: Download Pre-Built Executable (Recommended)

1. Go to the [**Releases**](../../releases) page
2. Download the latest `LiteFinPad_v3.4.zip`
3. Extract and run `LiteFinPad_v3.4.exe`
4. Look for the icon in your system tray!

**No Python installation required. Just download and run.**

### Option 2: Run from Source

**Requirements**: Python 3.11+ (3.14 recommended), Windows 10+

```bash
# Clone the repository
git clone https://github.com/yourusername/LiteFinPad.git
cd LiteFinPad

# Install dependencies (use python -m pip for correct Python version)
python -m pip install -r requirements.txt

# Run the application
python main.py
```

---

## 📚 Usage

### First Launch
1. Application starts minimized in your **system tray** (bottom-right corner)
2. Click the 💰 icon to open the main window
3. Start adding expenses!

### Adding Expenses (3 Methods)

#### Method 1: Inline Quick Add (Fastest)
- Located at the bottom of the Expense List page
- Type amount → Press Enter → Type description → Press Enter
- Perfect for rapid consecutive entries

#### Method 2: Add Expense Dialog
- Click **"+ Add Expense"** button on Expense List page
- Includes optional number pad for touch screens
- Amount → Enter → Description → Enter to submit

#### Method 3: Quick Add from Tray (Stealthiest)
- **Double-click** the system tray icon
- Add expense without opening main window
- Great for quick logging on the go

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Enter` | Navigate between fields / Submit form |
| `Escape` | Close current dialog |
| `Double-click tray icon` | Open Quick Add dialog |

### Managing Expenses
- **View**: All expenses listed on main "Expense List" tab
- **Edit**: Right-click any expense → "Edit"
- **Delete**: Right-click any expense → "Delete"
- **Export**: Click 📤 "Export" → Choose Excel or PDF

---

## 📂 Project Structure

```
LiteFinPad/
├── main.py                  # Application entry point and logic
├── gui.py                   # Main GUI and layout
├── expense_table.py         # Expense list and dialogs
├── tray_icon.py            # System tray integration
├── export_data.py          # Excel/PDF export functionality
├── import_data.py          # JSON import validation
├── window_animation.py     # Slide-out animations
├── error_logger.py         # Error logging system
├── version_manager.py      # Version management utilities
├── requirements.txt        # Python dependencies
├── icon.ico               # Application icon
├── version.txt            # Current version number
│
├── data_YYYY-MM/          # Monthly expense data (auto-created)
│   ├── expenses.json
│   └── calculations.json
│
├── build_dev.bat          # Development build script
├── build_release.bat      # Production build script
│
└── docs/
    ├── AI_MEMORY.md              # Project development history
    ├── BUILD_SYSTEM_GUIDE.md     # Build instructions
    ├── CHANGELOG.md              # Version history
    ├── DEPENDENCIES.md           # Library documentation
    └── THIRD_PARTY_LICENSES.md   # Open-source licenses
```

---

## 🔨 Building from Source

### Quick Build (Development)
```bash
# Build current version for testing
build_dev.bat

# Build with version increment (3.0 → 3.1)
build_dev.bat increment
```

### Production Release
```bash
# Build production-ready executable
build_release.bat

# Build with major version bump (3.4 → 4.0)
build_release.bat major
```

**Output**: `dist/LiteFinPad_vX.X/LiteFinPad_vX.X.exe`

For detailed build instructions, see [**BUILD_SYSTEM_GUIDE.md**](BUILD_SYSTEM_GUIDE.md).

---

## 📦 Dependencies

### Core Libraries
| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| **pywin32** | 306+ | System tray integration | PSF License |
| **xlsxwriter** | 3.2.0+ | Excel export | BSD License |
| **fpdf** | 1.7.2 | PDF generation | LGPL |

### Build Tools
| Tool | Version | Purpose |
|------|---------|---------|
| **PyInstaller** | 6.16.0+ | Executable creation |
| **Python** | 3.11+ | Runtime (3.14 recommended) |

For complete dependency information, see [**DEPENDENCIES.md**](DEPENDENCIES.md).  
For third-party licenses, see [**THIRD_PARTY_LICENSES.md**](THIRD_PARTY_LICENSES.md).

---

## 📊 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **3.4** | Oct 19, 2025 | Keyboard shortcuts, Enter navigation, Escape key support |
| **3.3** | Oct 19, 2025 | Enhanced import validation, real-time input validation |
| **3.2** | Oct 19, 2025 | Inline Quick Add, expense list enhancement |
| **3.1** | Oct 18, 2025 | UX enhancements, animation optimization |
| **3.0** | Oct 17, 2025 | Stable release, slide-out animations |
| **2.9** | Oct 15, 2025 | UI/UX polish, optimized builds |
| **2.8** | Oct 14, 2025 | Library optimization, size reduction |

For complete version history, see [**CHANGELOG.md**](CHANGELOG.md).

---

## 🎯 Design Philosophy

LiteFinPad follows these core principles:

1. **Offline First**: Your data stays on your machine. No cloud, no tracking, no accounts.
2. **Lightweight & Fast**: Small footprint (~23 MB), instant startup, minimal resources.
3. **User-Centric Design**: Built for rapid data entry with keyboard shortcuts and smart defaults.
4. **Zero Dependencies**: Single executable, no Python installation required for end users.
5. **Transparent & Open**: Full source code available, clear documentation, open license.

---

## 🤝 Contributing

LiteFinPad is currently a personal project, but contributions are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Setup
```bash
# Clone and install
git clone https://github.com/yourusername/LiteFinPad.git
cd LiteFinPad
python -m pip install -r requirements.txt

# Run in development mode
python main.py

# Build for testing
build_dev.bat
```

---

## 📄 License

LiteFinPad is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

**In short**: Free to use, modify, and distribute. No warranties provided.

### Third-Party Licenses
This project uses open-source libraries with permissive licenses. All attributions and license texts are available in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## 🙏 Acknowledgments

Built with the help of:
- **Mark Hammond** - pywin32 library for Windows integration
- **John McNamara** - xlsxwriter for Excel export
- **Olivier Plathey** - fpdf library for PDF generation
- **Python Software Foundation** - Python language and standard library
- **Claude (Anthropic)** - AI-assisted development and documentation

---

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: See `/docs` folder for detailed guides
- **Build Help**: [BUILD_SYSTEM_GUIDE.md](BUILD_SYSTEM_GUIDE.md)

---

## 🔮 Future Plans

Potential features under consideration (not committed):
- 📊 Category-based expense tracking
- 📈 Visual charts and graphs
- 🔄 Import from CSV/Excel
- 🌙 Dark mode theme
- 🌍 Multi-language support

**Note**: LiteFinPad prioritizes simplicity and stability. Features are added conservatively.

---

<div align="center">

**Made with ❤️ for personal finance tracking**

⭐ Star this repo if you find it useful!

</div>
