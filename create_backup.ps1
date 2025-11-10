# ============================================================
# BACKUP CONFIGURATION - Update these values for each backup
# ============================================================
$backupVersion = "v3.6.1"
$backupDescription = "build_scripts_license_files_and_indentation_fixes"  # Update this for each backup
# ============================================================

$timestamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$backupDir = "backup_$backupVersion" + "_" + "$backupDescription" + "_" + "$timestamp"
Write-Host ('Creating backup: ' + $backupDir)
New-Item -ItemType Directory -Path $backupDir | Out-Null

Get-ChildItem -Path . | Where-Object { 
    $_.Name -notlike 'backup_*' -and 
    $_.Name -ne 'build' -and 
    $_.Name -ne 'dist' -and 
    $_.Name -ne 'logs' -and 
    $_.Name -notlike '*.zip' -and 
    $_.Name -ne '__pycache__' -and
    $_.Name -ne 'create_backup.ps1' -and
    $_.Name -ne 'archive_backups'
} | Copy-Item -Destination $backupDir -Recurse -Force

# Create a BACKUP_INFO.md file
$backupDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$info = @'
# Backup Information

**Created:** BACKUP_DATE_PLACEHOLDER
**Version:** BACKUP_VERSION_PLACEHOLDER

## What Changed

### Build System Improvements (November 2025)
- **License Files Integration**: All build scripts now require and copy license files
  - LICENSE file (MIT License) - required in all builds
  - THIRD_PARTY_LICENSES.txt - required in all builds (created from .md source)
  - README.txt - required in all builds (user guide with how-to sections)
  - Builds fail if license files are missing (no silent warnings)
- **ZIP Script Enhancement**: create_release_zip.ps1 now verifies license files
  - Checks for LICENSE, THIRD_PARTY_LICENSES.txt, and README.txt
  - Falls back to copying from project root if missing from build folder
  - Aborts ZIP creation if required files are missing
- **Version Manager Extension**: version_manager.py now auto-updates README.txt
  - Automatically updates version number in README.txt when version increments
  - Pattern matching finds "Version: X.Y.Z" and replaces it
  - No separate script needed - integrated into version management

### Code Quality Fixes
- **Indentation Errors Fixed**: Resolved all 74 linter errors
  - Fixed 39 indentation errors in archive_mode_manager.py
  - Fixed 35 indentation errors in gui.py
  - All try/except blocks now properly indented
  - All else blocks properly indented
  - Code now passes all linter checks (0 errors remaining)

### Version Update
- Updated project to v3.6.1
- Updated version.txt, README.md, CHANGELOG.md
- Updated build spec file for v3.6.1
- Updated version history in README

### Documentation Updates
- Added comprehensive Configuration section to README
- Documented all settings.ini options
- Updated CHANGELOG with v3.6.1 release notes

**Changes Made:**
- Increased dialog height from 480px to 600px to accommodate all content
- Reduced content frame padding from 30px to 20px/15px for better space utilization
- Separated version and description into individual labels for better control
- Consolidated features text into compact multi-line format to prevent text cropping
- Reduced spacing between elements (version, description, license, GitHub link, Close button)
- Made "View on GitHub" link more prominent with proper spacing
- Optimized all label padding values for better visual balance

**Files Modified:**
- `gui.py` - Complete About dialog layout redesign with improved spacing
- `config.py` - Dialog height adjustment (ABOUT_HEIGHT: 480 → 600)

**Testing:**
- ✅ All text is visible without cropping
- ✅ "View on GitHub" link is clearly visible and clickable
- ✅ Content is properly organized and spaced
- ✅ Dialog height accommodates all content

**Impact:**
- Improved user experience with better text visibility
- Professional appearance with proper alignment
- Better use of dialog space

### Pin Button Dark Mode Fix (November 9, 2025)

**BUG FIX: Pin Button Highlight Color Too Bright in Dark Mode**

**Problem:**
- When clicking the pin (stay on top) button to toggle it, the highlight/active color was too bright (`#D0D0D0` - light mode color)
- Did not match the dark mode theme appearance

**Root Cause:**
- `toggle_stay_on_top_visual()` method was using hardcoded `config.Colors.BG_BUTTON_DISABLED` (light mode color)
- Not using theme-aware colors from `theme_manager`

**Fix Applied:**
- Updated `toggle_stay_on_top_visual()` to use `self.theme_manager.get_colors().BG_BUTTON_DISABLED`
- Now uses theme-aware colors:
  - Light mode: `#D0D0D0` (bright gray)
  - Dark mode: `#3f3f46` (darker gray that matches dark mode theme)

**Files Modified:**
- `gui.py` - Updated `toggle_stay_on_top_visual()` to use theme-aware colors

**Testing:**
- ✅ Pin button highlight color matches dark mode theme
- ✅ Toggle works correctly in both light and dark modes
- ✅ Visual feedback is consistent with application theme

**Impact:**
- Better visual consistency in dark mode
- Professional appearance with proper color matching

### Dark Mode Dialog Improvements (November 9, 2025)

**UI CONSISTENCY: Fixed Background Colors and Button Styling in Dialogs**

**Changes Made:**
- **Quick Add System Tray Dialog**:
  - Fixed inconsistent background colors for amount frame, description frame, and button frame
  - Applied `QuickAdd.TFrame` style to all frames for consistent theme-aware backgrounds
  - Fixed numpad background color to match dialog frame (BG_SECONDARY in dark, BG_LIGHT_GRAY in light)
  - Reduced button padding (Add button: padx from 10 to 5, Cancel button: no padding)
  - Increased dialog height from 725px to 750px to prevent button cropping
  - Reduced content frame padding from "15" to "10" for better space utilization

- **Add Expense Dialog**:
  - Fixed numpad background color to match dialog frame using `NumPad.TLabelframe` style
  - Ensured consistent theme-aware backgrounds throughout dialog

- **Dashboard Control Buttons**:
  - Made pin and minimize buttons consistent box sizes (both use width=30, height=28)
  - Increased minimize button height from 25px to 28px to match PoC
  - Positioned minimize button to right edge (changed controls_frame x offset from -4 to 0)
  - All control buttons now have consistent sizing and alignment

**Files Modified:**
- `main.py` - Quick Add dialog frame styling, numpad background, button padding, dialog height
- `expense_table.py` - Add Expense dialog numpad background styling
- `dashboard_page_builder.py` - Control button sizing and positioning
- `config.py` - Dialog height adjustment (ADD_EXPENSE_WITH_NUMPAD_HEIGHT: 725 → 750)

**Testing:**
- ✅ Quick Add dialog has consistent background colors throughout
- ✅ Numpad backgrounds match dialog frames in both dialogs
- ✅ Buttons are fully visible with proper spacing
- ✅ Dashboard control buttons have consistent sizing
- ✅ Minimize button positioned at right edge
- ✅ All changes work correctly in both light and dark modes

**Impact:**
- Improved visual consistency across all dialogs
- Better user experience with properly sized and positioned buttons
- Professional appearance with consistent backgrounds
- Enhanced dark mode visual quality

### Syntax Fixes (November 9, 2025)

**CODE QUALITY: Fixed Indentation Errors in Archive Mode Manager and GUI**

**Changes Made:**
- Fixed multiple indentation errors in `archive_mode_manager.py`
  - Corrected `try` block indentation for `update_display_callback()`
  - Fixed indentation for frame configuration calls
  - Fixed indentation for button state configuration
  - Fixed indentation in exception handlers
- Fixed indentation errors in `gui.py`
  - Corrected `else` block indentation for current mode expense filtering
  - Fixed `try` block indentation for label update calls
- All linter errors resolved (0 errors remaining)

**Files Modified:**
- `archive_mode_manager.py` - Fixed 10+ indentation issues
- `gui.py` - Fixed 5+ indentation issues

**Impact:**
- ✅ Code now passes all linter checks
- ✅ Improved code quality and maintainability
- ✅ Prevents potential runtime errors from syntax issues

### Codebase Review & Optimization Analysis (November 9, 2025)

**ANALYSIS: Comprehensive Codebase Review and Opportunity Identification**

**What Was Done:**
- Conducted comprehensive codebase review
- Identified completed optimizations (Analytics Consolidation, Exception Handling, Quick Add Autocomplete)
- Documented 14 new optimization opportunities:
  - 3 High-Priority (Multi-Month Data Aggregation, Atomic File Writes, Dark Mode Consistency)
  - 4 Medium-Priority (Code Quality Improvements)
  - 5 New Feature Opportunities (Categories, AI Chat, Visualization, etc.)
  - 2 Performance Optimizations (Lazy Loading, Caching)

**Files Created:**
- `docs/internal/CODEBASE_REVIEW_v3.6.1.md` - Comprehensive analysis document

**Impact:**
- ✅ Clear roadmap for future improvements
- ✅ Prioritized implementation plan
- ✅ Foundation for next development phase

### Dark Mode Expense Table Improvements (November 9, 2025)

**VISUAL ENHANCEMENTS: Improved Dark Mode Table Styling and Layout**

**Changes Made:**
- Added grayish navy blue background color for expense table in dark mode (#2a2d3a)
  - Only applies in dark mode, light mode remains unchanged (white background)
- Fixed Quick Add expense frame background to match main frame in dark mode
  - Created custom `QuickAdd.TLabelframe` style with theme-aware background
- Fixed status bar and pagination frame backgrounds to match main frame
  - Created `TableStatus.TFrame` style with theme-aware background
- Fixed table container background color mismatch in dark mode
  - Created `TableContainer.TLabelframe` style to match parent frame background
- Increased table height from 8 to 11 rows to display more entries
- Reduced spacing between expense insights and table for better layout
  - Removed padding between metrics section and table container
- Added 1px border to expense table container
  - Uses `BG_DARK_GRAY` border color for subtle definition

**Files Modified:**
- `expense_table.py` - Added table container styling, increased height, fixed status bar backgrounds
- `quick_add_helper.py` - Fixed Quick Add frame background with custom style
- `expense_list_page_builder.py` - Reduced spacing between sections
- `config.py` - Added `BG_TABLE` color for dark mode table background

**Testing:**
- ✅ Dark mode table background matches main frame
- ✅ Quick Add frame background matches in dark mode
- ✅ Status bar and pagination backgrounds match in dark mode
- ✅ Light mode remains unchanged (no visual differences)
- ✅ Table displays 11 rows instead of 8
- ✅ Table positioned closer to expense insights section
- ✅ 1px border visible on table container

**Impact:**
- Improved visual consistency in dark mode
- Better use of screen space with more visible entries
- Enhanced user experience with cleaner layout

### Quick Add Autocomplete Feature (November 9, 2025)

**USER EXPERIENCE ENHANCEMENT: Recurring Expense Suggestions in Inline Quick Add**

**Feature Added:**
- Added autocomplete/dropdown menu to the description field in the inline Quick Add expense form
- Now matches the functionality of other add expense dialogs (Add Expense Dialog, Quick Add from Tray)
- Users can see recurring expense patterns and suggestions as they type

**Implementation:**
- Integrated `AutoCompleteEntry` widget into `QuickAddHelper` class
- Added `description_history` parameter to `QuickAddHelper.__init__()`
- Updated `expense_list_page_builder.py` to pass `description_history` from `expense_tracker`
- Maintained backward compatibility with fallback to plain Entry if `description_history` unavailable
- Updated Enter key navigation to work correctly with `AutoCompleteEntry`
- Updated `set_enabled()` and `clear_form()` methods to handle both widget types

**Benefits:**
- Consistent user experience across all expense entry methods
- Faster expense entry with recurring expense suggestions
- Better discoverability of expense patterns
- Reduced typing for frequently used descriptions

**Files Modified:**
- `quick_add_helper.py` - Added AutoCompleteEntry support, updated widget handling
- `expense_list_page_builder.py` - Pass description_history to QuickAddHelper

**Testing:**
- ✅ Autocomplete suggestions appear when typing
- ✅ Recurring expense patterns shown in dropdown
- ✅ Enter key navigation works correctly (Amount → Description → Submit)
- ✅ Archive mode disable/enable works correctly
- ✅ Form clearing works correctly

**Impact:**
- Improved user experience and consistency
- Faster expense entry workflow
- Better utilization of recurring expense feature

---

### Analytics Method Consolidation (November 8, 2025)

**CODE QUALITY IMPROVEMENT: Eliminated Duplicate Filtering Logic**

**Problem:**
- Multiple analytics methods had duplicate expense filtering code
- Same filtering patterns repeated in 5 different methods
- Made maintenance difficult (fix bugs in multiple places)
- Inconsistent filtering logic across methods

**Duplication Identified:**
1. `calculate_daily_average()` and `calculate_weekly_average()` - Identical month filtering code
2. `calculate_median_expense()` and `calculate_largest_expense()` - Identical past expense filtering code
3. `calculate_weekly_pace()` - Week filtering code (similar pattern)

**Solution:**
- Created 4 reusable helper methods to centralize filtering logic:
  1. `_filter_expenses_by_date_range()` - Generic date range filtering
  2. `_filter_expenses_by_month()` - Month-specific filtering
  3. `_filter_expenses_by_week()` - Week-specific filtering
  4. `_filter_past_expenses()` - Simple past-only filtering
- Refactored all 5 methods to use helper methods
- Eliminated ~50 lines of duplicate code

**Benefits:**
- ✅ Single source of truth for filtering logic
- ✅ Easier maintenance (fix bugs once)
- ✅ Better code organization
- ✅ Consistent filtering behavior
- ✅ No breaking changes (all public APIs unchanged)

**Files Modified:**
- `analytics.py` - Added helper methods, refactored 5 calculation methods

**Testing:**
- ✅ All dashboard calculations work correctly
- ✅ Expense list metrics display accurately
- ✅ Archive mode calculations unchanged
- ✅ No performance degradation

**Impact:**
- Improved code maintainability
- Foundation for future analytics enhancements
- Better code quality and consistency

---

### Archive Mode Bug Fixes (November 8, 2025)

**CRITICAL BUG FIXES: Archive Mode Not Working Correctly**

**Problems Fixed:**
1. **Archive Mode Colors Not Updating**: Main window frame colors weren't changing when switching months
2. **Display Values Not Updating**: Dashboard values (total, count, progress, analytics) weren't updating when switching to archive mode
3. **"+Add Expense" Button Not Disabling**: Button remained enabled in archive mode when it should be disabled
4. **CustomTkinter Widget Compatibility**: Code was trying to use `style` parameter on CustomTkinter widgets (which don't support it)
5. **Tooltip Duplication**: Tooltips were appearing multiple times and not disappearing properly

**Root Causes:**
1. **Widget Type Detection**: Code wasn't properly detecting CustomTkinter widgets vs ttk widgets
2. **Missing Frame Updates**: `main_container` frame wasn't being updated for archive mode
3. **Incorrect Button State Management**: Using `.config()` instead of `.configure()` for CustomTkinter buttons
4. **Tooltip Event Handler Accumulation**: Multiple tooltip event handlers were being bound without removing old ones
5. **Display Update Logic**: `update_display()` wasn't using correct expense filtering for archive mode

**Fixes Applied:**
- ✅ Added `main_container` parameter to ArchiveModeManager and update it for archive/normal mode
- ✅ Improved widget type detection using both `isinstance()` and `hasattr('fg_color')` checks
- ✅ Fixed CustomTkinter button state management (use `.configure()` not `.config()`)
- ✅ Fixed `update_display()` to show ALL expenses in archive mode (no date filtering)
- ✅ Fixed tooltip_manager to unbind old event handlers before binding new ones
- ✅ Added proper tooltip cleanup in archive mode transitions
- ✅ Fixed expense filtering logic for analytics calculations in archive mode
- ✅ Added error handling and logging for debugging display updates

**Files Modified:**
- `archive_mode_manager.py` - Added main_container support, improved widget detection, fixed button state management
- `gui.py` - Fixed update_display() expense filtering, added logging, improved error handling
- `quick_add_helper.py` - Fixed CustomTkinter button state management
- `tooltip_manager.py` - Fixed tooltip duplication by unbinding old handlers before binding new ones

**Testing:**
- ✅ Archive mode colors update correctly (main_container, main_frame, all widgets)
- ✅ Display values update correctly when switching months
- ✅ "+Add Expense" button disables correctly in archive mode
- ✅ Tooltips appear once and disappear properly
- ✅ No errors when switching between archive and normal mode
- ✅ All analytics calculations use correct data for archive mode

**Impact:**
- Archive mode now fully functional
- Proper visual distinction between current and archived months
- Correct data display for historical months
- Better user experience with proper button states and tooltips

---

### Budget Display Update Bug Fix (November 2-3, 2025)

**BUG FIX: "vs. Budget" Metric Not Updating After Budget Change**

**Problem:**
- The "vs. Budget" metric in the Spending Analysis section was not updating after setting/changing the budget
- Bug was present for a while - budget could be saved but display would not refresh
- Users had to restart the application to see the updated budget comparison

**Root Causes Identified:**
1. **Missing Widget References**: Budget labels (`budget_amount_label`, `budget_status_label`) were not extracted as instance attributes in `gui.py`, so `_update_budget_display()` couldn't access them
2. **Wrong Widget Type Attribute**: Code was using `text_color` (for CTkLabel) instead of `foreground` (for ttk.Label)
3. **Incorrect Calculation**: Used `self.expense_tracker.monthly_total` (includes all expenses) instead of `monthly_total_past` (excludes future expenses), causing inconsistent calculations with rest of dashboard

**Fixes Applied:**
- ✅ Added `self.budget_amount_label` and `self.budget_status_label` extraction from widgets dictionary in `create_main_page()`
- ✅ Changed `text_color` to `foreground` in `_update_budget_display()` for ttk.Label compatibility
- ✅ Updated calculation to use `ExpenseDataManager.calculate_monthly_total()` to exclude future expenses (matches `update_display()` logic)
- ✅ Fixed status label to always show "(Click Here)" when budget is not set (matches initial display behavior)

**Testing:**
- ✅ Budget metric updates immediately after saving budget
- ✅ Calculation correctly uses past expenses only
- ✅ Display matches initial dashboard calculation
- ✅ Status text updates correctly (Under/Over/Not set)

**Impact:**
- Budget feature now fully functional - displays update in real-time
- Consistent calculation across all budget displays
- Better user experience with immediate feedback

**Files Modified:**
- `gui.py` - Added widget extraction, fixed `_update_budget_display()` method

---

### Budget Dialog Numpad Button Styling (November 2-3, 2025)

**EXPERIMENTAL STYLING: Neumorphic-Inspired Numpad Buttons**

**Styling Applied:**
- **Dark Blue Theme**: Deep dark blue buttons (`#1E3A8A`) with light cyan/blue text (`#7DD3FC`)
- **Hover Effects**: Lighter blue on hover (`#3B5FA0`) with brighter cyan text (`#A5E8FF`)
- **Pressed State**: Medium blue (`#2A4A90`) with bright cyan text (`#B5F0FF`)
- **Visual Style**: Inspired by modern dial pad designs with high contrast for readability

**Implementation:**
- Custom `BudgetNumPad.TButton` style for Budget Dialog numpad only
- Uses ttk.Button styling (not CustomTkinter) for raised relief support
- Applied only to Budget Dialog numpad, doesn't affect other numpads in application

**Note:** This is experimental styling - may be adjusted or reverted based on user feedback.

**Files Modified:**
- `gui.py` - Added custom numpad button styling in Budget Dialog

---

### Budget Dialog Grid Layout Migration & Final Polish (Previous Backup - November 2, 2025)

**Implementation: Grid Geometry Manager with Padding Fixes**

**LAYOUT MIGRATION:**

- **Grid Geometry Manager Implementation**:
  - Converted Budget Dialog from `pack()` to `grid()` geometry manager (CustomTkinter recommended)
  - All widgets now use `grid()` with explicit `row`, `column`, `sticky`, `padx`, and `pady` parameters
  - Better control over widget positioning and responsive layout
  - Follows CustomTkinter best practices for layout management

- **Padding Optimization & Fixes**:
  - Removed redundant bottom padding from `main_frame` (was causing layout confusion)
  - Standardized padding: `main_frame` uses uniform `pady=8`, `buttons_frame` uses `pady=(10, 10)`
  - Fixed button cutoff issue by removing excessive padding accumulation
  - Dialog height increased to 670px to accommodate buttons with proper clearance
  - Buttons now fully visible with correct spacing

- **Button Sizing Refinements**:
  - Reduced button height from 28px to 25px for more compact appearance
  - Button width: 70px (maintained from previous refinements)
  - Added explicit `border_spacing=2` parameter per CustomTkinter documentation
  - Buttons use `pack(side=tk.LEFT)` inside `buttons_frame` for side-by-side layout
  - More professional, compact button appearance

- **Grid Layout Structure**:
  - Row 0: Instruction label (centered)
  - Row 1: Current Threshold label (centered, navy blue, underlined)
  - Row 2: Amount entry with $ prefix (centered)
  - Row 3: Error label (centered, collapses when empty)
  - Row 4: Number pad (fills width)
  - Row 5: Buttons frame with Set and Cancel buttons (centered)

**TECHNICAL IMPROVEMENTS:**

- **CustomTkinter Documentation Compliance**:
  - Reviewed and applied CustomTkinter CTkButton documentation parameters
  - Proper use of `width`, `height`, and `border_spacing` parameters
  - Explicit padding control through geometry manager (not widget constructors)
  - Correct understanding of `pady` bottom padding (creates space below, doesn't push up)

- **Layout Understanding**:
  - Fixed misconception about bottom padding (it doesn't push content up)
  - Proper spacing hierarchy: main_frame → buttons_frame → buttons
  - Dialog height provides clearance, padding provides internal spacing
  - Removed unnecessary padding accumulations that caused cutoff issues

**Testing:**
- ✅ Buttons fully visible (no cutoff)
- ✅ Proper spacing throughout dialog
- ✅ Grid layout responsive and properly aligned
- ✅ Button sizing compact and professional
- ✅ All widgets positioned correctly
- ✅ Dialog height adequate for all content
- ✅ Error label collapses properly when empty
- ✅ Budget saving and validation working correctly

**Impact:**
- Cleaner, more maintainable layout code using grid()
- Better understanding of CustomTkinter padding and spacing
- Professional button appearance with compact sizing
- No visual glitches or cutoff issues
- Follows CustomTkinter best practices

**Files Modified:**
- `gui.py` - Grid layout migration, button sizing, padding fixes
- `config.py` - Dialog height adjustment (650px → 670px)

**Technical Notes:**
- CustomTkinter's `grid()` requires explicit row/column configuration
- Bottom `pady` adds space below widget (not above)
- Button `border_spacing` controls text-to-border spacing (default 2px)
- Dialog height must account for all content + padding
- Using `pack()` inside `buttons_frame` maintains original side-by-side button layout

---

### Budget Dialog CustomTkinter Refinements (Previous Backup - November 2, 2025)

**Implementation: Budget Dialog UI Improvements with CustomTkinter Integration**

**UI REFINEMENTS:**

- **CustomTkinter Styling**:
  - Migrated budget dialog to use CustomTkinter widgets for modern appearance
  - CustomTkinter labels, entry fields, and buttons for consistent styling
  - Maintained app theme with light gray backgrounds (`BG_LIGHT_GRAY`)
  - Navy purple "Set" button (`PURPLE_ARCHIVE`) with hover effects
  - Smaller, more compact entry field (height: 25px, width: 150px)

- **Standard NumberPadWidget Integration**:
  - Replaced custom CTkButton numpad with standard `NumberPadWidget` for consistency
  - Matches numpad styling used elsewhere in the application
  - Uses ttk.Button with proper spacing and sizing
  - Better integration with existing UI patterns

- **Compact Layout & Spacing**:
  - Reduced all padding throughout dialog for compactness
  - Main frame padding: `padx=15, pady=8` (down from 20/10)
  - Entry field spacing minimized
  - Error label uses `ttk.Label` instead of `CTkLabel` to eliminate minimum height space
  - Numpad and buttons positioned with minimal spacing (2-8px)
  - Dialog height optimized to 650px (reduced from 680px)

- **Error Label Optimization**:
  - Positioned above numpad (in gap between entry and numpad)
  - Switched from `CTkLabel` to `ttk.Label` to eliminate default minimum height
  - Takes zero space when empty, only appears when error occurs
  - No padding - directly adjacent to numpad when visible

- **Button Improvements**:
  - "OK" button renamed to "Set" with navy purple color
  - Button spacing from numpad: 2px bottom padding on numpad, 8px top padding on buttons
  - Smaller button size: 80x30px
  - Improved visual hierarchy

- **Layout Optimizations**:
  - Instruction label: centered with reduced spacing
  - Current Threshold label: centered, underlined, navy blue
  - Entry field: centered, narrow (150px width), minimal height (25px)
  - All elements use minimal padding for compact appearance
  - Corner radius set to 0 on frames to eliminate visual space

**Testing:**
- ✅ Dialog displays correctly with all elements visible
- ✅ Numpad buttons all show properly
- ✅ OK/Cancel buttons visible and accessible
- ✅ Error label appears when needed, zero space when empty
- ✅ Entry field properly sized and centered
- ✅ Compact spacing throughout
- ✅ Budget saving and display working correctly

**Impact:**
- Modern, polished dialog appearance with CustomTkinter styling
- More compact layout with efficient space usage
- Better user experience with optimized spacing
- Consistent with application's numpad widget usage
- Professional visual design

**Files Modified:**
- `gui.py` - Complete budget dialog refactoring with CustomTkinter
- `config.py` - Dialog height adjustments (680px → 650px)
- Added `NumberPadWidget` import from widgets module

**Technical Details:**
- CustomTkinter requires explicit sizing (no auto-sizing like ttk)
- CTkLabel has minimum height even when empty (switched to ttk.Label for error)
- Standard numpad widget ensures consistency across application
- Compact padding requires careful spacing adjustments

---

### Description Suggestions Feature (November 2, 2025)

**Implementation: Description Suggestion Dropdown with Manual Activation**

**⚠️ IMPORTANT: Tkinter Framework Limitation**
- This is **not a traditional auto-complete** (suggestions don't auto-open)
- The dropdown requires **manual activation** (Down arrow or click) to view suggestions
- **Auto-opening the dropdown programmatically blocks user input** due to Tkinter's `ttk.Combobox` focus management
- This is a known limitation of the Tkinter framework (30+ years old)
- Modern GUI frameworks (Qt, GTK, native APIs) handle this better
- The feature provides filtered suggestions but requires user interaction to view them

**FEATURE IMPLEMENTATION:**

- **Description History Tracking**:
  - Tracks all expense descriptions with usage count and last used date
  - Stores history in `description_history.json` file
  - Sorts suggestions by frequency (most used first) then recency
  - Displays last used amount as visual hint
  
- **Suggestion Widget**:
  - Custom `AutoCompleteEntry` widget based on `ttk.Combobox`
  - Filters suggestions based on typed text (minimum 2 characters)
  - Shows up to 5 suggestions by default
  - Manual dropdown activation required (Down arrow or dropdown button click)
  - Suggestions are filtered in background as you type
  - No input blocking - typing continues normally
  
- **Integration**:
  - Added to Quick Add dialog (Ctrl+A / system tray)
  - Added to Add Expense dialog (main table)
  - Automatically updates history when expenses are added
  
- **Configuration**:
  - Settings in `settings.ini` [AutoComplete] section
  - `show_on_focus`: Enable/disable top suggestions on focus
  - `min_chars`: Minimum characters for suggestions (default: 2)
  - `max_suggestions`: Display limit (default: 5)
  - `max_descriptions`: History size limit (default: 50)

**Testing:**
- ✅ Suggestions load as you type
- ✅ Dropdown opens with Down arrow or button click
- ✅ Filtering works correctly (e.g., "Gr" → Groceries, Gas)
- ✅ Top suggestions load on empty field focus
- ✅ Arrow key navigation works
- ✅ Enter key selection works
- ✅ Mouse click selection works
- ✅ No input blocking when typing
- ✅ History updates when expenses added

**Impact:**
- Assists with faster data entry by providing filtered suggestions
- Reduces typing errors and inconsistency
- Foundation for future recurring expense feature
- Functional suggestion system within Tkinter constraints (manual activation required)

**Files Added:**
- `description_autocomplete.py` - Description history management
- `widgets/autocomplete_entry.py` - Auto-complete combobox widget

**Files Modified:**
- `main.py` - Auto-complete integration in Quick Add dialog
- `expense_table.py` - Auto-complete integration in Add Expense dialog
- `settings.ini` - Auto-complete configuration section

---

### Budget Dialog UI Refinements (Previous Backup)

**Implementation: Enhanced Budget Dialog User Experience**

- **DASHBOARD IMPROVEMENTS**:
  - Added "(Click Here)" hint text when budget is not set
  - Status label now always displays (previously hidden when no budget)
  - Provides clear visual cue for users to set their budget

- **DIALOG LAYOUT IMPROVEMENTS**:
  - Centered dialog title: "Set monthly spending budget"
  - Changed "Current Budget Threshold" label to dark navy blue (`BLUE_DARK_NAVY`)
  - Label remains underlined for emphasis
  - Moved OK and Cancel buttons closer to numpad (reduced gap by 10px)
  - Increased dialog height from 520px to 580px to ensure buttons are fully visible

- **USER EXPERIENCE ENHANCEMENTS**:
  - Clearer call-to-action when budget not set
  - Better visual hierarchy with centered title
  - More compact layout with buttons closer to numpad
  - Consistent color scheme with dark navy for important labels

**Testing:**
- ✅ Application starts successfully
- ✅ Dashboard displays "Not set" with "(Click Here)" hint
- ✅ Budget dialog opens with centered title
- ✅ Current budget threshold shows in dark navy blue, underlined
- ✅ OK and Cancel buttons positioned closer to numpad
- ✅ All buttons fully visible in dialog
- ✅ Budget saving and display working correctly

**Impact:**
- Improved user experience with clearer call-to-action
- Better visual design with centered title and consistent colors
- More compact dialog layout with better button positioning
- Enhanced discoverability of budget feature

**Files Modified:**
- dashboard_page_builder.py (added "(Click Here)" hint, always show status label)
- gui.py (centered title, dark navy color for threshold, moved buttons closer)
- config.py (increased BUDGET_HEIGHT from 520 to 580)
- settings.ini (cleared budget threshold for testing)

**Visual Changes:**
- Dashboard: "Not set" now shows "(Click Here)" below it
- Dialog title: Centered "Set monthly spending budget"
- Current threshold: Dark navy blue, underlined
- Buttons: Moved 10px closer to numpad for better spacing

**Next Steps:**
- Monitor user feedback on budget feature
- Consider additional UI refinements if needed
- Continue with other feature enhancements

## Previous Changes (v3.6)

### Budget Dialog Feature Complete (November 1, 2025)

- **NEW FEATURE**: Budget Threshold Display & Dialog
  - Added "vs. Budget" label in Spending Analysis section
  - Displays budget difference with color coding
  - Clickable budget labels open dialog to set monthly budget threshold
  - Budget dialog with numpad, validation, and current threshold display
  - Integrated with settings_manager for persistent configuration

- **CRITICAL BUG FIX**: Tkinter Entry Validation Event Loop Deadlock
  - Discovered pre-filled Entry widgets with validation cause application freeze
  - Solution: Blank entry field + separate display label for current value
  - Fixed settings_manager threading lock issue
  - Documented in AI_REFERENCE_TECH.md as critical Tkinter gotcha

- **COLOR SCHEME REFINEMENTS**: Multiple color constant updates for better readability

### Phase 3: DPI Awareness Cleanup (October 29, 2025)
- Refactored main.py DPI awareness configuration
- Improved extensibility and logging
- Comprehensive code simplification review completed

### Phase 2: Settings Manager Module (October 28-29, 2025)
- NEW MODULE: settings_manager.py (370 lines)
- Thread-safe settings management
- Atomic file writes prevent corruption
- Migrated 3 files, eliminated 51 lines of duplicate logic

### Phase 1: Date Utilities Module (October 28-29, 2025)
- NEW MODULE: date_utils.py (313 lines)
- 19 utility methods for centralized date operations
- Consolidated 23 instances across 8 files
- Eliminated ~40 lines of duplicate try-except blocks

### Combined v3.6 Metrics
- **New Modules**: 2 (date_utils.py, settings_manager.py)
- **Total New Code**: 683 lines of clean, reusable utilities
- **Files Improved**: 12 files refactored
- **Code Eliminated**: ~91 lines of duplicate logic
- **New Features**: Thread-safe settings, atomic writes, centralized date operations

## Status

**Application Status:** FULLY WORKING AND TESTED  
**Build Status:** All changes tested in development environment  
**Ready for:** Continued development, production use

**Next Quick Wins:**
- Exception handling narrowing (window_manager.py, export_data.py, quick_add_helper.py)
- Remove obvious defensive hasattr checks
- Add missing type hints to utility functions
'@

# Replace placeholders with actual values
$info = $info -replace 'BACKUP_DATE_PLACEHOLDER', $backupDate
$info = $info -replace 'BACKUP_VERSION_PLACEHOLDER', $backupVersion

$backupInfoPath = Join-Path -Path $backupDir -ChildPath "BACKUP_INFO.md"
$info | Out-File -FilePath $backupInfoPath -Encoding UTF8

Write-Host ('Backup created successfully: ' + $backupDir)

