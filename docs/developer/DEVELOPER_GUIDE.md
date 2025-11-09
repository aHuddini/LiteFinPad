# LiteFinPad Developer Guide

**Version:** 3.6  
**Last Updated:** November 2025  
**Purpose:** Complete technical reference for LiteFinPad development

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Threading Model](#threading-model)
5. [API Reference](#api-reference)
6. [Design Patterns](#design-patterns)
7. [Development Guidelines](#development-guidelines)

---

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  System Tray Icon  │  Main Window  │  Dialogs  │  Widgets   │
│  (Background Thread) │  (Main Thread) │ (Main Thread) │      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LOGIC LAYER                   │
├─────────────────────────────────────────────────────────────┤
│  ExpenseTracker  │  Analytics  │  Validation  │  Settings   │
│  (Main Controller) │ (Calculations) │ (Input Check) │ (Config) │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  DataManager  │  SettingsManager  │  DateUtils  │  FileI/O  │
│  (JSON CRUD)   │  (INI Management)  │  (Date Ops)  │         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  data_YYYY-MM/  │  settings.ini  │  logs/  │  Temp Files   │
│  (Monthly Data)  │  (User Config)  │ (Debug) │  (Atomic)    │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**UI Layer:**
- Tkinter-based GUI components
- System tray integration (Win32 API)
- User input handling
- Visual feedback

**Logic Layer:**
- Business logic and workflows
- Data validation
- Analytics calculations
- State management

**Data Layer:**
- File I/O operations
- Data serialization/deserialization
- Settings persistence
- Date/time utilities

**Storage Layer:**
- JSON files (expense data)
- INI files (settings)
- Log files (debugging)

---

## 🏗️ Core Components

### 1. Application Entry Point

**File:** `main.py`  
**Class:** `ExpenseTracker`

Main application controller that:
- Initializes all components
- Manages application lifecycle
- Handles cross-month operations
- Coordinates GUI and tray icon

**Key Methods:**
- `__init__()` - Initialize application
- `load_data()` - Load expense data for current month
- `add_expense()` - Add new expense with cross-month routing
- `shutdown()` - Clean shutdown sequence

### 2. GUI Management

**File:** `gui.py`  
**Class:** `ExpenseTrackerGUI`

Manages the main application window:
- Two-page interface (Dashboard + Expense List)
- Budget tracking display
- Archive mode visual theming
- Widget lifecycle management

**Key Components:**
- `PageManager` - Handles page switching
- `StatusBarManager` - Shows operation feedback
- `TooltipManager` - Contextual help
- `ArchiveModeManager` - Historical data viewing

### 3. Data Management

**File:** `data_manager.py`  
**Class:** `ExpenseDataManager`

Handles all expense data persistence:
- Load/save expense data (JSON)
- Atomic file writes (temp → verify → rename)
- Automatic folder creation
- Data validation on load

**File:** `settings_manager.py`  
**Class:** `SettingsManager`

Manages application settings:
- Thread-safe INI file operations
- Type-safe getters (str, int, float, bool)
- Auto-creates missing sections/keys
- Singleton pattern for global access

### 4. Analytics Engine

**File:** `analytics.py`  
**Class:** `ExpenseAnalytics`

Calculates expense statistics:
- Monthly totals
- Daily/weekly averages
- Week/day progress tracking
- Month-over-month comparisons
- Largest/typical expense identification

### 5. System Tray Integration

**File:** `tray_icon.py`  
**Class:** `TrayIcon`

Windows system tray icon:
- Runs in background thread
- Win32 API message loop
- Context menu (Quick Add, Open, Quit)
- Tooltip with monthly total
- Thread-safe GUI queue communication

---

## 🔄 Data Flow

### Adding an Expense

```
User Input (GUI/Dialog)
    ↓
InputValidation.validate_expense()
    ↓
ExpenseTracker.add_expense()
    ↓
[Cross-month routing logic]
    ↓
ExpenseDataManager.save_expenses()
    ↓
ExpenseAnalytics.calculate_analytics()
    ↓
GUI.update_display()
    ↓
TrayIcon.update_tooltip()
```

### Loading Data

```
Application Start
    ↓
ExpenseTracker.__init__()
    ↓
ExpenseTracker.load_data()
    ↓
ExpenseDataManager.load_expenses()
    ↓
ExpenseAnalytics.calculate_analytics()
    ↓
GUI.show_main_page()
```

---

## 🧵 Threading Model

### Thread Architecture

**Main Thread (Tkinter):**
- GUI rendering
- User interactions
- Dialog management
- File I/O operations

**Background Thread (Tray Icon):**
- Win32 message loop
- System tray events
- Context menu handling

### Thread Communication

**GUI Queue Pattern:**
```python
# Tray icon (background thread) posts request
self.gui_queue.put(('show_quick_add', None))

# Main thread processes queue
def process_gui_queue(self):
    while not self.gui_queue.empty():
        action, data = self.gui_queue.get_nowait()
        if action == 'show_quick_add':
            self.show_quick_add_dialog()
```

**Why This Pattern:**
- Tkinter is not thread-safe
- Win32 message loop must run in separate thread
- Queue provides safe cross-thread communication
- Main thread processes queue every 100ms

---

## 📚 API Reference

### Data Management

#### ExpenseDataManager

**Module:** `data_manager.py`

##### `load_expenses(expenses_file, data_folder, current_month)`

Load expense data from JSON file.

**Parameters:**
- `expenses_file` (str): Path to expenses.json
- `data_folder` (str): Path to data folder
- `current_month` (str): Month string (YYYY-MM)

**Returns:**
- `tuple`: (expenses_list, monthly_total)

**Exception Handling:**
- Catches specific exceptions for better error diagnostics:
  - `FileNotFoundError`: File deleted between check and open
  - `json.JSONDecodeError`: Invalid JSON format
  - `PermissionError`: Permission denied reading file
  - `OSError`: Other OS-level errors (disk full, network issues)
  - `Exception`: Fallback for unexpected errors

**Example:**
```python
expenses, total = ExpenseDataManager.load_expenses(
    "data_2025-10/expenses.json",
    "data_2025-10",
    "2025-10"
)
```

##### `save_expenses(data_folder, expenses_file, expenses, monthly_total)`

Save expense data with atomic write.

**Parameters:**
- `data_folder` (str): Path to data folder
- `expenses_file` (str): Path to expenses.json
- `expenses` (List[Dict]): Expense list
- `monthly_total` (float): Total amount

**Returns:**
- `bool`: Success status

**Exception Handling:**
- Catches specific exceptions for better error diagnostics:
  - `PermissionError`: Permission denied writing file
  - `OSError`: OS-level errors (disk full, read-only filesystem, network issues)
  - `Exception`: Fallback for unexpected errors

---

### UI Components

#### QuickAddHelper

**Module:** `quick_add_helper.py`

Manages the inline Quick Add expense form on the Expense List page.

**Features:**
- Amount, description, and date input fields
- Autocomplete suggestions for description field (if `description_history` provided)
- Real-time validation
- Cross-month expense routing
- Archive mode enable/disable
- Enter key sequential navigation
- Status bar integration

##### `__init__(parent_widget, expense_tracker, description_history=None, ...)`

Initialize the Quick Add Helper.

**Parameters:**
- `parent_widget`: Parent frame to create UI in
- `expense_tracker`: ExpenseTracker instance for adding expenses
- `description_history`: Optional DescriptionHistory instance for autocomplete
- Additional optional parameters for callbacks and managers

**Note:** As of November 2025, the description field uses `AutoCompleteEntry` when `description_history` is provided, matching the behavior of other add expense dialogs.

##### `create_ui()`

Create and return the Quick Add UI frame.

**Returns:**
- `tk.Frame`: The Quick Add section frame

##### `add_expense()`

Validate and add expense from form. Handles validation, cross-month routing, status messages, and form clearing.

##### `set_enabled(enabled, tooltip_text=None)`

Enable or disable Quick Add fields (for archive mode).

**Parameters:**
- `enabled`: True to enable, False to disable
- `tooltip_text`: Optional tooltip text to display when disabled

**Note:** Handles both `AutoCompleteEntry` and plain `Entry` widgets correctly.

##### `clear_form()`

Clear all form fields and reset to defaults.

**Example:**
```python
from quick_add_helper import QuickAddHelper

quick_add = QuickAddHelper(
    parent_widget=expense_list_frame,
    expense_tracker=self.expense_tracker,
    description_history=self.description_history,  # Enables autocomplete
    on_add_callback=self.refresh_display,
    status_manager=self.status_manager
)

frame = quick_add.create_ui()
frame.grid(row=3, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
```

---

### Analytics

#### ExpenseAnalytics

**Module:** `analytics.py`

**Note:** As of November 2025, this class uses centralized helper methods for expense filtering to eliminate code duplication.

##### Helper Methods (Private - Internal Use)

**`_filter_expenses_by_date_range(expenses, start_date=None, end_date=None, current_date=None)`**
- Generic date range filtering for expenses
- Used internally by other filtering methods

**`_filter_expenses_by_month(expenses, month_date, exclude_future=True)`**
- Filter expenses for a specific month
- Used by `calculate_daily_average()` and `calculate_weekly_average()`

**`_filter_expenses_by_week(expenses, week_date, exclude_future=True)`**
- Filter expenses for a specific week (Monday to Sunday)
- Used by `calculate_weekly_pace()`

**`_filter_past_expenses(expenses, current_date=None)`**
- Filter out future expenses (keep only past and today)
- Used by `calculate_median_expense()` and `calculate_largest_expense()`

##### Public Methods

**`calculate_daily_average(expenses, current_date=None)`**
- Calculate average spending per day
- Uses `_filter_expenses_by_month()` helper

**`calculate_weekly_average(expenses, current_date=None)`**
- Calculate average spending per week
- Uses `_filter_expenses_by_month()` helper

**`calculate_weekly_pace(expenses, current_date=None)`**
- Calculate current week's spending pace
- Uses `_filter_expenses_by_week()` helper

**`calculate_median_expense(expenses, current_date=None)`**
- Calculate median expense amount
- Uses `_filter_past_expenses()` helper

**`calculate_largest_expense(expenses, current_date=None)`**
- Get the largest expense amount and description
- Uses `_filter_past_expenses()` helper

**Example:**
```python
# Calculate daily average
avg_per_day, days = ExpenseAnalytics.calculate_daily_average(expenses)

# Calculate median expense
median, count = ExpenseAnalytics.calculate_median_expense(expenses)

# Get largest expense
amount, description = ExpenseAnalytics.calculate_largest_expense(expenses)
```

---

### Validation

#### InputValidation

**Module:** `validation.py`

##### `validate_expense(amount, description, date_str=None)`

Validate expense input data.

**Parameters:**
- `amount` (str/float): Expense amount
- `description` (str): Expense description
- `date_str` (str, optional): Date in YYYY-MM-DD format

**Returns:**
- `ValidationResult`: Object with `is_valid`, `error_message`, `validated_data`

**Example:**
```python
result = InputValidation.validate_expense("50.00", "Groceries", "2025-10-19")
if result.is_valid:
    expense = result.validated_data
else:
    print(result.error_message)
```

---

### Settings Management

#### SettingsManager

**Module:** `settings_manager.py`

##### `get(section, key, default=None, value_type=str)`

Get setting value with type conversion.

**Parameters:**
- `section` (str): INI section name
- `key` (str): Setting key
- `default` (Any): Default value if not found
- `value_type` (type): Target type (str, int, float, bool)

**Returns:**
- Value converted to specified type

**Example:**
```python
from settings_manager import get_settings_manager

settings = get_settings_manager()
debug_mode = settings.get('Logging', 'debug_mode', default=False, value_type=bool)
```

##### `set(section, key, value)`

Set setting value with auto-save.

**Thread-safe:** Uses lock for concurrent access.

---

### Date Utilities

#### DateUtils

**Module:** `date_utils.py`

##### `parse_date(date_str)`

Parse YYYY-MM-DD string to datetime object.

**Parameters:**
- `date_str` (str): Date string

**Returns:**
- `datetime` or `None` if invalid

##### `get_month_folder_name(year, month)`

Generate data folder name.

**Returns:**
- `str`: "data_YYYY-MM"

**Example:**
```python
from date_utils import DateUtils

folder = DateUtils.get_month_folder_name(2025, 10)  # "data_2025-10"
```

---

## 🎨 Design Patterns

### 1. Singleton Pattern

**Used in:** `SettingsManager`

**Purpose:** Single global instance for settings access

```python
_settings_instance = None

def get_settings_manager():
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
```

### 2. Manager Pattern

**Used in:** UI component management

**Purpose:** Encapsulate related functionality

**Examples:**
- `StatusBarManager` - Status bar operations
- `TooltipManager` - Tooltip lifecycle
- `ArchiveModeManager` - Archive mode state
- `TrayIconManager` - Tray icon coordination

### 3. Builder Pattern

**Used in:** Page construction

**Purpose:** Separate UI construction from logic

**Examples:**
- `DashboardPageBuilder` - Dashboard UI
- `ExpenseListPageBuilder` - Expense list UI

### 4. Validation Result Pattern

**Used in:** `InputValidation`

**Purpose:** Structured validation responses

```python
class ValidationResult:
    def __init__(self, is_valid, error_message=None, validated_data=None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.validated_data = validated_data
```

### 5. Queue-Based Threading

**Used in:** Tray icon ↔ GUI communication

**Purpose:** Thread-safe cross-thread operations

---

## 🛠️ Development Guidelines

### Code Organization

**Module Structure:**
```
LiteFinPad/
├── main.py                 # Entry point
├── gui.py                  # Main GUI
├── config.py               # Constants
├── data_manager.py         # Data persistence
├── analytics.py            # Calculations
├── validation.py           # Input validation
├── settings_manager.py     # Settings
├── date_utils.py           # Date utilities
├── tray_icon.py            # System tray
└── widgets/                # Reusable components
    ├── collapsible_date_combo.py
    ├── autocomplete_entry.py
    └── number_pad.py
├── quick_add_helper.py     # Inline Quick Add expense form
```

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `ExpenseTracker`)
- **Functions:** `snake_case` (e.g., `load_expenses`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `BG_LIGHT_GRAY`)
- **Private methods:** `_leading_underscore` (e.g., `_is_archive_mode`)

### Error Handling

**Prefer specific exceptions:**
```python
# Good
try:
    data = json.load(f)
except (ValueError, KeyError) as e:
    log_error(f"JSON parse error: {e}")

# Avoid
try:
    data = json.load(f)
except Exception as e:  # Too broad
    log_error(f"Error: {e}")
```

**Exception Handling Best Practices (Updated November 2025):**

1. **Catch specific exceptions first, then fallback:**
```python
# Good - Specific exceptions first, then fallback
try:
    result = win32_api_call()
except (WindowsError, OSError) as e:
    log_error(f"Win32 API error: {e}", e)
    return False
except AttributeError as e:
    log_error(f"Module error: {e}", e)
    return False
except Exception as e:
    # Fallback for unexpected errors
    log_warning(f"Unexpected error: {e}")
    return False
```

2. **Framework workarounds require broad exceptions:**
```python
# Window procedures called by Windows OS must catch everything
def window_proc(hwnd, msg, wparam, lparam):
    try:
        # ... message handling ...
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    except Exception as e:
        # CRITICAL: Windows OS calls this directly - must catch all exceptions
        # to prevent application crash
        log_error(f"Window proc error: {e}")
        return 0
```

3. **Use decorators for repetitive Win32 error handling:**
```python
from tray_icon import win32_safe

@win32_safe(default_return=False, operation_name="add to tray")
def add_to_tray(self):
    # Win32 API calls here
    result = shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
    return result
```

4. **Log expected vs unexpected errors appropriately:**
```python
# Expected errors (shutdown, cleanup) - log at DEBUG
except (tk.TclError, AttributeError) as e:
    log_debug(f"Expected during shutdown: {e}")

# Unexpected errors - log at ERROR/WARNING
except Exception as e:
    log_error(f"Unexpected error: {e}", e)
```

5. **File I/O operations - catch specific errors:**
```python
# Good - Specific file operation exceptions
try:
    with open(expenses_file, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    log_warning(f"File not found: {expenses_file}")
    return [], 0.0
except json.JSONDecodeError as e:
    log_error(f"Invalid JSON in {expenses_file}: {e}", e)
    return [], 0.0
except PermissionError as e:
    log_error(f"Permission denied: {e}", e)
    return [], 0.0
except OSError as e:
    log_error(f"OS error: {e}", e)
    return [], 0.0
except Exception as e:
    # Fallback for unexpected errors
    log_error(f"Unexpected error: {e}", e)
    return [], 0.0
```

### Configuration

**All constants in `config.py`:**
```python
class Colors:
    BG_LIGHT_GRAY = '#e5e5e5'
    TEXT_DARK = '#2c3e50'

class Window:
    WIDTH = 700
    HEIGHT = 800
```

### Testing Workflow

1. **Run from source:** `python main.py`
2. **Test feature:** Verify functionality
3. **Check logs:** Review `logs/error_log_YYYY-MM-DD.log`
4. **Build dev:** `build_dev.bat` for quick testing
5. **Build release:** `build_release.bat` for distribution

### Common Pitfalls

**1. Tkinter Thread Safety**
- ❌ Never call Tkinter methods from background thread
- ✅ Use GUI queue for cross-thread operations

**2. File Operations**
- ❌ Direct writes (can corrupt on crash)
- ✅ Atomic writes (temp → verify → rename)

**3. Date Handling**
- ❌ Manual string parsing
- ✅ Use `DateUtils` methods

**4. Settings Access**
- ❌ Direct `configparser` usage
- ✅ Use `SettingsManager` singleton

**5. CustomTkinter Widget Compatibility (Updated November 2025)**
- ❌ Using `style` parameter on CustomTkinter widgets (they don't support it)
- ❌ Using `.config()` method on CustomTkinter widgets
- ✅ Use `fg_color` for background colors on CustomTkinter widgets
- ✅ Use `.configure()` method (not `.config()`) for CustomTkinter widgets
- ✅ Detect widget type using `isinstance(widget, ctk.CTkWidget)` or `hasattr(widget, 'fg_color')`
- ✅ Always unbind old tooltip event handlers before binding new ones

**Example:**
```python
# Correct CustomTkinter widget handling
if isinstance(widget, ctk.CTkFrame) or hasattr(widget, 'fg_color'):
    widget.configure(fg_color=config.Colors.BG_ARCHIVE_TINT)  # Use fg_color
    widget.configure(state='disabled')  # Use configure(), not config()
else:
    widget.configure(style='Archive.TFrame')  # ttk widgets use style
    widget.config(state='disabled')  # ttk widgets can use config()
```

---

## 📖 Additional Resources

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 15 minutes
- **[Dependencies](DEPENDENCIES.md)** - Library details and licenses
- **[Build System Guide](../user/BUILD_SYSTEM_GUIDE.md)** - Complete build instructions
- **[Contributing Guide](../user/CONTRIBUTING.md)** - Contribution guidelines

---

**Last Updated:** November 2025  
**Maintainer:** AI-Assisted Development (Claude Sonnet 4.5)

