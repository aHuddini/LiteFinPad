# LiteFinPad Developer Quick Start

**Version:** 3.6  
**Last Updated:** November 2025  
**Purpose:** Get up and running with LiteFinPad development in 15 minutes

---

## 🚀 Quick Setup (5 minutes)

### Prerequisites

- **Python 3.11+** (Python 3.14 recommended)
- **Windows 10+** (currently Windows-only)
- **Git** for version control
- **Text editor** (VS Code recommended)

### 1. Clone & Install

```powershell
# Clone repository
git clone https://github.com/aHuddini/LiteFinPad.git
cd LiteFinPad

# Install dependencies (use python -m pip for correct Python version)
python -m pip install -r requirements.txt
```

**Dependencies installed:**
- `pywin32>=306` - Windows system tray
- `xlsxwriter>=3.1.0` - Excel export
- `fpdf==1.7.2` - PDF export
- `Pillow>=10.0.0` - Image handling
- `pyinstaller>=6.0.0` - Executable building

### 2. Run from Source

```powershell
python main.py
```

**Expected behavior:**
- Application starts minimized in system tray (bottom-right corner)
- Click 💰 icon to open main window
- No errors in console

### 3. Test Core Features

1. **Add Expense** - Click "+ Add Expense" button
2. **View Dashboard** - Check analytics display
3. **System Tray** - Double-click icon for Quick Add
4. **Export** - Test Excel/PDF export

**If everything works:** You're ready to develop! 🎉

---

## 📁 Project Structure (5 minutes)

### Core Application Files

```
LiteFinPad/
├── main.py                    # Application entry point & ExpenseTracker class
├── gui.py                     # Main GUI and layout (LiteFinPadGUI class)
├── config.py                  # All configuration constants (colors, fonts, dimensions)
└── version.txt                # Current version number
```

### Data Management

```
├── data_manager.py            # File I/O operations (load/save expenses)
├── expense_table.py           # Expense table UI and dialogs
├── analytics.py               # All analytics calculations
├── validation.py              # Input validation with structured results
└── date_utils.py              # Date parsing and utilities
```

### UI Components

```
├── gui.py                     # Main window
├── dashboard_page_builder.py  # Dashboard UI construction
├── expense_list_page_builder.py # Expense list UI construction
├── dialog_helpers.py          # Dialog creation utilities
├── status_bar_manager.py      # Status messages
├── tooltip_manager.py         # Tooltip system
└── widgets/                   # Reusable UI components
    ├── number_pad.py          # Calculator-style number pad
    └── collapsible_date_combo.py # Advanced date picker
```

### System Integration

```
├── tray_icon.py               # Low-level Windows tray icon (Win32 API)
├── tray_icon_manager.py       # High-level tray icon management
├── window_manager.py          # Window visibility and positioning
├── window_animation.py        # Slide-out animations
└── error_logger.py            # Logging system
```

### Data & Settings

```
├── settings_manager.py        # Thread-safe settings management
├── settings.ini               # User settings (created on first run)
├── month_viewer.py            # Archive mode navigation
├── archive_mode_manager.py    # Archive mode UI state
└── data_YYYY-MM/              # Monthly expense data (auto-created)
    ├── expenses.json          # Expense records
    └── calculations.json      # Cached analytics
```

### Build System

```
├── build_dev.bat              # Development builds (fast iteration)
├── build_release.bat          # Production builds (optimized)
├── copy_libraries.bat         # Copy export libraries
├── LiteFinPad_v3.6.spec       # PyInstaller configuration
└── version_manager.py         # Version management utilities
```

---

## 🔧 Development Workflow (5 minutes)

### Making Code Changes

#### 1. Edit Source Files

```powershell
# Open in your editor
code .

# Make changes to any .py file
# Example: Edit gui.py to change button text
```

#### 2. Test from Source

```powershell
# Kill any running instances
taskkill /F /IM python.exe 2>$null

# Clear Python cache (IMPORTANT!)
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force

# Run application
python main.py
```

**Why clear cache?** Python caches bytecode (.pyc files). Old cache can cause changes to not take effect.

#### 3. Build for Testing

```powershell
# Build development executable (fast, no optimization)
.\build_dev.bat

# Test the executable
cd dist\LiteFinPad_v3.6
.\LiteFinPad_v3.6.exe
```

**Development build:** ~8 seconds, includes debug symbols, larger size

### Common Development Tasks

#### Add a New Feature

1. **Plan** - Decide which module(s) to modify
2. **Implement** - Add code to appropriate file(s)
3. **Test** - Run from source, verify functionality
4. **Build** - Create executable, test again
5. **Document** - Update CHANGELOG.md, add docstrings

#### Fix a Bug

1. **Reproduce** - Confirm the bug exists
2. **Locate** - Find the problematic code
3. **Fix** - Make minimal changes
4. **Test** - Verify fix works, no regressions
5. **Document** - Note fix in CHANGELOG.md

#### Refactor Code

1. **Backup** - Create backup before major changes
2. **Refactor** - Make incremental changes
3. **Test** - After each change, verify nothing breaks
4. **Commit** - Save working state frequently

---

## 🎯 Key Concepts

### 1. Modular Architecture

LiteFinPad uses **separation of concerns**:

- **Data** - `data_manager.py` handles all file I/O
- **Logic** - `analytics.py` performs calculations
- **UI** - `gui.py` and builders handle display
- **Validation** - `validation.py` checks user input

**Example:** To add a new analytics metric:
1. Add calculation method to `analytics.py`
2. Call it from `dashboard_page_builder.py`
3. Update UI in `dashboard_page_builder.py`

### 2. Thread-Safe GUI Operations

**Critical Pattern:** System tray runs in background thread, GUI must run on main thread.

```python
# ❌ WRONG - Direct GUI call from tray thread (crashes!)
def on_tray_click():
    self.app.show_window()  # GIL violation!

# ✅ CORRECT - Queue-based pipeline (safe!)
def on_tray_click():
    self.gui_queue.put(self.app.show_window)  # Post to queue

# Main thread processes queue
def check_gui_queue():
    while not self.gui_queue.empty():
        callback = self.gui_queue.get()
        callback()  # Execute on main thread (GIL held)
```

**Rule:** Never call GUI methods from background threads directly.

### 3. Validation Pattern

Use `ValidationResult` for structured validation:

```python
from validation import InputValidation

# Validate user input
result = InputValidation.validate_final_amount(user_input)

# Boolean context (Pythonic!)
if result:
    save_expense(result.value)  # result.value is converted float
else:
    show_error(result.error_message)  # User-friendly message
```

### 4. Settings Management

Use `SettingsManager` singleton for all settings:

```python
from settings_manager import get_settings_manager

settings = get_settings_manager()

# Read setting with type conversion
debug_mode = settings.get("Logging", "debug_mode", default=False, value_type=bool)

# Write setting (auto-saves)
settings.set("Export", "default_path", "/path/to/exports")
```

**Thread-safe** and **atomic writes** prevent corruption.

### 5. Date Operations

Use `DateUtils` for all date operations:

```python
from date_utils import DateUtils

# Parse date string
date = DateUtils.parse_date("2025-10-19")
if date is None:
    # Handle invalid date
    return

# Get previous month
prev_month = DateUtils.get_previous_month("2025-10")  # "2025-09"
```

**Returns None** instead of raising exceptions for easier error handling.

---

## 🧪 Testing Your Changes

### Manual Testing Checklist

**Basic Functionality:**
- [ ] Application starts and tray icon appears
- [ ] Main window opens from tray icon
- [ ] Can add expense via Add Expense dialog
- [ ] Can add expense via Inline Quick Add
- [ ] Can add expense via tray Quick Add (double-click)
- [ ] Can edit existing expense
- [ ] Can delete existing expense
- [ ] Monthly total updates correctly

**Data Persistence:**
- [ ] Expenses save to JSON
- [ ] Data persists after restart
- [ ] Monthly folders created automatically

**Export Functionality:**
- [ ] Excel export generates valid .xlsx file
- [ ] PDF export generates valid .pdf file
- [ ] Exported data matches displayed data

**UI/UX:**
- [ ] Keyboard shortcuts work (Enter, Escape)
- [ ] Window positioning correct
- [ ] Dialogs close properly
- [ ] No visual glitches

### Debug Mode

Enable detailed logging for troubleshooting:

1. Edit `settings.ini`:
```ini
[Logging]
debug_mode = true
```

2. Run application - check `logs/app.log` for detailed output

3. Disable after debugging:
```ini
[Logging]
debug_mode = false
```

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found" error

**Cause:** Dependencies not installed or wrong Python version

**Solution:**
```powershell
# Verify Python version
python --version  # Should be 3.11+

# Reinstall dependencies
python -m pip install -r requirements.txt --force-reinstall
```

### Issue: Changes not taking effect

**Cause:** Python cache serving old bytecode

**Solution:**
```powershell
# Aggressive cache clearing
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force
```

### Issue: Application crashes on startup

**Cause:** Corrupted settings or data file

**Solution:**
```powershell
# Backup and reset settings
copy settings.ini settings.ini.backup
del settings.ini

# Run application (will create fresh settings.ini)
python main.py
```

### Issue: Tray icon doesn't appear

**Cause:** Windows tray icon issues or pywin32 not installed

**Solution:**
```powershell
# Reinstall pywin32
python -m pip install --upgrade --force-reinstall pywin32

# Run post-install script
python -m pywin32_postinstall -install
```

### Issue: Build fails with "file locked" error

**Cause:** Application running during build

**Solution:**
```powershell
# Kill all Python processes
taskkill /F /IM python.exe
taskkill /F /IM LiteFinPad_v3.6.exe

# Try build again
.\build_dev.bat
```

---

## 📚 Next Steps

### Learn the Codebase

1. **Read** `BEGINNER_THOUGHTS.md` - Development philosophy and learnings
2. **Review** `API_REFERENCE.md` - Comprehensive API documentation
3. **Study** `analytics.py` - Example of clean, well-documented code
4. **Explore** `validation.py` - Pythonic patterns and structured results

### Make Your First Contribution

**Easy First Tasks:**
1. Add a new color to `config.py` and use it in the UI
2. Add a new validation rule to `validation.py`
3. Create a new analytics metric in `analytics.py`
4. Add a tooltip to an existing button

**Medium Tasks:**
1. Create a new reusable widget in `widgets/`
2. Add a new export format (CSV)
3. Implement a new dialog with validation
4. Add keyboard shortcut for existing feature

**Advanced Tasks:**
1. Implement category system for expenses
2. Add search/filter functionality
3. Create data visualization charts
4. Implement undo/redo system

### Development Resources

**Documentation:**
- `docs/developer/API_REFERENCE.md` - API documentation
- `docs/developer/DEPENDENCIES.md` - Library information
- `docs/user/CONTRIBUTING.md` - Contribution guidelines
- `docs/user/BUILD_SYSTEM_GUIDE.md` - Build system details

**Code Examples:**
- `analytics.py` - Pure functions, static methods
- `validation.py` - Structured results, Pythonic patterns
- `settings_manager.py` - Thread-safe singleton, atomic writes
- `date_utils.py` - Utility class, error handling

**External Resources:**
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [pywin32 Documentation](https://mhammond.github.io/pywin32/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)

---

## 🎓 Development Philosophy

### Conservative Refactoring

**Approach:** Make ONE change at a time, test thoroughly, then proceed.

**Why:** Easier to identify what broke, safer for beginners.

**Example Workflow:**
1. Extract one function to utility module
2. Test application works
3. Commit/backup
4. Extract next function
5. Repeat

### AI-Assisted Development

**LiteFinPad was built with AI assistance (Cursor + Claude).**

**Best Practices:**
- AI implements, you review and test
- Question AI when something seems off
- Test incrementally, don't assume it works
- Document decisions and learnings

### Code Quality Over Features

**Priorities:**
1. **Working code** - Functionality first
2. **Clean code** - Readable and maintainable
3. **Optimized code** - Performance improvements
4. **New features** - Add after quality is high

---

## 💡 Pro Tips

### Faster Development Cycle

```powershell
# Create a dev script (dev.ps1)
taskkill /F /IM python.exe 2>$null
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
python main.py

# Run with: .\dev.ps1
```

### Quick Backup Before Major Changes

```powershell
# Create timestamped backup
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupDir = "backup_working_$timestamp"
robocopy . $backupDir /E /XD dist build __pycache__ logs data_* backup_* archive_*
```

### Use VS Code Debugging

1. Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: LiteFinPad",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal"
        }
    ]
}
```

2. Press F5 to debug with breakpoints

### Monitor File Changes

```powershell
# Watch for file changes (requires watchdog)
pip install watchdog
watchmedo shell-command --patterns="*.py" --recursive --command='echo File changed: ${watch_src_path}' .
```

---

## 🤝 Getting Help

### Documentation

- **API Reference** - `docs/developer/API_REFERENCE.md`
- **Build Guide** - `docs/user/BUILD_SYSTEM_GUIDE.md`
- **Contributing** - `docs/user/CONTRIBUTING.md`

### Community

- **GitHub Issues** - Report bugs or request features
- **GitHub Discussions** - Ask questions, share ideas

### Code Comments

Look for comments in the code explaining complex logic:
- `main.py` - Application lifecycle
- `tray_icon.py` - Win32 API interactions
- `validation.py` - Validation patterns

---

## ✅ Quick Start Complete!

You should now be able to:
- ✅ Run LiteFinPad from source
- ✅ Make code changes and test them
- ✅ Build development executables
- ✅ Understand the project structure
- ✅ Follow development best practices

**Next:** Pick a task from "Make Your First Contribution" and start coding!

---

**Last Updated:** November 2025  
**Maintainer:** AI-Assisted Development (Claude Sonnet 4.5)

