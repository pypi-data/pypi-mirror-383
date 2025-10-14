# Scribus Image Embedder

Embed **linked images** inline into Scribus `.sla` files using the same qCompress format Scribus understands.  
**Images only** (JPG/PNG/TIFF/GIF/BMP). 

---



## Why

Scribus layouts often reference external image files via `PFILE="..."`.  
When you move a `.sla` or share it, file links can break. This tool parses the `.sla`, finds **image frames** (`PTYPE="2"`), and embeds the raw image bytes directly into the document. The result is a self-contained `.sla` that opens cleanly even if original image files are missing.

---

## Features

- **Images only**.
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

