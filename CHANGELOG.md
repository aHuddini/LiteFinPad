# LiteFinPad Changelog

## 🚀 Version 3.6 - Budget Threshold & Visual Refinements - October 27 - November 2, 2025

### **Summary**
v3.6 introduces the **Budget Threshold feature** with a clickable dialog for setting monthly spending limits, **Description Suggestions** dropdown to assist with expense entry, and visual color refinements to improve the dashboard's readability. The version also includes critical bug fixes for Tkinter validation issues, code quality improvements through date utilities consolidation, and defensive code cleanup to reduce unnecessary checks.

**Development Status:**
- ✅ Feature Complete (November 2, 2025)
- 📦 Built on stable v3.5.3 foundation
- 🎯 Budget threshold tracking now available
- 📝 Description suggestions feature added
- 🧹 Code quality improvements completed

---

### ✨ **New Features**

#### **Description Suggestions** 📝 NEW
- **Added**: Description suggestion dropdown for expense descriptions
  - Tracks description usage history in `description_history.json`
  - Loads filtered suggestions based on partial text input (minimum 2 characters)
  - Shows up to 5 suggestions sorted by usage frequency and recency
  - Displays last used amount as hint (e.g., "Groceries  $78.00")
  - Available in Quick Add dialog and Add Expense dialog
  - **Manual activation**: Press Down arrow or click dropdown button to view suggestions
  - **Note**: Dropdown does not auto-open due to Tkinter framework limitations (programmatic opening blocks user input)
- **Settings**: Configurable via `settings.ini` [AutoComplete] section
  - `show_on_focus`: Load top suggestions when field receives focus (default: true)
  - `min_chars`: Minimum characters before filtering suggestions (default: 2)
  - `max_suggestions`: Maximum suggestions to display (default: 5)
  - `max_descriptions`: Maximum descriptions to track (default: 50)

#### **Budget Threshold Tracking** 💰 NEW
- **Added**: "vs. Budget" label in Spending Analysis section
  - Displays between "Weekly Pace" and "Previous Month"
  - Shows difference from monthly budget with color coding:
    - 🟢 Green: Under budget
    - 🔴 Red: Over budget
    - ⚪ Gray: Budget not set
  - Status displayed below amount (e.g., "(Under)" or "(Over)")
  - Reads from `settings.ini` [Budget] section

#### **Budget Dialog** 🎯 NEW
- **Added**: Clickable budget labels open dialog to set monthly threshold
  - Click on "vs. Budget" label to open dialog
  - Displays current budget threshold (or "Not Set")
  - Blank entry field with integrated numpad
  - Input validation (amount format, max 10 characters)
  - Saves to `settings.ini` persistently
  - Updates dashboard immediately after saving
  - Follows `ExpenseAddDialog` pattern for consistency

---

### 🎨 **Visual Refinements**

#### **Color Scheme Improvements**
- **Enhanced**: Dashboard label colors for better readability
  - "Weekly Pace": Darker orange (`#E67E22`)
  - "vs. Budget": Dark navy blue (`#1A3A52`)
  - "Previous Month" indicator (↑): Red for increases (`#E74C3C`)
  - "Previous Month" label: Vibrant purple (`#9B59B6`)
  - "Day" / "Week" labels: Darker navy (`#2C5F8D`)
  - "Daily Average": Dark teal (`#16A085`)
  - "Weekly Average": Dark amber (`#D68910`)

#### **Layout Adjustments**
- **Refined**: Spacing in Current Progress section
  - Day/Week labels grouped and centered
  - Daily/Weekly averages grouped and centered
  - Consistent 25px spacing between label groups
- **Refined**: Spending Analysis section
  - 5px spacing between Weekly Pace, vs. Budget, and Previous Month
  - Budget status displayed below amount for compact layout

---

### 🐛 **Critical Bug Fixes**

#### **Tkinter Validation Event Loop Deadlock** 🔧 FIXED
- **Fixed**: Application freeze when using pre-filled Entry widgets with validation
  - **Root Cause**: Pre-filled Entry widgets (`StringVar(value="3000.00")`) created validation state conflict
  - **Symptom**: Clicking "OK" in budget dialog froze entire application (no error logs)
  - **Solution**: Blank entry field + separate display label pattern
    - Entry starts blank (`StringVar(value="")`) - no validation conflicts
    - Current budget displayed as read-only label above entry
    - Numpad works correctly with blank entry (append-only logic)
  - **Impact**: Budget dialog now works reliably without freezing
  - **Documented**: Added to `AI_REFERENCE_TECH.md` as critical Tkinter gotcha

#### **Settings Manager Threading Fix** 🔧 FIXED
- **Fixed**: Lock-within-lock deadlock in `settings_manager.py`
  - `set()` method was calling `save()` while already holding lock
  - Created internal `_save_unlocked()` method to prevent deadlock
  - Auto-save now uses unlocked version when lock is already held

#### **Week Progress Display Fix** 🔧 FIXED
- **Fixed**: Week value displaying beyond calculated total (e.g., "5.2/5" in 5-week month)
  - Modified `calculate_week_progress()` to cap `precise_week` at `total_weeks`
  - Ensures display is logically capped until next month

#### **Budget Display Update Fix** 🔧 FIXED (November 3, 2025)
- **Fixed**: "vs. Budget" metric not updating after setting/changing budget
  - **Symptom**: Budget could be saved but "vs. Budget" display would not refresh until application restart
  - **Root Causes**:
    1. Budget label widgets were not extracted as instance attributes, so update method couldn't access them
    2. Used `text_color` attribute (CTkLabel) instead of `foreground` (ttk.Label)
    3. Used `monthly_total` (all expenses) instead of `monthly_total_past` (past expenses only)
  - **Solution**: 
    - Added widget extraction for `budget_amount_label` and `budget_status_label`
    - Fixed widget attribute to use `foreground` for ttk.Label
    - Updated calculation to use `ExpenseDataManager.calculate_monthly_total()` for consistency
    - Display now updates immediately after budget changes
  - **Impact**: Budget feature now fully functional with real-time display updates

#### **Archive Mode Bug Fixes** 🔧 FIXED (November 8, 2025)
- **Fixed**: Multiple critical issues preventing archive mode from working correctly
  - **Problems Fixed**:
    1. Archive mode colors not updating when switching months
    2. Display values (total, count, progress, analytics) not updating in archive mode
    3. "+Add Expense" button not disabling in archive mode
    4. CustomTkinter widget compatibility errors (using `style` parameter incorrectly)
    5. Tooltip duplication and persistence issues
  - **Root Causes**:
    1. Widget type detection wasn't properly identifying CustomTkinter vs ttk widgets
    2. `main_container` frame wasn't being updated for archive mode
    3. Using `.config()` instead of `.configure()` for CustomTkinter buttons
    4. Tooltip event handlers accumulating without proper cleanup
    5. `update_display()` using incorrect expense filtering for archive mode
  - **Solutions Applied**:
    - Added `main_container` parameter to ArchiveModeManager for complete frame updates
    - Improved widget detection using `isinstance()` and `hasattr('fg_color')` checks
    - Fixed CustomTkinter button state management (use `.configure()` not `.config()`)
    - Fixed `update_display()` to show ALL expenses in archive mode (no date filtering)
    - Fixed tooltip_manager to unbind old handlers before binding new ones
    - Added proper tooltip cleanup in archive mode transitions
    - Fixed expense filtering for analytics calculations in archive mode
  - **Files Modified**: `archive_mode_manager.py`, `gui.py`, `quick_add_helper.py`, `tooltip_manager.py`
  - **Impact**: Archive mode now fully functional with correct colors, values, button states, and tooltips

---

### ✨ **New Features**

#### **Quick Add Autocomplete** ✨ NEW (November 9, 2025)
- **Added**: Autocomplete/dropdown menu to description field in inline Quick Add expense form
  - Now matches functionality of other add expense dialogs (Add Expense Dialog, Quick Add from Tray)
  - Shows recurring expense patterns and suggestions as users type
  - Consistent user experience across all expense entry methods
  - Faster expense entry with intelligent suggestions
  - Better discoverability of expense patterns
  - **Files Modified**: `quick_add_helper.py`, `expense_list_page_builder.py`
  - **Impact**: Improved user experience, faster expense entry workflow, better utilization of recurring expense feature

---

### 🔧 **Code Quality Improvements**

#### **Analytics Method Consolidation** 🔧 NEW (November 8, 2025)
- **Improved**: Eliminated duplicate expense filtering logic across analytics methods
  - **Problem**: Same filtering patterns repeated in 5 different methods (`calculate_daily_average`, `calculate_weekly_average`, `calculate_weekly_pace`, `calculate_median_expense`, `calculate_largest_expense`)
  - **Solution**: Created 4 reusable helper methods to centralize filtering logic:
    - `_filter_expenses_by_date_range()` - Generic date range filtering
    - `_filter_expenses_by_month()` - Month-specific filtering
    - `_filter_expenses_by_week()` - Week-specific filtering
    - `_filter_past_expenses()` - Simple past-only filtering
  - **Benefits**:
    - Single source of truth for filtering logic
    - Easier maintenance (fix bugs once instead of multiple places)
    - Better code organization and consistency
    - No breaking changes (all public APIs unchanged)
  - **Files Modified**: `analytics.py` - Added helper methods, refactored 5 calculation methods
  - **Impact**: Improved code maintainability, foundation for future analytics enhancements

#### **Data Loading Exception Handling** 🔧 NEW (November 9, 2025)
- **Improved**: Narrowed exception handling in data loading/saving operations for better error diagnostics
  - **Problem**: Broad `Exception` catches in `ExpenseDataManager.load_expenses()` and `save_expenses()` made it difficult to diagnose specific issues (JSON errors vs permission errors vs system errors)
  - **Solution**: Replaced broad exception handling with specific exception types:
    - `load_expenses()`: Now catches `FileNotFoundError`, `json.JSONDecodeError`, `PermissionError`, `OSError` specifically before fallback
    - `save_expenses()`: Now catches `PermissionError`, `OSError` specifically before fallback
  - **Benefits**:
    - More specific error messages for users (e.g., "Invalid JSON format" vs "Permission denied")
    - Better error diagnostics in logs (specific exception types logged)
    - Easier debugging (identify root cause faster)
    - Consistent with exception handling refactoring patterns
  - **Files Modified**: `data_manager.py` - Narrowed exception handling in 2 methods
  - **Impact**: Improved error reporting and debugging capabilities

#### **Exception Handling Refactoring** 🔧 NEW (November 8, 2025)
- **Phase 1: Documentation** - Added comprehensive comments explaining framework workarounds
  - Documented Windows OS requirements for window procedures (must catch all exceptions)
  - Explained Tkinter limitations requiring defensive programming
  - Clarified PyInstaller detection as standard pattern (not workaround)
  - Added comments to 11 locations across `tray_icon.py`, `main.py`, and `window_manager.py`
  - **Impact**: Future developers understand why broad exceptions are necessary

- **Phase 2: Narrowing Exceptions** - Improved error detection with specific exception handling
  - Icon loading: Catches `WindowsError`/`OSError`/`AttributeError` specifically, then fallback
  - Window creation: Catches Win32 errors specifically, then fallback
  - Dialog cleanup: Catches `tk.TclError`/`AttributeError` specifically, then fallback
  - GUI queue shutdown: Catches `tk.TclError`/`AttributeError`/`RuntimeError` specifically, then fallback
  - Window operations: Catches Tkinter errors specifically, then fallback
  - **Impact**: Better error categorization (DEBUG for expected, ERROR/WARNING for unexpected)
  - **Files Updated**: `tray_icon.py` (2 locations), `main.py` (2 locations), `window_manager.py` (4 locations)

- **Phase 3: Win32 Decorator Pattern** - Reduced code duplication in Win32 API error handling
  - Created `@win32_safe` decorator for reusable Win32 exception handling
  - Applied to 5 methods: `create_window()`, `add_to_tray()`, `update_tooltip()`, `remove_from_tray()`, `show_context_menu()`
  - Catches Win32-specific exceptions (`WindowsError`, `OSError`, `AttributeError`) with configurable defaults
  - Reduced ~20 lines of duplicate exception handling code
  - **Impact**: DRY principle applied, improved maintainability, functionality preserved
  - **Files Updated**: `tray_icon.py`

- **Testing**: ✅ All phases tested and verified working correctly
- **Documentation**: Created `CODEBASE_STYLE_PROFILE.md`, `REFACTORING_PLAN.md`, and `REFACTORING_COMPLETE_SUMMARY.md`

#### **Defensive Checks Analysis & Removal** 📊 NEW (November 2, 2025)
- **Analyzed**: 28 `hasattr()` checks across 9 files
  - ✅ 22 NECESSARY (79%) - Legitimate runtime checks (tooltip management, PyInstaller detection, platform-specific handling, initialization safety)
  - ⚠️ 3 REMOVABLE (10%) - Obvious defensive code (remaining in `gui.py`, low priority)
  - ✅ 4 REMOVED (14%) - Successfully cleaned up unnecessary checks
- **Removed**: 4 unnecessary defensive checks
  - `main.py` line 716: `status_manager` check in `export_expenses_dialog()`
  - `main.py` line 726: `status_manager` check in `import_expenses_dialog()`
  - `window_manager.py` line 170: `stay_on_top_var` check in `toggle_stay_on_top()`
  - `window_manager.py` line 178: `stay_on_top_var` check in `_apply_topmost_setting()`
- **Verified**: `archive_mode_manager` checks in `gui.py` are NECESSARY
  - Attempted removal caused `AttributeError` during startup
  - Methods called during early initialization before manager exists
  - Checks re-introduced for stability
- **Impact**: Cleaner code, zero functional changes, thoroughly tested
- **Documented**: See `docs/internal/DEFENSIVE_CHECKS_ANALYSIS.md` for complete analysis

#### **Settings Manager Module** ⚙️ NEW
- **Created**: `settings_manager.py` - Centralized settings management system
  - Thread-safe operations with lock protection
  - Atomic file writes (temp → verify → rename) prevent corruption
  - Type-safe getters with automatic conversion (str, int, float, bool)
  - Auto-creates missing sections and keys
  - Singleton pattern for global access
  - Comprehensive validation and error handling
- **Migrated**: 4 files to use Settings Manager
  - `expense_table.py` - Sort preferences
  - `export_data.py` - Export location
  - `error_logger.py` - Debug mode
  - `dashboard_page_builder.py` - Budget threshold (NEW)
- **Impact**:
  - Thread-safe concurrent access protection
  - No more corrupted settings files (atomic writes)
  - Consistent validation across all settings operations

#### **Date Utilities Consolidation** 📅
- **Created**: `date_utils.py` - Centralized date operations module
  - 19 utility methods for consistent date handling
  - Clean API with proper error handling
  - Single source of truth for date operations
- **Consolidated**: 23 instances of duplicate date parsing across 8 files
  - Eliminated ~40 lines of duplicate `try-except` blocks
  - Improved code readability and maintainability

---

### 📝 **Documentation Updates**

#### **Technical Documentation**
- **Updated**: `AI_REFERENCE_TECH.md`
  - Added "Tkinter Entry Validation with Pre-filled Text - Event Loop Deadlock" section
  - Documented pre-filled Entry widget gotcha with validation
  - Included evidence (logs), root cause analysis, and solution pattern
  - Critical reference for future Tkinter dialog development

#### **User Documentation**
- **Updated**: `BEGINNER_THOUGHTS.md`
  - Added Section 13: "The Budget Dialog Debugging Marathon: When AI Gets It Wrong"
  - Documented collaborative debugging process
  - Emphasized importance of user feedback in identifying issues
  - Lessons on questioning AI diagnoses when evidence doesn't match

---

### 🧪 **Testing**

#### **Budget Feature Testing**
- ✅ Budget dialog opens correctly with current threshold displayed
- ✅ Numpad works perfectly with blank entry field
- ✅ Budget saves successfully without freezing or crashing
- ✅ Budget display updates immediately after saving
- ✅ Color coding works correctly (green/red/gray)
- ✅ Clickable labels respond to mouse clicks
- ✅ Settings persist across application restarts

#### **Visual Testing**
- ✅ All color changes applied successfully
- ✅ Layout spacing adjustments working as expected
- ✅ Week progress capped correctly at total weeks
- ✅ Previous month indicator shows red for increases

---

### 📝 **Documentation Updates** (Agent 1 & Agent 5 - November 2, 2025)

#### **New Documentation Created**
- **DEFENSIVE_CHECKS_ANALYSIS.md** - Comprehensive analysis of 28 `hasattr()` checks
  - Categorization with detailed rationale
  - Phase 1 implementation and Phase 2 recommendations
- **WORKTREE_EXPLANATION.md** - Guide for multi-agent worktree management
  - Main project vs. worktree locations
  - Best practices for multi-agent collaboration
- **PROJECT_ANALYSIS_AND_OPPORTUNITIES.md** - Updated project analysis
  - Code quality assessment
  - Refactoring opportunities
  - Multi-agent collaboration strategy
- **MULTI_AGENT_WORK_SUMMARY.md** - Summary of multi-agent collaboration
  - Agent roles and contributions
  - Phase 1 & Phase 2 details
- **docs/developer/API_REFERENCE.md** - Comprehensive API documentation
- **docs/developer/QUICK_START.md** - Developer onboarding guide
- **docs/developer/ARCHITECTURE.md** - System architecture overview
- **docs/README.md** - Updated with improved navigation

---

### 📊 **Version 3.6 Statistics**

**Files Modified:**
- `gui.py` - Budget dialog implementation + 3 defensive checks removed
- `dashboard_page_builder.py` - Budget display and color refinements
- `config.py` - New color constants and dialog dimensions
- `main.py` - Description suggestions integration in Quick Add dialog
- `expense_table.py` - Description suggestions integration in Add Expense dialog
- `description_autocomplete.py` - NEW: Description history management module
- `widgets/autocomplete_entry.py` - NEW: Description suggestions combobox widget
- `settings.ini` - Auto-complete configuration section added
- `analytics.py` - Week progress cap fix
- `settings_manager.py` - Threading fix
- `settings.ini` - Budget section added

**New Files:**
- `date_utils.py` - Date utilities module
- `settings_manager.py` - Settings management module

**Lines of Code:**
- Budget dialog: ~140 lines (dialog + numpad + validation)
- Budget display: ~50 lines (labels + color coding + clickable)
- Color refinements: ~15 color constant updates

**Code Quality:**
- Eliminated ~40 lines of duplicate date parsing
- Eliminated ~51 lines of duplicate settings logic
- Removed 3 unnecessary defensive checks (Agent 1)
- Fixed 3 critical bugs (validation freeze, threading deadlock, week cap)

**Documentation:**
- 8 new documentation files created (~3,000+ lines)
- Comprehensive developer onboarding materials
- Multi-agent collaboration guides

---

## 🚀 Version 3.6 (Phase 1) - Date Utilities & Code Consolidation - October 27-29, 2025

### **Summary**
Phase 1 of v3.6 focused on **code quality improvements** through the consolidation of duplicate date handling logic into a centralized utilities module. This laid the foundation for the Budget Threshold feature while improving maintainability and consistency.

**Development Status:**
- ✅ Phase 1 Complete (October 27-29, 2025)
- 📦 Built on stable v3.5.3 foundation
- 🎯 Foundation for Budget Threshold feature

---

### ✨ **New Modules**

#### **Date Utilities Module** 📅 NEW
- **Created**: `date_utils.py` - Centralized date operations module
  - 19 utility methods for consistent date handling across the application
  - Clean API with proper error handling (returns `None` instead of exceptions)
  - Well-documented with docstrings and usage examples
  - **Methods Include**:
    - `parse_date()` - Parse YYYY-MM-DD strings to datetime objects
    - `format_date()` - Format datetime objects consistently
    - `get_month_folder_name()` - Generate data folder names
    - `get_previous_month()` / `get_next_month()` - Month navigation
    - `is_valid_date()` - Date validation
    - And 14 more date utility methods
  - **Benefits**:
    - Single source of truth for date operations
    - Consistent date handling across all 8 modules
    - Easier to update date formats in the future
    - Better error handling and debugging

---

### 🔧 **Code Quality Improvements**

#### **Settings Manager Module** ⚙️ NEW
- **Created**: `settings_manager.py` - Centralized settings management system
  - Thread-safe operations with lock protection
  - Atomic file writes (temp → verify → rename) prevent corruption
  - Type-safe getters with automatic conversion (str, int, float, bool)
  - Auto-creates missing sections and keys
  - Singleton pattern for global access
  - Comprehensive validation and error handling
- **Migrated**: 3 files to use Settings Manager
  - `expense_table.py` - Sort preferences (16 lines → 6 lines, -73%)
  - `export_data.py` - Export location (32 lines → 10 lines, -69%)
  - `error_logger.py` - Debug mode (16 lines → 3 lines, -81%)
- **Impact**:
  - Eliminated 51 lines of duplicate settings logic
  - Thread-safe concurrent access protection
  - No more corrupted settings files (atomic writes)
  - Consistent validation across all settings operations
- **Example**:
  ```python
  # Before: Manual configparser with try-except blocks
  try:
      config = configparser.ConfigParser()
      config.read('settings.ini')
      value = config.get('Section', 'key', fallback='default')
  except Exception:
      value = 'default'
  
  # After: Clean, type-safe utility
  settings = get_settings_manager()
  value = settings.get('Section', 'key', default='default', value_type=str)
  ```

#### **Date Utilities Consolidation** 📅 NEW
- **Consolidated**: 23 instances of duplicate date parsing across 8 files
  - `expense_table.py` - 5 instances replaced
  - `analytics.py` - 9 instances replaced  
  - `gui.py` - 3 instances replaced
  - `main.py` - 2 instances replaced
  - `dashboard_page_builder.py` - 2 instances replaced
  - `export_data.py` - 2 instances replaced
  - `import_data.py` - 2 instances replaced
  - `data_manager.py` - 1 instance replaced
- **Impact**:
  - Eliminated ~40 lines of duplicate `try-except` date parsing blocks
  - Improved code readability with clean utility calls
  - Reduced maintenance burden (update once, apply everywhere)
  - Consistent error handling across all date operations
- **Example**:
  ```python
  # Before: Scattered throughout codebase
  try:
      date_obj = datetime.strptime(date_str, "%Y-%m-%d")
  except ValueError:
      # handle error
  
  # After: Clean, consistent utility call
  date_obj = DateUtils.parse_date(date_str)
  if date_obj:
      # use date_obj
  ```

#### **Combined v3.6 Code Quality Metrics** 📊
- **New Modules Created**: 2 (`date_utils.py`, `settings_manager.py`)
- **Total Code Reduction**: ~91 lines of duplicate logic eliminated
- **Files Improved**: 11 files refactored
- **New Utility Methods**: 19 date utilities + 12 settings methods
- **Improved Safety**: Thread-safe settings, atomic writes, consistent validation

---

### 🐛 **Bug Fixes**
*None in this release - focus was on code quality*

---

## 🔧 Version 3.5.3 - Archive Mode, Build Optimizations & Privacy Fixes - October 21-27, 2025

### **Summary**
v3.5.3 brings **professional system tray improvements**, a **minimal status bar** for important action feedback, **streamlined export workflow**, **flexible date selection**, and **intelligent month-to-month spending comparisons**. The system tray icon now features a right-click context menu for quick access to common actions. A new status bar provides purposeful, non-intrusive feedback for critical operations. The export dialog has been enhanced with a default save location feature, eliminating repetitive file picker navigation. Date pickers now support cross-month selection (up to 2 months back), enabling retroactive expense entry and month-end transaction handling. The analytics dashboard now shows at-a-glance spending trend indicators comparing the current/viewed month against the previous month.

---

### ✨ **New Features**

#### **1. Month-to-Month Spending Comparison** 📊 NEW
- **Added**: Visual indicators showing spending trends compared to previous month
  - ▲ **Orange** indicator for increased spending with percentage
  - ▼ **Gray** indicator for decreased spending with percentage
  - ≈ **Light gray** indicator for similar spending (<5% change)
  - Displays inline with "Previous Month" analytics on dashboard
  - **Smart Contextual Awareness**:
    - Normal mode: Compares current month vs previous month
    - Archive mode: Compares viewed month vs its previous month (e.g., September vs August when viewing September)
    - Automatically hides when previous month has no data
  - **Benefits**:
    - Quick visual awareness of spending patterns at a glance
    - Helps identify month-over-month trends without manual calculation
    - Subtle design matches existing analytics styling
    - Color-coded for easy interpretation (orange for awareness, gray for neutral)
    - Works seamlessly with existing cross-month system and Archive Mode
- **Impact**: MEDIUM-HIGH - Provides valuable trend insight without disrupting existing workflow

#### **2. Enhanced Export Dialog with Default Save Location** 📁 NEW
- **Added**: One-click export workflow with persistent save location
  - Set a default export location (defaults to application folder)
  - All exports (Excel, PDF, JSON backups) go directly to saved location
  - No more repetitive folder navigation through file pickers
  - Smart path display shows drive and key folders (e.g., `C:\Users\...\Documents`)
  - "Change..." button to update location anytime
  - Location persists across sessions
  - **Benefits**:
    - Much faster export workflow - no more clicking through folders every time
    - Keeps all exports organized in one location
    - Perfect for portable installations - defaults to app folder
    - More professional and efficient user experience
- **Impact**: HIGH - Significantly streamlines the export process for daily use

#### **Status Bar for Important Actions** ℹ️
- **Added**: Minimal status bar at bottom of Expense List page
  - Shows success/error messages for important operations only
  - Auto-clears after 5 seconds to avoid clutter
  - **Messages Include**:
    - ✅ Expense deleted
    - ✅ Expense edited successfully
    - ✅ Exported to Excel/PDF/JSON
    - ✅ Import successful
    - ⚠️ Import failed (with error details)
  - **Design Philosophy**:
    - Only visible on Expense List page (hidden on main page)
    - Minimal, purposeful feedback for less-frequent, high-impact actions
    - Matches application color theme (subtle gray background)
- **Impact**: MEDIUM - Provides helpful confirmation without being intrusive

#### **3. System Tray Right-Click Context Menu** 🖱️
- **Added**: Professional context menu when right-clicking the system tray icon
  - **Open LiteFinPad** - Quickly show or hide the main window
  - **Quick Add Expense** - Open the Quick Add dialog instantly
  - **Quit** - Exit the application cleanly
  - **Benefits**:
  - More intuitive - Follows standard Windows application behavior
  - Convenient access - All common actions available from one menu
  - Professional feel - Polished user experience
- **Impact**: HIGH - Significant UX improvement for daily use

#### **2. System Tray Management Improvements** 🔧
- **Improved**: Tray icon organization and reliability
  - Better code organization for tray icon functionality
  - Enhanced tooltip updates when expenses change
  - More robust tray icon lifecycle management
  - **Benefits**:
  - More reliable tray icon behavior
  - Smoother monthly total updates in tooltip
  - Better system integration
- **Impact**: MEDIUM - Behind-the-scenes improvements for stability

#### **3. Expense Table Column Sorting** 📊 NEW
- **Added**: Clickable column headers for sorting expenses
  - Click "Date", "Amount", or "Description" to sort
  - Visual indicators (↑↓) show current sort direction
  - Sort preference remembers your choice across sessions
  - **Benefits**:
    - Quickly find your largest expenses
    - Organize by description alphabetically
    - More flexible data viewing
    - Professional table behavior
- **Impact**: MEDIUM - Helpful for analyzing expenses with many entries

#### **4. Expense Table Pagination** 📄 NEW
- **Added**: Smart pagination for expense tables with 16+ expenses
  - Navigate with arrow buttons: ◄◄ (first), ◄ (previous), ► (next), ►► (last)
  - Page indicator shows current position (e.g., "1/3")
  - Auto-hides when you have 15 or fewer expenses
  - Shows 15 expenses per page for optimal viewing
  - Works seamlessly with column sorting
  - **Benefits**:
    - View all your expenses without performance issues
    - Easy navigation for users with many monthly expenses
    - Clean interface - pagination only appears when needed
    - Professional table experience
- **Impact**: HIGH - Essential for users with many expenses

#### **5. Cross-Month Date Selection** 📅 NEW
- **Added**: Record expenses for previous months (up to 2 months back)
  - Date pickers now show current month + 2 previous months
  - Expenses automatically save to correct month's data folder
  - Visual month separators for easy navigation
  - Status bar notification when expense saved to previous/future month
  - **Benefits**:
    - Handle month-end credit card payments easily
    - Record forgotten expenses retroactively
    - More flexible expense tracking
    - Foundation for viewing historical month data
  - **Available In**:
    - Add Expense dialog
    - Edit Expense dialog
    - Quick Add section
- **Impact**: HIGH - Essential for real-world expense tracking flexibility

#### **6. Collapsible Date Picker Widget** 🗓️ NEW
- **Added**: Advanced date picker with collapsible month navigation
  - Shows all 12 months of the current year in a single dropdown
  - Accordion-style month sections (only one expanded at a time)
  - Click month separators (▶/▼) to expand/collapse months
  - **Mousewheel Navigation**: Scroll through all dates seamlessly across months
    - Hover over date field and scroll to navigate any date in the year
    - Automatically expands months as you scroll through them
    - Works across all 12 months without clicking
  - Full month names (e.g., "October" instead of "Oct") for clarity
  - Visual indicators: "(Current)" for current month, "(Today)" for today's date
  - Compact, professional design matching app aesthetics
  - **Benefits**:
    - Extremely fast date selection - scroll directly to any date
    - No more clicking through multiple dropdowns or calendars
    - Clear visual organization with month sections
    - Intuitive accordion behavior reduces clutter
    - Professional, modern date picker experience
  - **Technical**:
    - Reusable widget component (`widgets/collapsible_date_combo.py`)
    - Replaces ~70 lines of duplicate date logic in each dialog
    - Standard library only (no external dependencies)
- **Impact**: HIGH - Significantly improves date selection UX across the entire app

#### **7. Month Viewer System (Archive Mode)** 📚 NEW
- **Added**: View and explore historical month data with clear visual distinction
  - **Click Month Title**: Click the month label at the top of the main page to open navigation menu
  - **Year/Month Hierarchy**: Menu organizes months by year for easy navigation
  - **Smart Month Detection**: Only shows months with actual expense data
  - **Archive Mode Theme**: Lavender-tinted background (`#E0DDF0`) when viewing past months
  - **Window Title Indicator**: Shows "📚 Archive: [Month] [Year]" for clarity
  - **Read-Only Protection**: All expense entry methods disabled in archive mode
    - "+ Add Expense" button disabled (main page)
    - Quick Add section disabled (expense list page: button and input fields disabled)
    - Prevents accidental modifications to historical data
    - *Note*: Uses simple `state='disabled'` for TTK widgets (custom styling attempted but not feasible)
  - **Seamless Navigation**: Easily switch between months or return to current month
  - **Benefits**:
    - Review past spending patterns at a glance
    - Verify historical expense data for accuracy
    - Understand spending trends over time
    - Clear visual distinction between current and archived data
    - Safe exploration without risk of modifying past data
  - **Technical**:
    - Dedicated `month_viewer.py` module for clean separation of concerns
    - State management: `actual_month`, `viewed_month`, `viewing_mode`
    - Dynamic TTK styling with archive-specific style prefixes
- **Impact**: HIGH - Enables meaningful historical expense analysis and trend tracking

---

### ⚡ **Performance Improvements**

#### **1. Window Animation Responsiveness** 🚀 NEW
- **Improved**: Window show animation now appears significantly faster
  - Reduced startup delay before window appears (40x faster)
  - Eliminated 1-second delay before animation starts
  - Optimized screen position calculations with smart caching
  - Improved event processing speed (50ms → 20ms polling)
  - **Benefits**:
  - Window appears nearly instantly when clicking tray icon
  - Smoother, more responsive user experience
  - Application feels snappier and more polished
  - No visual glitches or quality compromises
- **Impact**: HIGH - Very noticeable improvement in daily use

---

### 🔧 **Code Quality Improvements**

#### **1. Configuration Consolidation** 🔧 NEW
- **Improved**: Centralized all hardcoded values into `config.py`
  - Organized timing delays, messages, file patterns into logical sections
  - Added new `Threading`, `Messages`, and `Files` configuration classes
  - Enhanced `Dialog` and `TreeView` classes with behavior constants
  - **Benefits**:
  - Easier to customize application behavior
  - Consistent messaging throughout the app
  - Simplified maintenance and future updates
  - Foundation for potential internationalization
- **Impact**: LOW for users, HIGH for maintainability and future customization

#### **2. Code Organization & Maintainability** 📊
- **Improved**: Internal code structure for better maintainability
  - Simplified analytics method calls for cleaner code architecture
  - Removed unnecessary code layers (37 lines)
  - Better organized tray icon management
  - Extracted window management into dedicated module for cleaner architecture
  - **Extracted Archive Mode Management** (October 26, 2025):
    - Moved all archive mode logic into dedicated `archive_mode_manager.py` module
    - Reduced main GUI code by 127 lines (11% reduction)
    - Improved archive mode feature organization and testability
    - Established clean pattern for future feature-specific managers
  - **Extracted Tooltip System** (October 26, 2025):
    - Moved all tooltip logic into dedicated `tooltip_manager.py` module
    - Reduced main GUI code by 42 lines (4% reduction)
    - Centralized tooltip styling and positioning for consistency
    - Fixed ghost tooltip bug when switching between archive/normal modes
    - Removed unnecessary tooltip from self-explanatory buttons
  - **Simplified About Dialog** (October 27, 2025):
    - Refactored `show_about_dialog()` from 124 lines to 57 lines (-54% reduction)
    - Introduced helper function pattern to eliminate repetitive code
    - Combined multiple labels into multi-line displays for cleaner structure
    - Same dialog appearance and functionality with much better maintainability
    - Reduced `gui.py` from 610 to 544 lines (60.4% total reduction from original)
  - **Consolidated Application Shutdown** (October 26, 2025):
    - Unified shutdown logic with proper cleanup sequence (dialogs → tray icon → window)
    - Added guard flag to prevent duplicate shutdown execution
    - Improved logging clarity (moved intermediate steps to DEBUG level)
    - Fixed race condition in GUI queue processor during shutdown
    - Single "Application shutdown complete" message for cleaner user experience
  - **Extracted Dashboard Builder** (October 26, 2025):
    - Moved all dashboard UI construction into dedicated `dashboard_page_builder.py` module
    - Reduced main GUI code by 251 lines (25% reduction from previous iteration)
    - Separated UI construction from update logic for clearer architecture
    - Easier to theme and redesign dashboard layout in the future
    - Improved code organization: construction vs. logic now cleanly separated
  - **Extracted Expense List Page Builder** (October 27, 2025):
    - Moved all expense list UI construction into dedicated `expense_list_page_builder.py` module
    - Reduced main GUI code by 113 lines (15% reduction from previous iteration)
    - Mirrors Dashboard Builder pattern for consistency
    - Entire expense list page now reusable for future features (V4.0 Power User Workspace)
    - Fixed Archive Mode Quick Add blocking bug during extraction
    - Total GUI code reduction: 764 lines (56% smaller from 1,374 to 610, significantly easier to maintain)
  - **Benefits**:
  - Faster future development and bug fixes
  - Easier to add new features
  - More reliable and stable codebase
  - Better separation of concerns for window lifecycle management
  - Archive mode features now easier to enhance and extend
- **Impact**: No visible changes - all features work exactly the same as v3.5.2

### 🛠️ **Build System Improvements** (October 27, 2025)

#### **1. Python Version Compatibility Fix** ⚠️ CRITICAL
- **Fixed**: Build system was mixing Python versions
  - `copy_libraries.bat` was copying xlsxwriter/fpdf from Python 3.11
  - PyInstaller was building with Python 3.14
  - Could cause compatibility issues or outdated library behavior
- **Solution**: Updated `copy_libraries.bat` to dynamically detect Python 3.14 site-packages
  - Queries Python directly: `py -3.14 -c "import sys; print(...)"`
  - Works on any developer's machine (portable)
  - No hardcoded personal paths
  - Includes error handling if Python 3.14 not found
- **Impact**: Ensures all library versions match the Python runtime, works for all developers

#### **2. Production Build Optimization** 🗜️
- **Removed**: Redundant Python source files from distribution
  - Deleted 61 unnecessary `.py` files (~1 MB saved)
  - Python only needs `.pyc` (compiled bytecode) to run - source files are for editing
  - Kept source files when no compiled version exists (e.g., tkinter)
- **Benefits**:
  - Smaller distribution (~24 MB vs ~25 MB)
  - Fewer files for users to see (335 vs 396 files)
  - More professional package
- **Impact**: Cleaner builds without changing functionality

#### **3. User Experience: Hidden Internal Folder** 👁️
- **Improved**: `_internal` folder now hidden from users (Windows hidden attribute)
  - Users see only: `.exe`, `settings.ini`, `version.txt`, data folders
  - Technical files (335 items) hidden from normal browsing
  - Still accessible if "Show hidden files" enabled
- **Benefits**:
  - Professional, clean folder appearance
  - Less overwhelming for non-technical users
  - Matches industry-standard application packaging
- **Impact**: Much cleaner user experience when browsing install folder


---

### ✅ **What's Been Tested**

All features thoroughly tested and verified:
- ✅ Export dialog displays default save location correctly
- ✅ All export formats (Excel, PDF, JSON) use saved location
- ✅ Change location feature updates and persists correctly
- ✅ Smart path truncation displays readable folder paths
- ✅ Column sorting works for Date, Amount, and Description
- ✅ Sort indicators (↑↓) display correctly
- ✅ Sort preferences persist across app restarts
- ✅ Pagination appears automatically with 16+ expenses
- ✅ Navigation buttons (◄◄ ◄ ► ►►) work correctly
- ✅ Page indicator displays correct current/total pages
- ✅ Pagination hides when 15 or fewer expenses
- ✅ Pagination works seamlessly with column sorting
- ✅ Collapsible date picker displays all 12 months correctly
- ✅ Month separators expand/collapse with accordion behavior
- ✅ Mousewheel scrolling navigates through all dates seamlessly
- ✅ Mousewheel auto-expands months as user scrolls
- ✅ Full month names display correctly (e.g., "October 2025")
- ✅ Visual indicators show for current month, today, and future dates
- ✅ Date picker works in all three locations (Quick Add, Add Dialog, Edit Dialog)
- ✅ Cross-month expenses save to correct month folders
- ✅ Status bar shows appropriate messages for past/future expenses
- ✅ Calculations.json created for all months with expense data
- ✅ System tray right-click menu works correctly
- ✅ Quick Add dialog opens from menu
- ✅ Application quit from menu functions properly
- ✅ Window show animation appears instantly (20-40ms startup)
- ✅ All widgets render correctly with no visual glitches
- ✅ Consistent performance across multiple shows/hides
- ✅ Dashboard displays all analytics correctly
- ✅ Expense tracking and calculations work identically to previous version
- ✅ No crashes or errors

---

## 🐛 Version 3.5.2 - Quick Add Dialog Stability Fix - October 19, 2025

### **Summary**
v3.5.2 fixes an **important stability issue** with the Quick Add dialog (double-click tray icon). This release ensures the Quick Add dialog opens reliably every time and includes the convenient auto-close feature when you click outside the dialog. All functionality works smoothly and consistently.

---

### 🐛 **Bug Fixes**

#### **1. Quick Add Dialog Reliability** ⚠️ IMPORTANT
- **Fixed**: Quick Add dialog now opens reliably from system tray
  - Previously could fail to open or behave unpredictably
  - Now opens instantly and consistently every time
  - Auto-close feature restored (dialog closes when clicking outside)
- **Benefits**:
  - Reliable and predictable behavior
  - Faster expense entry workflow
  - No more frustration with unresponsive dialog
- **Impact**: High - Critical feature now works perfectly

---

## 🔧 Version 3.5.1 - Dialog & Performance Improvements - October 20, 2025

### **Summary**
v3.5.1 brings **better dialog behavior** and **improved performance**. All dialogs now position themselves intelligently (never going off-screen), log files are much cleaner and faster, and added optional debug mode for troubleshooting. Minor visual improvements included.

---

### ✨ **New Features**

#### **1. Debug Mode** 🔍
- **Added**: Optional debug mode for troubleshooting
  - Edit `settings.ini` to enable detailed logging when needed
  - Normal mode keeps logs clean and fast (default)
  - Debug mode shows detailed information for support
  - **Benefits**:
  - Easier to troubleshoot issues
  - Faster application performance with normal mode
  - Simple toggle without code changes

---

### 🔧 **Improvements**

#### **1. Better Performance** ⚡
- **Improved**: Application runs faster with cleaner logs
  - Reduced unnecessary logging by 90%
  - Faster startup and operation
  - Smaller log files
  - **Benefits**:
  - Snappier feel throughout the application
  - Easier to review logs when troubleshooting

#### **2. Dialog Improvements** 🪟
- **Improved**: All dialogs now position themselves better
  - Dialogs appear in consistent, predictable locations
  - Never go off-screen on any monitor
  - Better sizing for all dialog content
  - Cleaner button labels
  - **Benefits**:
  - More polished appearance
  - Works better on different screen configurations

---

## 🏗️ Version 3.5 - Code Organization & Quality - October 19, 2025

### **Summary**
v3.5 is a **major code quality release** focused on internal improvements. Better organized code means faster future development and more reliable application. All existing features work exactly the same - this release is entirely about making the codebase cleaner and more maintainable.

---

### 🔧 **Code Quality Improvements**

#### **1. Internal Code Organization** 📦
- **Improved**: Better organized code structure
  - Better organized calculations, data handling, and validation
  - Cleaner code that's easier to maintain and update
  - Foundation for future features and improvements
- **Impact**: No visible changes - all features work exactly the same

#### **2. Context Menu Improvements** 🎯
- **Improved**: Expense table right-click menu is clearer
  - "Delete" option moved to bottom with red color
  - Better visual organization with separators
  - Harder to accidentally delete expenses
- **Impact**: Safer and more intuitive menu

###  🐛 **Bug Fixes**

#### **1. About Dialog Fix** ℹ️
- **Fixed**: About dialog now opens without errors
  - Previously could show an error when opening
  - Now works reliably every time

---

## ⌨️ Version 3.4 - Keyboard Navigation - October 19, 2025

### **Summary**
v3.4 adds **better keyboard support** for faster data entry. Press Enter to move between fields and submit expenses without reaching for the mouse. Great for power users entering multiple expenses quickly.

---

###  ✨ **New Features**

#### **1. Enter Key Navigation** ⌨️
- **Added**: Press Enter to move through expense fields
  - Amount → Description → Submit (works everywhere)
  - Same behavior in all dialogs (Quick Add, Add Expense, Inline Add)
  - Much faster data entry workflow
- **Benefits**:
  - Faster bulk expense entry
  - No mouse needed for adding expenses
  - Consistent behavior everywhere

#### **2. Escape Key Support** 🔑
- **Added**: Press Escape to close Export dialog
  - Quick exit without clicking Cancel
  - Standard keyboard shortcut behavior

###  🐛 **Bug Fixes**

#### **1. Quick Add Crash Fix**
- **Fixed**: Crash when pressing Enter too quickly
  - Previously could crash when pressing Enter in amount field
  - Now handles fast typing safely

---

## 🎯 Version 3.3 - Input Validation Improvements - October 19, 2025

### **Summary**
v3.3 makes **data entry smoother and more flexible**. Amount fields now block invalid characters as you type (no more accidentally typing letters!), and backup imports accept any amount (no artificial limits).

---

### ✨ **New Features**

#### **1. Real-Time Amount Validation** 💰
- **Added**: Amount fields only accept numbers as you type
  - Blocks letters and symbols automatically
  - Allows only valid currency format (e.g., 123.45)
  - Works everywhere (Quick Add, Add Expense, Inline Add)
- **Benefits**:
  - No more accidental typos in amounts
  - Cleaner, more intuitive typing experience
  - Fewer error messages

---

### 🔧 **Improvements**

#### **1. Flexible Import Limits**
- **Improved**: Removed $1M limit on imported expenses
  - Now accepts any positive amount
  - Useful for real estate, business equipment, etc.
  - Still blocks negative amounts


#### **2. Optional Descriptions**
- **Improved**: Descriptions now optional when importing backups
  - More flexible for different use cases
  - Prepares for future features

---

## 🎯 Version 3.2 - Inline Quick Add & JSON Backup - October 18, 2025

### **Summary**
v3.2 adds **Inline Quick Add** on the Expense List page for rapid bulk entry without dialogs, plus a complete **JSON Backup/Import system** for data portability. Also added total monthly amount display.

---

### ✨ **New Features**

#### **1. Inline Quick Add** ⚡
- **Added**: Quick expense entry directly on Expense List page
  - Add expenses without opening dialogs
  - Perfect for entering multiple expenses quickly
  - Auto-clears and refocuses after each entry
- **Benefits**:
  - Faster bulk expense entry
  - Less clicking and waiting
  - Ideal for reviewing receipts

#### **2. Total Amount Display** 💰
- **Added**: Monthly total now shown on Expense List page
  - Displayed between Typical and Largest expense
  - Shows total with expense count
  - Updates in real-time

#### **3. JSON Backup & Import** 💾
- **Added**: Complete backup and restore system
  - Export all your data to JSON file
  - Import backups to restore or migrate data
  - Backs up ALL months automatically
  - Secure with checksums and validation
- **Benefits**:
  - Safe backups of all your expense data
  - Easy migration between computers
  - Protection against data loss

---

### 🔧 **Improvements**

#### **1. UI Refinements**
- **Improved**: Cleaner expense table footer
  - Removed redundant total display (now in Insights section)
  - Better layout balance with new features

---

## 🎉 Version 3.1 - Quick Add Dialog - October 18, 2025

### **Summary**
v3.1 adds the **Quick Add dialog** - double-click the tray icon to add expenses instantly without opening the main window. Perfect for quick expense capture on the go. Also improved window animations for smoother performance.

---

### ✨ **New Features**

#### **1. Quick Add Dialog** ⚡
- **Added**: Double-click tray icon to add expenses
  - Add expenses without opening main window
  - Calculator-style number pad for easy entry
  - Auto-closes when you click away
  - Shows current month total
- **Benefits**:
  - Fastest way to capture expenses
  - Perfect for quick entries
  - No need to open full app

---

### 🔧 **Improvements**

#### **1. Smoother Animations** ✨
- **Improved**: Window slide-out animation
  - Buttery-smooth performance
  - Optimized for high-refresh displays
  - Faster and more responsive feel

---

## 🎉 Version 3.0 - Polish & Bug Fixes - October 18, 2025

### **Summary**
v3.0 adds **polish and fixes critical bugs**. The tray icon now shows your monthly total on hover, export filenames are cleaner, and version is visible in the window title. Most importantly, fixed a critical bug where deleted expenses weren't actually being saved.

---

### ✨ **New Features**

#### **1. Tray Icon Monthly Total** 💰
- **Added**: Hover over tray icon to see monthly total
  - Shows current month and total amount
  - Updates automatically when you add/edit/delete expenses
- **Benefits**:
  - Check your total without opening the app
  - Quick at-a-glance information

#### **2. Better Export Filenames** 📄
- **Improved**: Cleaner export file names
  - Now: `LF_October_2025_Expenses.xlsx`
  - Easier to organize and find files

#### **3. Version Display** 🏷️
- **Added**: Version shown in window title
  - Easy to see which version you're running

---

### 🐛 **Critical Bug Fixes**

#### **1. Expense Deletion Bug** 🔴
- **Fixed**: Deleted expenses now actually delete permanently
  - Previously, deleted expenses would reappear
  - Dashboard now updates correctly after deletion
  - Changes properly saved to disk

---

---

## 🎉 Version 2.9 - UI Polish & Build System - October 14, 2025

### **Summary**
v2.9 brings **UI refinements** and a **smarter build system**. Better button placement, improved dialog positioning, and automatic focus make the app feel more polished. Plus, the build system now prevents incomplete builds.

---

### ✨ **Improvements**

#### **1. UI Refinements** 🎨
- **Improved**: Better button placement and dialog behavior
  - "Add Expense" button moved to left (easier to access)
  - Dialog positions consistently in lower-right corner
  - Amount field auto-focuses when opening dialog
- **Benefits**:
  - Smoother, more intuitive workflow
  - Less clicking, faster entry

#### **2. Reliable Builds** 🔧
- **Improved**: Build system now validates everything
  - Detects and closes running app before building
  - Verifies all critical files are included
  - Prevents incomplete builds

---

## 🎉 Version 2.8 - Massive Size Optimization - October 14, 2025

### **Summary**
v2.8 achieved **50% size reduction** (46MB → 23MB) through TCL/TK optimizations and dependency cleanup - with zero functionality loss!

### ✨ **What Changed**
- **Optimized**: Removed unnecessary files and libraries
  - Removed unused image processing (Pillow)
  - Removed SSL libraries (offline app doesn't need them)
  - Removed timezone files and translations (English-only, Windows)
- **Result**: 50% smaller download, same features!

---

## 🎉 Version 2.7 - Faster Exports - October 13, 2025

### **Summary**
v2.7 switched to lighter, faster export libraries. Excel and PDF exports work exactly the same but the app is now smaller and faster.

### ✨ **What Changed**
- **Improved**: Faster Excel and PDF exports
  - Switched to lighter libraries
  - Smaller download size
  - Same great features

---

## 🎉 Version 2.6 - Export Features - October 13, 2025

### **Summary**
v2.6 completed the export system. Both Excel and PDF exports now work perfectly in the built application.

### ✨ **What Changed**
- **Fixed**: Excel and PDF export now work reliably
  - Professional formatting in both formats
  - Easy export button on Expense List page

---

# Early Development History (v1.0 - v2.5)

**Development Period**: October 12-13, 2025

Versions v1.0 through v2.5 were developed during rapid prototyping. These early versions established:
- Core expense tracking functionality
- System tray integration
- Monthly data organization
- Basic dashboard and expense list
- Initial export features

Formal changelog documentation began with v2.6, the first production-ready release.