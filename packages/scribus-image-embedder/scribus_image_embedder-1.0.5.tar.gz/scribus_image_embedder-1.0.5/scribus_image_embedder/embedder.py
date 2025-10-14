# Author : Afueth Thomas
# Created : 2025-10-09
# Last Modified : 2025-10-09
# Version : 1.0.0 (images only)

import os
import base64
import zlib
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, List, Optional

def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except Exception:
        pass

# Supported image extensions only (no PDF)
_EXT_MAP = {
    "jpeg": "jpg", "jpg": "jpg",
    "png": "png",
    "tiff": "tif", "tif": "tif",
    "gif": "gif",
    "bmp": "bmp",
}

def detect_ext_wh(path: str) -> Tuple[str, int, int]:
    """Return (normalized_ext, width, height). Falls back gracefully if Pillow fails."""
    suffix = Path(path).suffix.replace(".", "").lower()
    try:
        from PIL import Image  # Pillow is a runtime dependency
        with Image.open(path) as im:
            fmt = (im.format or "").lower()
            ext = _EXT_MAP.get(fmt) or (suffix or "png")
            w, h = im.size
            return ext, w, h
    except Exception as e:
        log(f"Pillow failed for '{path}': {e}")
        ext = _EXT_MAP.get(suffix, suffix or "png")
        return ext, 0, 0

def resolve_path(pfile: str, sla_dir: str) -> str:
    if not pfile:
        return ""
    return pfile if os.path.isabs(pfile) else os.path.abspath(os.path.join(sla_dir, pfile))

def qcompress(raw: bytes) -> bytes:
    """Qt qCompress format: 4-byte BE length + zlib-compressed payload."""
    return struct.pack(">I", len(raw)) + zlib.compress(raw)

def embed_images_in_sla(sla_file: str, output_path: Optional[str] = None) -> Optional[str]:
    log("\n=== Scribus SLA Inline Embedder — images only ===")
    log(f"Input: {sla_file}")

    if not os.path.exists(sla_file):
        log(f"✗ File not found: {sla_file}")
        return None

    sla_dir = os.path.dirname(os.path.abspath(sla_file))
    tree = ET.parse(sla_file)
    root = tree.getroot()

    frames: List[tuple[ET.Element, str]] = []
    for elem in root.iter("PAGEOBJECT"):
        if elem.attrib.get("PTYPE") == "2":  # image frame
            pfile = (elem.attrib.get("PFILE") or "").strip()
            if pfile:
                frames.append((elem, pfile))

    log(f"Linked image frames found: {len(frames)}")

    embedded = skipped = 0

    for elem, hint in frames:
        try:
            abs_path = resolve_path(hint, sla_dir)
            log(f"\n→ {os.path.basename(hint)}")
            log(f"Resolved: {abs_path}")

            if not os.path.exists(abs_path):
                log("Missing file; skipped")
                skipped += 1
                continue

            ext, w, h = detect_ext_wh(abs_path)
            log(f"Detected: {ext.upper()}" + (f"  {w}×{h}" if w and h else ""))

            raw = open(abs_path, "rb").read()
            if not raw:
                log("Empty file; skipped")
                skipped += 1
                continue

            b64 = base64.b64encode(qcompress(raw)).decode("ascii")

            # Remove prior linking/inline artifacts
            for a in ("PFILE", "PFILE2", "PRFILE", "ImageData", "isInlineImage", "inlineImageExt"):
                elem.attrib.pop(a, None)
            for child in list(elem):
                if child.tag in ("IMAGEOBJECT", "DATA", "ImageData"):
                    elem.remove(child)

            # Set inline attributes
            elem.set("isInlineImage", "1")
            elem.set("inlineImageExt", ext)
            elem.set("PFILE", "")
            elem.set("EMBEDDED", "1")
            elem.set("IRENDER", "1")
            elem.set("PICART", "1")
            elem.set("PICSHAPE", "1")
            elem.set("SCALETYPE", elem.get("SCALETYPE", "1"))
            elem.set("RATIO", elem.get("RATIO", "1"))
            elem.set("LOCALSCX", elem.get("LOCALSCX", "1"))
            elem.set("LOCALSCY", elem.get("LOCALSCY", "1"))
            elem.set("LOCALX", elem.get("LOCALX", "0"))
            elem.set("LOCALY", elem.get("LOCALY", "0"))
            elem.set("LOCALROT", elem.get("LOCALROT", "0"))

            # Attribute + child node to satisfy both Scribus variants
            elem.set("ImageData", b64)
            ET.SubElement(elem, "ImageData").text = b64

            embedded += 1
            log("✓ Embedded inline (qCompress)")

        except Exception as e:
            log(f"Error: {e}")
            skipped += 1

    out = output_path or f"{os.path.splitext(sla_file)[0]}_embedded.sla"
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root, encoding="unicode", method="xml")

    with open(out, "w", encoding="utf-8") as f:
        f.write(xml_header + xml_body)

    if os.path.exists(out):
        log(f"\n✓ Wrote: {out}")
        log(f"   Embedded: {embedded}, Skipped: {skipped}")
        return out

    log("✗ Failed to write output")
    return None
