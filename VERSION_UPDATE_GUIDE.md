# Version Update Guide

## 📋 Complete Checklist for Version Updates

This guide ensures consistency across all version references when releasing a new version of LiteFinPad.

---

## 🔄 Step-by-Step Version Update Process

### **1. Update Core Version Files**

#### **version.txt**
- Update to new version number (e.g., `3.6`)
- This file is the **single source of truth** for the version

#### **Spec File**
- Rename: `LiteFinPad_v3.5.spec` → `LiteFinPad_v3.6.spec`
- Update `name` fields inside the spec (lines 44 and 64):
  ```python
  name='LiteFinPad_v3.6',
  ```
- Move old spec to `archive_old_specs/`

#### **gui.py**
- Update fallback version (search for `version = "`):
  ```python
  version = "3.6"  # Fallback version
  ```

---

### **2. Update Documentation**

#### **README.md** (3 changes required)

**A) Main Title (Line 1):**
```markdown
# 💰 LiteFinPad v3.6
```

**B) Version Badge (Line 7):**
```markdown
![Version](https://img.shields.io/badge/version-3.6-blue.svg)
```

**C) "What's New" Section (Lines 28-50):**

**Template:**
```markdown
## 🆕 What's New in v3.6

### [Title of Major Feature or Change] ([Month] 2025)

**New Features:**
- 🎨 **[Feature Name]**: Description
- ℹ️ **[Feature Name]**: Description

**Code Quality Improvements:**
- 📦 **[Improvement]**: Description
- 📉 **[Metric]**: Specific numbers if applicable

**Technical:**
- [Technical detail 1]
- [Technical detail 2]

**Known Issues:**
- [Issue 1, if any]
- None reported for v3.6
```

---

### **3. Update CHANGELOG.md**

Add new version section at the **top** of the file:

```markdown
## 🏗️ Version 3.6 - [Feature Name] - [Month] [Day], 2025

### **Summary**
[2-3 sentence overview of the release]

### ✨ **New Features**
[List features with descriptions]

### 🔧 **Improvements**
[List improvements]

### 📊 **Build Statistics**
[Include metrics: line counts, file sizes, etc.]

### 📝 **Developer Notes**
[Include breaking changes, future work, etc.]
```

---

### **4. Create Backup**

Run PowerShell command:
```powershell
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupDir = "backup_v3.6_[feature_name]_$timestamp"
New-Item -ItemType Directory -Path $backupDir
Copy-Item -Path "*.py" -Destination $backupDir -Force
Copy-Item -Path "widgets" -Destination $backupDir -Recurse -Force
Copy-Item -Path "config.py" -Destination $backupDir -Force
Copy-Item -Path "*.spec" -Destination $backupDir -Force
```

---

### **5. Build & Test**

#### **Test Python Execution:**
```bash
python main.py
```

#### **Build Production Executable:**
```bash
.\build_release.bat
```
*(Build script will auto-detect the new spec file)*

#### **Verify Build:**
- Check `dist\LiteFinPad_v3.6\LiteFinPad_v3.6.exe` exists
- Test executable runs correctly
- Verify all features work as expected

---

### **6. Commit to GitHub**

#### **Files to Commit:**
- ✅ `version.txt`
- ✅ `gui.py`
- ✅ `LiteFinPad_v3.6.spec`
- ✅ `README.md` (3 changes: title, badge, "What's New")
- ✅ `CHANGELOG.md`
- ✅ Any feature/bug fix files
- ✅ `build_release.bat` / `build_dev.bat` (if modified)

#### **Commit Message Template:**
```
Release v3.6 - [Feature Name]

[Brief description of major changes]

New Features:
- [Feature 1]
- [Feature 2]

Improvements:
- [Improvement 1]

Technical:
- [Technical change 1]

Files Modified: [list]
Files Added: [list]
Documentation: Updated README.md, CHANGELOG.md
```

#### **GitHub Release:**
1. Go to: https://github.com/aHuddini/LiteFinPad/releases
2. Click "Create a new release"
3. **Tag:** `v3.6`
4. **Title:** `v3.6 - [Feature Name]`
5. **Description:** Copy from CHANGELOG.md v3.6 section
6. **Attach:** `dist\LiteFinPad_v3.6\LiteFinPad_v3.6.exe`
7. **Publish release**

---

## 🎯 Quick Reference: Files to Update

| File | Update Required | Location |
|------|----------------|----------|
| `version.txt` | Change version number | Line 1 |
| `LiteFinPad_v*.spec` | Rename file + update `name` fields | Lines 44, 64 |
| `gui.py` | Update fallback version | Search `version = "` |
| `README.md` | Update title | Line 1 |
| `README.md` | Update version badge | Line 7 |
| `README.md` | Update "What's New" section | Lines 28-50 |
| `CHANGELOG.md` | Add new version section | Top of file |

---

## ✅ Validation Checklist

Before committing:
- [ ] `version.txt` updated
- [ ] Spec file renamed and `name` fields updated
- [ ] Old spec archived to `archive_old_specs/`
- [ ] `gui.py` fallback version updated
- [ ] README.md title updated (line 1)
- [ ] README.md badge updated (line 7)
- [ ] README.md "What's New" section updated (lines 28-50)
- [ ] CHANGELOG.md new section added at top
- [ ] Backup created
- [ ] Python execution tested
- [ ] Executable built and tested
- [ ] All changes committed to GitHub
- [ ] GitHub Release created with executable

---

## 📝 Notes

### **Build Scripts Auto-Detection**
The build scripts (`build_release.bat` and `build_dev.bat`) automatically detect the current spec file by searching for `LiteFinPad_v*.spec` in the root directory. **No manual updates needed** for build scripts!

### **Single Source of Truth**
`version.txt` is read by `version_manager.py` and used throughout the build process. Update this file first, and it will propagate to most build artifacts automatically.

### **README.md Best Practices**
- Keep "What's New" section concise but informative
- Use emojis for visual appeal (🎨 ℹ️ 🎯 📦 📉 🔧 🚀)
- Include specific metrics when possible (line counts, percentages)
- List known issues honestly for transparency
- Archive old "What's New" content to CHANGELOG.md

### **GitHub Repo Display**
GitHub automatically displays README.md on the repository's main page. Updates to README.md will immediately reflect on:
- https://github.com/aHuddini/LiteFinPad (main repo page)
- Repository "About" section (if configured)
- Social preview cards (if configured)

---

## 🔗 Related Documentation
- `CHANGELOG.md` - Full version history
- `BUILD_SYSTEM_GUIDE.md` - Build process documentation
- `AI_MEMORY.md` - AI-assisted development log

---

**Last Updated:** v3.5 (October 2025)

