# GitHub Commit Plan for v3.6 Release

## 📋 Overview

This document provides a step-by-step guide for committing v3.6 changes using **GitHub Desktop**. Commits are organized by feature/change type for clear history and easy review.

**Current Version:** 3.5.3  
**Target Version:** 3.6  
**Last Commit:** `61235fc` - Fix: Build system Python version & privacy improvements (v3.5.3)

---

## 🎯 Commit Strategy

We'll organize commits into logical groups. You can follow this plan in GitHub Desktop by:
1. Staging files for each commit
2. Using the provided commit messages
3. Committing one group at a time

---

## Commit 1: Code Quality - Analytics Method Consolidation

**Type:** `refactor(analytics)`

**Files:**
- `analytics.py`

**Message:**
```
refactor(analytics): consolidate duplicate expense filtering logic

- Created 4 reusable helper methods to centralize filtering:
  - _filter_expenses_by_date_range() - Generic date range filtering
  - _filter_expenses_by_month() - Month-specific filtering
  - _filter_expenses_by_week() - Week-specific filtering
  - _filter_past_expenses() - Simple past-only filtering
- Refactored 5 calculation methods to use helper methods
- Eliminated ~50 lines of duplicate code
- No breaking changes (all public APIs unchanged)

Benefits:
- Single source of truth for filtering logic
- Easier maintenance (fix bugs once)
- Better code organization and consistency
```

---

## Commit 2: Code Quality - Exception Handling Improvements

**Type:** `refactor(data): improve exception handling`

**Files:**
- `data_manager.py`

**Message:**
```
refactor(data): narrow exception handling in data operations

- Replaced broad Exception catches with specific exception types
- load_expenses(): Now catches FileNotFoundError, JSONDecodeError, PermissionError, OSError
- save_expenses(): Now catches PermissionError, OSError
- Better error diagnostics and user-friendly error messages
- Consistent with exception handling refactoring patterns
```

---

## Commit 3: Bug Fixes - Archive Mode

**Type:** `fix(archive): resolve archive mode display and widget issues`

**Files:**
- `archive_mode_manager.py`
- `gui.py`
- `quick_add_helper.py`
- `tooltip_manager.py`

**Message:**
```
fix(archive): resolve archive mode display and widget issues

Fixed multiple critical issues preventing archive mode from working:
- Archive mode colors now update correctly when switching months
- Display values (total, count, progress, analytics) update properly
- "+Add Expense" button correctly disables in archive mode
- CustomTkinter widget compatibility (proper detection and configuration)
- Tooltip duplication issues (proper event handler cleanup)

Changes:
- Added main_container parameter to ArchiveModeManager
- Improved widget type detection using isinstance() and hasattr()
- Fixed CustomTkinter button state management (use .configure() not .config())
- Fixed update_display() expense filtering for archive mode
- Fixed tooltip_manager to unbind old handlers before binding new ones
```

---

## Commit 4: Feature - Quick Add Autocomplete

**Type:** `feat(quick-add): add autocomplete to inline description field`

**Files:**
- `quick_add_helper.py`
- `expense_list_page_builder.py`

**Message:**
```
feat(quick-add): add autocomplete to inline description field

- Added AutoCompleteEntry widget to Quick Add description field
- Shows recurring expense patterns and suggestions as users type
- Consistent experience across all expense entry methods
- Maintained backward compatibility with fallback to plain Entry
- Updated Enter key navigation and form handling for AutoCompleteEntry
```

---

## Commit 5: Documentation Updates

**Type:** `docs: update documentation for v3.6 changes`

**Files:**
- `CHANGELOG.md`
- `README.md`
- `docs/developer/DEVELOPER_GUIDE.md`

**Message:**
```
docs: update documentation for v3.6 changes

- Added Quick Add Autocomplete feature to CHANGELOG and README
- Updated DEVELOPER_GUIDE with QuickAddHelper API documentation
- Added exception handling improvements documentation
- Updated analytics consolidation documentation
- Streamlined README (removed excessive emojis and technical details)
```

---

## Commit 6: Project Cleanup and Organization

**Type:** `chore: organize project files and cleanup root directory`

**Files:**
- `.gitignore` (add exports/, docs/internal/)
- Deleted: `BEGINNER_THOUGHTS.md`, `LiteFinPad_v3.5.3.spec`, `test_config.py`
- New: `LiteFinPad_v3.6.spec`, `.cursorignore`, `.cursorrules`
- Moved files to `docs/internal/` and `exports/`

**Message:**
```
chore: organize project files and cleanup root directory

- Moved internal documentation to docs/internal/
- Moved export files to exports/
- Added .cursorignore and .cursorrules for development
- Updated .gitignore to exclude build artifacts and backups
- Created LiteFinPad_v3.6.spec for PyInstaller builds
- Removed old spec files and test files
```

---

## Commit 7: New Modules and Features

**Type:** `feat: add new utility modules and widgets`

**Files:**
- `date_utils.py` (new)
- `settings_manager.py` (new)
- `description_autocomplete.py` (new)
- `widgets/autocomplete_entry.py` (new)
- `widgets/__init__.py` (updated)

**Message:**
```
feat: add new utility modules and widgets

New modules:
- date_utils.py: Centralized date operations (19 utility methods)
- settings_manager.py: Thread-safe settings management
- description_autocomplete.py: Recurring expense pattern tracking
- widgets/autocomplete_entry.py: Auto-complete combobox widget

These modules provide reusable functionality and eliminate code duplication.
```

---

## Commit 8: Configuration and Build Updates

**Type:** `chore: update configuration and build files`

**Files:**
- `version.txt` (3.6)
- `requirements.txt`
- `settings.ini`
- `config.py`
- Various module updates for new features

**Message:**
```
chore: update configuration and build files for v3.6

- Updated version to 3.6
- Updated requirements.txt with new dependencies
- Updated settings.ini with autocomplete configuration
- Updated config.py with new constants
- Updated build scripts to use LiteFinPad_v3.6.spec
```

---

## Optional: Single Commit Approach

If you prefer fewer commits, you can combine related changes:

**Option A: Feature-based commits**
1. All code quality improvements (analytics + exception handling)
2. All bug fixes (archive mode)
3. All new features (autocomplete + new modules)
4. Documentation updates
5. Project cleanup

**Option B: Single commit for v3.6**
```
chore: prepare v3.6 release

- Code quality improvements (analytics consolidation, exception handling)
- Archive mode bug fixes
- Quick Add autocomplete feature
- New utility modules (date_utils, settings_manager, autocomplete)
- Documentation updates
- Project cleanup and organization
```

---

## Release Notes Template

When creating the GitHub release, use this template:

```markdown
# LiteFinPad v3.6 Release

## 🎉 What's New

### Quick Add Autocomplete
- Added autocomplete suggestions to the description field in inline Quick Add
- Shows recurring expense patterns as you type
- Consistent experience across all expense entry methods

### Archive Mode Improvements
- Fixed display values not updating when viewing past months
- Fixed "+Add Expense" button not disabling in archive mode
- Fixed tooltip duplication issues
- Improved CustomTkinter widget compatibility

## 🔧 Code Quality Improvements

- Consolidated duplicate expense filtering logic in analytics
- Improved exception handling with specific error types
- Better error diagnostics and user-friendly messages

## 📦 Technical Improvements

- New utility modules: date_utils, settings_manager
- New widgets: AutoCompleteEntry
- Project cleanup and organization

## 📚 Documentation

- Updated README (streamlined, less technical)
- Enhanced developer guide
- Complete changelog updates

---

**Full Changelog:** See [CHANGELOG.md](CHANGELOG.md) for complete details.
```

---

## Next Steps

1. Review this commit plan
2. Use GitHub Desktop to stage and commit files according to this plan
3. Push commits to GitHub
4. Create a new release tag: `v3.6`
5. Use the release notes template above

