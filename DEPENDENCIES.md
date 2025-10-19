# LiteFinPad Dependencies

**Last Updated**: October 13, 2025  
**Version**: 2.6

---

## Overview

LiteFinPad uses a minimal set of Python libraries to provide expense tracking, Excel/PDF export, and Windows system tray integration. All dependencies use permissive open-source licenses.

---

## Core Dependencies

### 1. pywin32 (>=306)

**Purpose**: Windows API access for system tray icon  
**License**: PSF License  
**Homepage**: https://github.com/mhammond/pywin32  
**Size Impact**: ~5MB in distribution

**What we use**:
- `win32gui` - Window management and system tray
- `win32con` - Windows constants
- `pywintypes` - Windows data types

**Why this library**:
- Direct access to Windows APIs
- Most reliable system tray implementation for Windows
- Mature, well-maintained project
- Better Windows integration than cross-platform alternatives

**Alternatives considered**:
- `pystray`: Cross-platform but less native feel on Windows
- `infi.systray`: Unmaintained since 2016

---

### 2. Pillow (>=10.0.0)

**Purpose**: Image processing for application icon  
**License**: HPND License (Historical Permission Notice and Disclaimer)  
**Homepage**: https://python-pillow.org/  
**Size Impact**: ~3MB in distribution

**What we use**:
- `PIL.Image` - Loading .ico files
- Image conversion for tkinter compatibility
- Icon display in GUI

**Why this library**:
- Industry standard for Python image processing
- Required by tkinter for custom icons
- Well-maintained with security updates
- Minimal overhead for basic icon operations

**Alternatives considered**:
- Native Windows API: More complex, marginal size savings
- Pre-processed images: Still need PIL for tkinter integration

---

### 3. openpyxl (>=3.1.0)

**Purpose**: Excel file generation (.xlsx format)  
**License**: MIT License  
**Homepage**: https://openpyxl.readthedocs.io/  
**Size Impact**: ~2MB bundled

**What we use**:
- Creating new workbooks
- Adding worksheets and cells
- Basic cell formatting (bold, colors, borders)
- Column width adjustment
- Saving .xlsx files

**Why this library**:
- Read/write Excel files natively (no Excel installation required)
- Clean API for cell operations
- Good documentation and community support
- Handles .xlsx format (modern Excel)

**What we DON'T use** (optimization opportunity for v2.7):
- Charts and graphs
- Pivot tables
- Formula evaluation
- VBA macros
- Advanced formatting

**Alternatives considered** for v2.7:
- `xlsxwriter`: Write-only, smaller footprint (~1MB), sufficient for our needs
- `pyexcel`: Higher-level API but adds dependencies
- CSV files: Too basic, loses formatting

**v2.7 Recommendation**: Consider switching to `xlsxwriter` for 50% size reduction

---

### 4. reportlab (>=4.0.0)

**Purpose**: PDF document generation  
**License**: BSD License  
**Homepage**: https://www.reportlab.com/  
**Size Impact**: ~8MB bundled (includes fonts, samples, test files)

**What we use**:
- `reportlab.lib.pagesizes` - Page dimensions (letter size)
- `reportlab.lib.styles` - Basic text styling
- `reportlab.lib.units` - Unit conversions (inches)
- `reportlab.platypus` - High-level document layout
- `reportlab.platypus.Table` - Table generation

**Why this library**:
- Industry-standard PDF generation
- Powerful table support with formatting
- No external dependencies (unlike wkhtmltopdf)
- Professional-quality output

**What we DON'T use** (optimization opportunity for v2.7):
- Graphics and charts
- Sample templates
- Test files
- Advanced fonts
- Barcode generation

**Alternatives considered** for v2.7:
- `fpdf2`: Much lighter (~1MB), simpler API, sufficient for tables
- `weasyprint`: CSS-based, too heavy (~30MB with dependencies)
- `pdfkit`: Requires wkhtmltopdf binary (distribution complexity)
- `PyPDF2`: Cannot create PDFs, only modify existing ones

**v2.7 Recommendation**: Consider switching to `fpdf2` for 80% size reduction

**Current Issue**: Reportlab bundles ~6MB of font files, samples, and test data that we don't use

---

### 5. et_xmlfile

**Purpose**: XML handling for openpyxl  
**License**: MIT License  
**Homepage**: Part of openpyxl ecosystem  
**Size Impact**: <1MB

**What we use**:
- Automatically used by openpyxl for XML processing
- Not directly imported in our code

**Why this library**:
- Required dependency of openpyxl
- Handles the XML structure of .xlsx files
- Optimized for Excel file format

**Note**: If we switch to `xlsxwriter` in v2.7, this dependency can be removed

---

## Development Dependencies

### PyInstaller (>=6.0.0)

**Purpose**: Creating standalone Windows executable  
**License**: GPL with exception for bundled applications  
**Homepage**: https://pyinstaller.org/  
**Not included in distribution** (build-time only)

**Configuration**:
- Using `--onedir` mode for better library bundling
- Manual library copying for problematic modules
- Hidden imports for dynamic dependencies
- TCL/TK data bundling for GUI

---

## Python Standard Library Modules Used

These are included with Python and don't require separate installation:

- `tkinter` - GUI framework
- `json` - Data persistence
- `datetime` - Date/time handling
- `os`, `sys`, `pathlib` - File system operations
- `logging` - Error logging
- `threading` - Tray icon message loop
- `queue` - Thread-safe communication
- `html.parser` - PDF generation support (reportlab dependency)

---

## Size Breakdown (v2.6)

| Component | Size | Percentage |
|-----------|------|-----------|
| Python Runtime | ~15MB | 30% |
| TCL/TK (GUI) | ~12MB | 24% |
| reportlab | ~8MB | 16% |
| pywin32 | ~5MB | 10% |
| Pillow | ~3MB | 6% |
| openpyxl | ~2MB | 4% |
| Application Code | ~1MB | 2% |
| Other | ~4MB | 8% |
| **Total** | **~50MB** | **100%** |

---

## Optimization Opportunities for v2.7

### High Impact
1. **Switch to fpdf2 for PDF** → Save ~7MB (87% reduction)
2. **Switch to xlsxwriter for Excel** → Save ~1MB (50% reduction)
3. **Strip TCL/TK timezone data** → Save ~5MB (42% reduction)

### Medium Impact
4. **Remove reportlab samples** → Save ~2MB (if keeping reportlab)
5. **Strip unused PIL formats** → Save ~1MB (33% reduction)
6. **UPX compression** → Save ~5-10MB (10-20% compression)

### Total Potential Savings: ~15-20MB (30-40% reduction)

---

## License Compatibility

All dependencies use permissive licenses compatible with MIT:

| Library | License | Commercial Use | Attribution Required |
|---------|---------|----------------|---------------------|
| pywin32 | PSF | ✅ Yes | Recommended |
| Pillow | HPND | ✅ Yes | Recommended |
| openpyxl | MIT | ✅ Yes | Yes |
| reportlab | BSD | ✅ Yes | Yes |
| et_xmlfile | MIT | ✅ Yes | Yes |

**Conclusion**: Safe for commercial use, open-source distribution, and redistribution. Attribution is good practice and required for MIT/BSD libraries.

---

## Security Considerations

### Dependency Updates
- Check for security updates quarterly
- Monitor GitHub Security Advisories
- Use `pip list --outdated` to check versions
- Review CHANGELOG for security fixes

### Known Security Issues (as of Oct 2025)
- ✅ No known critical vulnerabilities
- ✅ All libraries actively maintained
- ✅ Regular security patches released

### Update Policy
- Minor version updates: Monthly review
- Security patches: Immediate update
- Major version updates: Test thoroughly before adopting

---

## Building from Source

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Build Executable
```bash
build_latest.bat
```

### Verify Build
```bash
python verify_build.py
```

---

## Credits & Attribution

LiteFinPad is built on the shoulders of giants. Special thanks to:

- **Mark Hammond** and contributors for pywin32
- **Alex Clark** and the Pillow team
- **Eric Gazoni** and the openpyxl team
- **ReportLab Inc.** and contributors
- **Guido van Rossum** and the Python core team
- **Fredrik Lundh** for tkinter improvements

---

## Further Reading

- [Choosing the Right Excel Library](https://www.python-excel.org/)
- [PDF Generation in Python](https://realpython.com/creating-modifying-pdf/)
- [PyInstaller Optimization Guide](https://pyinstaller.org/en/stable/usage.html#reducing-the-size-of-your-executable)

