# LiteFinPad v3.6

<div align="center">

<img src="LF_ReadMeTemporary.png" alt="LiteFinPad Logo" width="200">

**A lightweight, open-source, offline Windows expense tracker**

![Version](https://img.shields.io/badge/version-3.6-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

</div>

---

## Overview

**LiteFinPad** is a Windows application for tracking monthly personal expenses. It offers a clean, functional interface, system tray integration, simple financial analytics, and offline data management.

**Perfect for**:
- Personal finance tracking
- Monthly budget monitoring  
- Quick expense logging without opening apps
- Users who want complete data privacy (no cloud, no accounts)

---

## Screenshots

<div align="center">

<table>
<tr>
<td align="center">
<img src="ReadmeDemo1.png" alt="Dashboard View" width="400">
<br>
<em>Main dashboard with spending analytics and budget tracking</em>
</td>
<td align="center">
<img src="ReadmeDemo2.png" alt="Expense List View" width="400">
<br>
<em>Expense list with quick add functionality</em>
</td>
</tr>
</table>

</div>

---

## What's New in v3.6

### Budget Threshold Tracking (November 2025)

**New Feature:**
- Set a monthly spending budget threshold directly from the dashboard
- "vs. Budget" metric shows how much you're over or under budget
- Color-coded status indicators:
  - 🟢 Green: Under budget (shows amount remaining)
  - 🔴 Red: Over budget (shows amount exceeded)
  - ⚪ Gray: Budget not set (click to set)
- Click on budget labels to open dialog and set your monthly threshold
- Budget persists across sessions and updates in real-time

Quick Use-case: Am I "over" or "under" my current budget spending?
### Quick Add Autocomplete (November 2025)

**New Feature:**
- Added autocomplete suggestions to the description field in the inline Quick Add expense form
- Shows recurring expense patterns as you type
- Consistent experience across all expense entry methods
- Faster expense entry with intelligent suggestions

### Archive Mode Improvements (November 2025)

**Fixed Issues:**
- Archive mode now correctly displays colors and values when viewing past months
- All analytics and totals update properly in archive mode
- Add Expense button correctly disables when viewing archived data
- Improved tooltip behavior and display

### Code Quality Improvements (October - November 2025)

**Under the Hood:**
- Improved error handling and code organization
- Consolidated duplicate code for better maintainability
- Enhanced settings and date utility modules
- Better code documentation and structure

These improvements make the application more stable and easier to maintain, ensuring a better experience for users.

---

## Previous Releases

### v3.5.3 - Archive Mode & Export Features (October 2025)

**New Features:**
- **Archive Mode** - View historical expense data in read-only mode with visual distinction
- **System Tray Context Menu** - Right-click menu for quick access (Quick Add, Open, Quit)
- **One-Click Exports** - Export monthly expenses to Excel or PDF formats
- **Spending Trend Indicators** - Visual indicators showing spending changes month-to-month
- **Status Bar** - Feedback bar for important actions
- **Cross-Month Date Selection** - Expenses automatically route to the correct month folder

**User Experience Improvements:**
- Mousewheel date picker for easier date selection
- Expense table sorting by clicking column headers
- Pagination controls for large expense lists
- Improved data validation with real-time formatting

### v3.5.2 - Quick Add Dialog Fix (October 2025)

**Critical Fix:**
- Resolved threading issue with Quick Add dialog (double-click tray icon)
- Quick Add dialog now works reliably without crashes
- Restored auto-close behavior when clicking outside dialog

This fix ensures the fastest way to log expenses (Quick Add from tray) works consistently on all systems.

---

## Recent Updates (v3.5.1)

### Dialog System Improvements

**New Features:**
- Centralized dialog system for consistent behavior
- Optional debug mode for troubleshooting (via `settings.ini`)

**Performance Improvements:**
- Reduced logging overhead for better performance
- Improved dialog display and element visibility

### v3.5 - Major Update (October 2025)

**Improvements:**
- New modular architecture for better code organization
- Centralized configuration and settings
- Improved context menu organization
- Enhanced maintainability and stability

---

## Key Features

### Core Functionality
- **Quick Expense Entry**: Three ways to add expenses (inline, dialog, tray icon)
- **Real-time Analytics**: Monthly totals, weekly/daily averages, spending trends
- **Minimal Budget Tracking**: Set monthly spending threshold and monitor over/under status
- **Organized Data Storage**: Automatic monthly folders, JSON-based storage
- **Full Expense Management**: View, edit, delete, and search expenses
- **Export Options**: Excel (.xlsx) and PDF formats with professional styling

### User Experience
- **Modern Interface**: Clean, professional design with intuitive navigation
- **Keyboard Shortcuts**: Enter for navigation, Escape to close dialogs
- **System Tray Integration**: Always accessible, minimal screen footprint
- **Stay on Top Mode**: Keep tracker visible while working
- **Smart Dialogs**: Auto-focus, intelligent positioning, number pad support

### Technical Highlights
- **Fully Offline**: No internet required, no tracking, no cloud sync
- **Automatic Backups**: Monthly archives with zero data loss
- **Lightweight**: ~23 MB distribution, fast startup
- **Data Validation**: Real-time input validation prevents errors
- **Single Executable**: No Python installation required

---

## Quick Start

### Option 1: Download Pre-Built Executable (Recommended)

1. Go to the [Releases](https://github.com/aHuddini/LiteFinPad/releases) page
2. Download the latest release
3. Extract and run `LiteFinPad_v3.x.x.exe`
4. Look for the icon in your system tray

**No Python installation required. Just download and run.**

### Option 2: Run from Source

**Requirements**: Python 3.11+ (3.14 recommended), Windows 10+

```bash
# Clone the repository
git clone https://github.com/yourusername/LiteFinPad.git
cd LiteFinPad

# Install dependencies
python -m pip install -r requirements.txt

# Run the application
python main.py
```

---

## Usage

### First Launch
1. Application starts minimized in your system tray (bottom-right corner)
2. Click the system tray icon to open the main window
3. Start adding expenses

### Adding Expenses (3 Methods)

#### Method 1: Inline Quick Add (Fastest)
- Located at the bottom of the "Expense List" page
- Type amount → Press Enter → Type description → Press Enter
- Perfect for rapid consecutive entries

#### Method 2: Add Expense Dialog
- Click "+ Add Expense" button on Expense List page
- Includes optional number pad for touch screens
- Amount → Enter → Description → Enter to submit

#### Method 3: Quick Add from Tray (Stealthiest)
- Double-click the system tray icon
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
- **Export**: Click "Export" → Choose Excel or PDF

### Setting Your Monthly Budget
1. On the Dashboard, find the "vs. Budget" section in the Spending Analysis area
2. Click on the budget amount or status label (e.g., "Not set" or "(Click Here)")
3. Enter your monthly spending threshold using the number pad or keyboard
4. Click "Set" to save your budget
5. The dashboard will immediately update to show:
   - **Green amount**: How much you're under budget (e.g., "+$500.00")
   - **Red amount**: How much you're over budget (e.g., "-$200.00")
   - **Status**: "(Under)" or "(Over)" indicator
6. Your budget persists across sessions and updates automatically as you add expenses

---

## Project Structure

For developers, the project is organized into modular components:

- **Core modules**: `main.py`, `gui.py`, `expense_table.py`, `analytics.py`
- **System integration**: `tray_icon.py`, `window_animation.py`
- **Data management**: `export_data.py`, `import_data.py`, `data_manager.py`
- **Utilities**: `error_logger.py`, `validation.py`, `config.py`

Monthly expense data is stored in `data_YYYY-MM/` folders (auto-created).

For detailed technical documentation, see the `/docs` folder.

---

## Building from Source

```bash
# Development build
build_dev.bat

# Production release
build_release.bat
```

**Output**: `dist/LiteFinPad_vX.X/LiteFinPad_vX.X.exe`

For complete build instructions and options, see [BUILD_SYSTEM_GUIDE.md](docs/user/BUILD_SYSTEM_GUIDE.md).

---

## Dependencies

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

For complete dependency information, see [DEPENDENCIES.md](docs/developer/DEPENDENCIES.md).  
For third-party licenses, see [THIRD_PARTY_LICENSES.md](docs/developer/THIRD_PARTY_LICENSES.md).

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **3.6** | Nov 2025 | Archive mode improvements, code quality enhancements |
| **3.5** | Oct 2025 | Archive mode, export features, system tray improvements |
| **3.4** | Oct 2025 | Keyboard shortcuts, Enter navigation, Escape key support |
| **3.3** | Oct 2025 | Enhanced import validation, real-time input validation |
| **3.2** | Oct 2025 | Inline Quick Add, expense list enhancement |
| **3.1** | Oct 2025 | UX enhancements, animation optimization |
| **3.0** | Oct 2025 | Stable release, slide-out animations |

For complete version history, see [CHANGELOG.md](CHANGELOG.md).

---

## Design Philosophy

LiteFinPad follows these core principles:

1. **Offline First**: Your data stays on your machine. No cloud, no tracking, no accounts.
2. **Lightweight & Fast**: Small footprint (~23 MB), instant startup, minimal resources.
3. **User-Centric Design**: Built for rapid data entry with keyboard shortcuts and smart defaults.
4. **Zero Dependencies**: Single executable, no Python installation required for end users.
5. **Transparent & Open**: Full source code available, clear documentation, open license.

---

## Contributing

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

## License

LiteFinPad is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

**In short**: Free to use, modify, and distribute. No warranties provided.

### Third-Party Licenses
This project uses open-source libraries with permissive licenses. All attributions and license texts are available in [THIRD_PARTY_LICENSES.md](docs/developer/THIRD_PARTY_LICENSES.md).

## Acknowledgments

Built with the help of:
- **Mark Hammond** - pywin32 library for Windows integration
- **John McNamara** - xlsxwriter for Excel export
- **Olivier Plathey** - fpdf library for PDF generation
- **Python Software Foundation** - Python language and standard library

## Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: See `/docs` folder for detailed guides
- **Build Help**: [BUILD_SYSTEM_GUIDE.md](docs/user/BUILD_SYSTEM_GUIDE.md)

## Future Plans

Potential features under consideration (not committed):
- Category-based expense tracking
- Visual charts and graphs
- Import from CSV/Excel
- Dark mode theme
- Multi-language support
- Local AI parsing

**Note**: LiteFinPad prioritizes simplicity and stability. Features are added conservatively.

---

<div align="center">

**Made for personal finance tracking**

⭐ Star this repo if you find it useful!

</div>
