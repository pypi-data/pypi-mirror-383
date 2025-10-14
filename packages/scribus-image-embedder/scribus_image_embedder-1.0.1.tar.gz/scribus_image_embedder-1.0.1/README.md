# Scribus Image Embedder

Embed **linked images** inline into Scribus `.sla` files using the same qCompress format Scribus understands.  
**Images only** (JPG/PNG/TIFF/GIF/BMP). 

---



## Why

Scribus layouts often reference external image files via `PFILE="..."`.  
When you move a `.sla` or share it, file links can break. This tool parses the `.sla`, finds **image frames** (`PTYPE="2"`), and embeds the raw image bytes directly into the document. The result is a self-contained `.sla` that opens cleanly even if original image files are missing.

---

## Features

- **Images only** (no PDF embedding).
- Preserves scaling/position attributes of frames.
- Stores data both as `ImageData` **attribute** and `<ImageData>...</ImageData>` **node** for compatibility.
- Removes `PFILE`/linking attributes, so the SLA stands alone.
- Clean CLI with success/failure exit codes.

---

## Install

### Windows (pipx — recommended)
For users who don’t want to “deal with Python environments,” `pipx` installs this as a standalone command.

```powershell
pip install --user pipx
pipx ensurepath
pipx install scribus-image-embedder
```

Any OS (pip)

```powershell
pip install scribus-image-embedder
```
Usage
```powershell

scribus-embed /path/to/input.sla -o /path/to/output_embedded.sla
```

Windows examples
```powershell

scribus-embed "C:\Layouts\page1.sla" -o "C:\Layouts\page1_embedded.sla"
scribus-embed "\\server\share\newspaper.sla" -o "\\server\share\newspaper_embedded.sla"
```
Behavior

    Scans for PAGEOBJECT elements where PTYPE="2" (image frames).

    If PFILE="..." is present, reads the referenced file and embeds it:

        qCompress format: 4-byte big-endian length + zlib-compressed payload

        Sets isInlineImage="1", inlineImageExt="...", EMBEDDED="1", and other safe defaults

        Removes PFILE, PFILE2, PRFILE, previous ImageData, and link-only child nodes

    Writes a new .sla file; does not modify the original.

Verify Without Opening Scribus
Windows PowerShell
```powershell

# Show embedded data nodes (should see lines)
Select-String -Path "C:\Layouts\page1_embedded.sla" -Pattern '<ImageData>' | Select-Object -First 5

# Show any remaining file links (should show nothing)
Select-String -Path "C:\Layouts\page1_embedded.sla" -Pattern 'PFILE='
```

Linux/macOS


grep -n '<ImageData>' /path/to/page1_embedded.sla | head
grep -n 'PFILE=' /path/to/page1_embedded.sla

Supported Formats

    JPEG/JPG, PNG, TIFF, GIF, BMP (via Pillow

    )

    Width/height detection is best-effort; embedding still works even if detection fails.

Requirements

    Python 3.10+

    Pillow 8.0.0+

Troubleshooting

    scribus-embed: command not found
    Ensure your environment is set correctly. On Windows, either activate your venv or run:

    python -m scribus_image_embedder.cli --help

    Pillow warnings/errors
    Some exotic images (e.g., CMYK TIFFs with unusual tags) may log warnings. Embedding still proceeds; width/height in logs may be 0×0.

    Images appear linked after embedding
    Open the embedded .sla with a text editor and inspect an image frame:

        There should be no PFILE="..." attribute.

        There should be isInlineImage="1" and an <ImageData>...</ImageData> node with a large Base64 payload.

Local Development

# Windows PowerShell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
scribus-embed --help

Run a test:

scribus-embed "C:\path\to\layout.sla" -o "C:\path\to\layout_embedded.sla"

Build & Publish
Build

python -m pip install --upgrade build twine
python -m build
twine check dist\*

Artifacts will appear under dist/:

    scribus_image_embedder-<version>.tar.gz

    scribus_image_embedder-<version>-py3-none-any.whl

Dry Run on TestPyPI

$Env:TWINE_USERNAME="__token__"
$Env:TWINE_PASSWORD="pypi-TESTPYPI_YOUR_TOKEN"
twine upload --repository testpypi dist\*

# simulate an end-user install:
py -3 -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple scribus-image-embedder
scribus-embed --help

Publish to PyPI

$Env:TWINE_USERNAME="__token__"
$Env:TWINE_PASSWORD="pypi-PYPI_YOUR_TOKEN"
twine upload dist\*

Versioning

This project follows semantic versioning:

    Patch: 1.0.1 — bug fixes only

    Minor: 1.1.0 — new features, backwards compatible

    Major: 2.0.0 — breaking changes

PyPI will not let you overwrite an existing version. Bump the version in pyproject.toml before re-uploading.
FAQ

Does this modify my original .sla file?
No. A new output file is created; the source is unchanged.

Can it embed PDF or SVG?
No. This package intentionally supports images only.

Which Scribus versions are compatible?
The inline qCompress format is recognized by modern Scribus (1.5+). If you hit a version-specific quirk, open an issue.

Is my embedded data reversible?
The embedded data is the raw image bytes in a qCompressed wrapper. Scribus reads it natively; this tool doesn’t provide an “extract” command.
Contributing

    Open issues or pull requests on GitHub.

    For feature ideas, include a minimal .sla demonstrating the use-case.

    Keep the package focused on image embedding; PDF embedding is out of scope.

License

MIT © Afueth Thomas
