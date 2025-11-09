# LiteFinPad v3.6 Release Notes

**Release Date:** November 9, 2025  
**Version:** 3.6

---

## 🎉 What's New

### Quick Add Autocomplete
- Added autocomplete suggestions to the description field in inline Quick Add expense form
- Shows recurring expense patterns as you type
- Consistent experience across all expense entry methods (Quick Add, Add Expense Dialog, System Tray)
- Faster expense entry with intelligent suggestions

### Archive Mode Improvements
- **Fixed:** Display values (total, count, progress, analytics) now update correctly when viewing past months
- **Fixed:** "+Add Expense" button now properly disables in archive mode
- **Fixed:** Tooltip duplication issues resolved
- **Improved:** CustomTkinter widget compatibility and styling

---

## 🔧 Code Quality Improvements

### Analytics Method Consolidation
- Eliminated duplicate expense filtering logic across 5 calculation methods
- Created 4 reusable helper methods for centralized filtering
- Reduced code duplication by ~50 lines
- Single source of truth for filtering logic

### Exception Handling Improvements
- Narrowed broad exception catches to specific exception types
- Better error diagnostics and user-friendly error messages
- Improved data loading/saving error handling

---

## 📦 Technical Improvements

### New Utility Modules
- **`date_utils.py`**: Centralized date operations (19 utility methods)
- **`settings_manager.py`**: Thread-safe settings management with atomic writes
- **`description_autocomplete.py`**: Recurring expense pattern tracking

### New Widgets
- **`widgets/autocomplete_entry.py`**: Auto-complete combobox widget for text input

---

## 📚 Documentation Updates

- Streamlined README (removed excessive emojis and technical details)
- Enhanced developer guide with new API documentation
- Complete changelog updates for all v3.6 changes

---

## 🐛 Bug Fixes

- Archive mode display values not updating
- Archive mode button states not disabling correctly
- Tooltip duplication and event handler issues
- CustomTkinter widget styling compatibility

---

## 📊 Technical Details

**Files Modified:** 20+ files  
**New Modules:** 3 (date_utils, settings_manager, description_autocomplete)  
**New Widgets:** 1 (autocomplete_entry)  
**Code Quality:** Eliminated ~50 lines of duplicate code

---

## 🔄 Migration Notes

**No breaking changes** - This is a fully backward-compatible release.

- All existing data files work without modification
- Settings are automatically migrated
- No configuration changes required

---

## 📥 Installation

Download the latest release from the [Releases page](https://github.com/aHuddini/LiteFinPad/releases).

**System Requirements:**
- Windows 10/11
- No additional dependencies required (all bundled)

---

## 🙏 Thank You

Thank you for using LiteFinPad! If you encounter any issues or have suggestions, please [open an issue](https://github.com/aHuddini/LiteFinPad/issues) on GitHub.

---

**Full Changelog:** See [CHANGELOG.md](CHANGELOG.md) for complete details.

