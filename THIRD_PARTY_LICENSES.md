# Third-Party Licenses

LiteFinPad uses the following open-source libraries. We are grateful to their authors and contributors.

---

## Python Software Foundation License

### Python Standard Library
- **Copyright**: Python Software Foundation
- **License**: PSF License Agreement
- **Used for**: Core Python functionality
- **Link**: https://www.python.org/psf/license/

### pywin32
- **Version**: 306+
- **Copyright**: Copyright (c) 1996-2008 by Mark Hammond and contributors
- **License**: PSF License Agreement
- **Used for**: Windows system tray integration and Windows API access
- **Link**: https://github.com/mhammond/pywin32
- **License Text**: https://github.com/mhammond/pywin32/blob/main/Pythonwin/License.txt

---

## MIT License

### openpyxl
- **Version**: 3.1.0+
- **Copyright**: Copyright (c) 2010-2023 openpyxl authors
- **License**: MIT License
- **Used for**: Excel file generation and formatting
- **Link**: https://openpyxl.readthedocs.io/
- **Repository**: https://foss.heptapod.net/openpyxl/openpyxl

**License Text**:
```
MIT License

Copyright (c) 2010 openpyxl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### et_xmlfile
- **Version**: (dependency of openpyxl)
- **Copyright**: Copyright (c) 2014 openpyxl
- **License**: MIT License
- **Used for**: XML processing for Excel files
- **Repository**: https://foss.heptapod.net/openpyxl/et_xmlfile

**License Text**: Same as openpyxl (MIT License)

---

## Historical Permission Notice and Disclaimer (HPND)

### Pillow (PIL Fork)
- **Version**: 10.0.0+
- **Copyright**: 
  - Copyright (c) 1997-2011 by Secret Labs AB
  - Copyright (c) 1995-2011 by Fredrik Lundh
  - Copyright (c) 2010-2023 by Jeffrey A. Clark (Alex) and contributors
- **License**: HPND License
- **Used for**: Image processing and icon handling
- **Link**: https://python-pillow.org/
- **Repository**: https://github.com/python-pillow/Pillow

**License Text**:
```
The Python Imaging Library (PIL) is

    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh and contributors

Pillow is the friendly PIL fork. It is

    Copyright © 2010-2023 by Jeffrey A. Clark (Alex) and contributors

Like PIL, Pillow is licensed under the open source HPND License:

By obtaining, using, and/or copying this software and/or its associated
documentation, you agree that you have read, understood, and will comply
with the following terms and conditions:

Permission to use, copy, modify and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appears in all copies, and that
both that copyright notice and this permission notice appear in supporting
documentation, and that the name of Secret Labs AB or the author not be
used in advertising or publicity pertaining to distribution of the software
without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
```

---

## BSD License

### ReportLab
- **Version**: 4.0.0+
- **Copyright**: Copyright (c) 2000-2023 ReportLab Inc.
- **License**: BSD License (3-Clause)
- **Used for**: PDF document generation and formatting
- **Link**: https://www.reportlab.com/
- **Repository**: https://github.com/MrBitBucket/reportlab-mirror

**License Text**:
```
Copyright (c) 2000-2023, ReportLab Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

---

## Additional Attributions

### Fonts (Bundled with ReportLab)

#### Bitstream Vera Fonts
- **Copyright**: Copyright (c) 2003 Bitstream, Inc.
- **License**: Bitstream Vera Fonts License (similar to MIT)
- **Used for**: Default fonts in PDF generation
- **Note**: Distributed with reportlab package

#### DarkGarden Font
- **Copyright**: Copyright (c) 2000 Ray Larabie
- **License**: GPL with font exception
- **Note**: Distributed with reportlab package (not used by LiteFinPad)

---

## Development Tools (Not Included in Distribution)

### PyInstaller
- **Version**: 6.0.0+
- **Copyright**: Copyright (c) 2005-2023 PyInstaller Development Team
- **License**: GPL with exception for bundled applications
- **Used for**: Creating standalone executables (build-time only)
- **Link**: https://pyinstaller.org/
- **Note**: Not included in final executable; only used during build process

**GPL Exception**: Applications bundled with PyInstaller are not subject to GPL.
The executable created is not a derivative work of PyInstaller itself.

---

## Summary of License Compatibility

All runtime dependencies use permissive licenses that allow:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ Sublicensing

All libraries are compatible with LiteFinPad's MIT License.

---

## Attribution Guidelines

If you redistribute LiteFinPad or create derivative works:

1. **Required**:
   - Include the MIT License (LICENSE file)
   - Include this THIRD_PARTY_LICENSES.md file
   - Maintain copyright notices

2. **Recommended**:
   - Mention use of Python libraries in your documentation
   - Link to original library repositories
   - Credit library authors in About dialog or README

3. **Not Required** (but appreciated):
   - Notify original authors of derivative works
   - Contribute improvements back to the community

---

## Questions?

For licensing questions or clarifications:
- Review the LICENSE file for LiteFinPad's license
- Visit linked repositories for detailed license information
- Consult with legal counsel for specific use cases

Last Updated: October 13, 2025

