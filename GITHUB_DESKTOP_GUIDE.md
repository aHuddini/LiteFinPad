# GitHub Desktop Guide for v3.6 Release

## 🚀 Quick Start

This guide helps you commit v3.6 changes using GitHub Desktop in **one single commit**.

---

## Single Commit Approach

**Stage ALL modified, new, and deleted files** in GitHub Desktop, then use this commit message:

## Commit Message

**Title:**
```
chore: prepare v3.6 release
```

**Description:**
```
Code Quality Improvements:
- Analytics method consolidation (eliminated ~50 lines of duplicate code)
- Improved exception handling with specific error types
- Better error diagnostics in data operations

Bug Fixes:
- Fixed archive mode display values not updating
- Fixed "+Add Expense" button not disabling in archive mode
- Fixed tooltip duplication issues
- Improved CustomTkinter widget compatibility

New Features:
- Quick Add autocomplete for description field
- New utility modules: date_utils, settings_manager
- New widget: AutoCompleteEntry

Documentation:
- Updated CHANGELOG, README, and DEVELOPER_GUIDE
- Streamlined README (removed excessive emojis)
- Enhanced developer documentation

Project Organization:
- Updated .gitignore (exclude exports, user data)
- Created LiteFinPad_v3.6.spec for builds
- Added .cursorignore and .cursorrules
- Updated version to 3.6
- Cleaned up old files (moved internal docs to docs/internal/, kept BEGINNER_THOUGHTS.md public)
```

---

## Step 2: Push to GitHub

After committing:
1. Click "Push origin" in GitHub Desktop
2. Verify the commit appears on GitHub

---

## Step 3: Create Release Tag

### Option A: Using GitHub Desktop

1. Go to **Repository** → **Create Tag**
2. Tag name: `v3.6`
3. Description: Copy from `RELEASE_NOTES_v3.6.md`
4. Click **Create Tag**
5. Push the tag: **Repository** → **Push Tags**

### Option B: Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click **Releases** → **Draft a new release**
3. Tag: `v3.6`
4. Title: `LiteFinPad v3.6`
5. Description: Copy from `RELEASE_NOTES_v3.6.md`
6. Click **Publish release**

---

## Files to Exclude (Already in .gitignore)

These files should NOT be committed:
- `exports/` directory
- `*.pdf`, `*.xlsx` files
- `description_history.json`
- `LiteFinPad_Backup_*.json`
- `backup_*/` directories
- `data_*/` directories

---

## Verification Checklist

Before pushing:
- [ ] All files staged (modified, new, and deleted)
- [ ] No user data files committed (check .gitignore)
- [ ] Version is 3.6 in `version.txt`
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] Commit message follows the format above

---

## Need Help?

If you encounter issues:
1. Review `RELEASE_NOTES_v3.6.md` for release content
2. Verify `.gitignore` is properly configured
3. Check that all user data files are excluded
