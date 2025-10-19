# Contributing to LiteFinPad

Thank you for considering contributing to LiteFinPad! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Building from Source](#building-from-source)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Project Philosophy](#project-philosophy)

---

## 🤝 Code of Conduct

- Be respectful and constructive
- Focus on what is best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (Python 3.14 recommended)
- **Windows 10+** (currently Windows-only)
- **Git** for version control
- **Text editor** (VS Code recommended)

### System Requirements

- Windows 10 or later
- 100 MB free disk space (for development)
- Internet connection (for installing dependencies)

---

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/LiteFinPad.git
cd LiteFinPad
```

### 2. Install Dependencies

**IMPORTANT**: Use `python -m pip` to ensure packages install to the correct Python version:

```bash
python -m pip install -r requirements.txt
```

This installs:
- `pywin32>=306` - Windows system tray integration
- `xlsxwriter>=3.2.0` - Excel export
- `fpdf==1.7.2` - PDF generation (specific version for size optimization)
- `pyinstaller>=6.16.0` - Executable building

### 3. Verify Installation

```bash
# Run the application from source
python main.py
```

You should see the LiteFinPad icon appear in your system tray.

---

## 🔨 Building from Source

LiteFinPad uses a dual-script build system with automatic version management.

### Development Builds (Fast Iteration)

```bash
# Build current version for testing
build_dev.bat

# Build with version increment (3.0 → 3.1)
build_dev.bat increment
```

**When to use**:
- Testing new features
- Quick bug fixes
- Daily development work

**Output**: `dist/LiteFinPad_vX.X/`

### Production Releases (Fully Optimized)

```bash
# Build production-ready executable
build_release.bat

# Build with major version bump (3.4 → 4.0)
build_release.bat major
```

**When to use**:
- Creating stable releases
- After thorough testing
- Ready for distribution

**Output**: Fully optimized build in `dist/LiteFinPad_vX.X/`

### Manual Build (Advanced)

```bash
# Using PyInstaller directly
pyinstaller LiteFinPad_v3.4.spec
```

For detailed build system documentation, see [BUILD_SYSTEM_GUIDE.md](BUILD_SYSTEM_GUIDE.md).

---

## 🛠️ Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-dark-mode`
- `bugfix/fix-tray-icon-crash`
- `docs/update-readme`
- `refactor/cleanup-gui-code`

### Commit Messages

Follow conventional commit format:

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code restructuring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Build/tooling changes

**Examples**:
```
feat: add dark mode theme support

Implements dark mode with automatic detection based on Windows theme.
Includes toggle in Settings menu.

Closes #42
```

```
fix: prevent crash on empty description field

Quick Add dialog now validates description before submission.
Shows error message instead of crashing.

Fixes #38
```

---

## 🧪 Testing

### Manual Testing Checklist

Before submitting a PR, test these core workflows:

#### Basic Functionality
- [ ] Application starts and tray icon appears
- [ ] Main window opens from tray icon
- [ ] Can add expense via Add Expense dialog
- [ ] Can add expense via Inline Quick Add
- [ ] Can add expense via tray Quick Add (double-click)
- [ ] Can edit existing expense
- [ ] Can delete existing expense
- [ ] Monthly total updates correctly

#### Data Persistence
- [ ] Expenses save to JSON
- [ ] Data persists after restart
- [ ] Monthly folders created automatically
- [ ] Previous month data archived

#### Export Functionality
- [ ] Excel export generates valid .xlsx file
- [ ] PDF export generates valid .pdf file
- [ ] Exported data matches displayed data

#### UI/UX
- [ ] Keyboard shortcuts work (Enter, Escape)
- [ ] Window positioning correct
- [ ] Dialogs close properly
- [ ] No visual glitches

### Running from Source

```bash
# Always test from source before building
python main.py
```

### Testing Build

```bash
# Build and run executable
build_dev.bat
cd dist\LiteFinPad_vX.X
.\LiteFinPad_vX.X.exe
```

---

## 📤 Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Test thoroughly

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

### PR Title Format

```
[TYPE] Short description

Examples:
[FEAT] Add dark mode support
[FIX] Resolve tray icon crash on exit
[DOCS] Update build instructions
```

### PR Description Template

```markdown
## Description
Brief summary of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested from source (python main.py)
- [ ] Tested from build (exe)
- [ ] All manual tests passed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings or errors
- [ ] Tested thoroughly
```

---

## 💻 Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters** (flexible for readability)
- Use **docstrings** for functions and classes

### Code Structure

```python
def function_name(param1, param2):
    """
    Brief description of what the function does.
    
    Args:
        param1 (type): Description
        param2 (type): Description
        
    Returns:
        type: Description
    """
    # Implementation
    pass
```

### File Organization

- One class per file (exceptions allowed for small utility classes)
- Group imports: standard library → third-party → local
- Keep functions focused and small (< 50 lines preferred)
- Use meaningful variable names

### Comments

- Write self-documenting code first
- Add comments for complex logic
- Explain WHY, not WHAT
- Keep comments up-to-date

**Good**:
```python
# Windows tray icons require special handling due to message loop
self._create_tray_window()
```

**Bad**:
```python
# Create window
self._create_tray_window()
```

### Tkinter GUI Guidelines

- Use descriptive widget names
- Group related widgets together
- Configure widgets immediately after creation
- Use grid layout consistently

---

## 🎯 Project Philosophy

Understanding these principles helps guide contribution decisions:

### 1. Offline First
- **No internet required** for core functionality
- **No cloud sync** - all data stays local
- **No telemetry** or tracking

### 2. Lightweight & Fast
- Keep bundle size **< 25 MB**
- Optimize for **fast startup** (< 2 seconds)
- Minimize **memory usage** (< 100 MB)

### 3. User-Centric Design
- **Keyboard shortcuts** for power users
- **Smart defaults** - minimal configuration needed
- **Non-intrusive** - system tray, not taskbar

### 4. Simplicity Over Features
- Features must be **genuinely useful**
- **No feature bloat** - reject unnecessary complexity
- **Conservative updates** - stability over novelty

### 5. Windows Native Feel
- Follow **Windows UI conventions**
- Use **native Windows APIs** where appropriate
- **Respect user preferences** (theme, language, etc.)

---

## 📝 Documentation

When adding features, update relevant documentation:

- **README.md** - User-facing features
- **CHANGELOG.md** - All changes (required)
- **BUILD_SYSTEM_GUIDE.md** - Build process changes
- **DEPENDENCIES.md** - New library additions
- **THIRD_PARTY_LICENSES.md** - New library licenses
- **Code comments** - Complex logic explanation

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check if issue already exists
2. Test with latest version
3. Try to reproduce consistently

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what happened

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment**
- OS: Windows 10/11
- LiteFinPad Version: v3.4
- Python Version (if from source): 3.14

**Additional context**
Any other relevant information
```

---

## 💡 Feature Requests

We welcome feature ideas! However, LiteFinPad prioritizes **simplicity and stability**.

### Feature Request Template

```markdown
**Feature Description**
Clear, concise description

**Use Case**
Why is this useful? Real-world scenario?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other ways to solve this?

**Additional Context**
Screenshots, mockups, examples
```

### Evaluation Criteria

Features are evaluated on:
1. **Value** - Does it solve a real problem?
2. **Complexity** - How much code/maintenance?
3. **Scope** - Does it fit the project vision?
4. **Impact** - How many users benefit?

---

## 🎓 Learning Resources

### Python + Tkinter
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Real Python Tkinter Tutorial](https://realpython.com/python-gui-tkinter/)

### Windows API (pywin32)
- [pywin32 Documentation](https://mhammond.github.io/pywin32/)
- [Windows API Reference](https://docs.microsoft.com/en-us/windows/win32/)

### PyInstaller
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [PyInstaller Hooks](https://pyinstaller.org/en/stable/hooks.html)

---

## ❓ Questions?

- **General Questions**: Open a [GitHub Discussion](../../discussions)
- **Bug Reports**: Open an [Issue](../../issues)
- **Feature Ideas**: Open an [Issue](../../issues) with "Feature Request" label

---

## 📜 License

By contributing to LiteFinPad, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

**Thank you for contributing to LiteFinPad!** 🎉

Every contribution, no matter how small, helps make this project better.

