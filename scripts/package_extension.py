"""
ExamPilot Chrome Extension Packaging Script
GT InnoX LLP
Packages the Manifest V3 Chrome Extension into a clean distribution ZIP.
Strictly excludes private keys (*.pem, *.key), user-specific manifests, and cache.
"""

import os
import zipfile
from pathlib import Path

# Files and directories permitted in the distribution package
ALLOWED_FILES = {
    "manifest.json",
    "background.js",
    "content.js",
    "popup.html",
    "popup.js",
    "popup.css",
}

def package_chrome_extension(output_zip: Path = Path("dist/exampilot-chrome-extension.zip")) -> Path:
    ext_dir = Path("chrome-extension")
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    if output_zip.exists():
        output_zip.unlink()

    included_entries = []

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root extension files
        for item in ext_dir.iterdir():
            if item.is_file():
                # Enforce exclusion of private keys and temporary manifests
                if item.suffix in [".pem", ".key", ".pfx", ".tmp", ".bak"]:
                    continue
                if item.name not in ALLOWED_FILES:
                    continue
                zf.write(item, arcname=item.name)
                included_entries.append(item.name)

        # Add icons
        icons_dir = ext_dir / "icons"
        if icons_dir.exists() and icons_dir.is_dir():
            for icon in icons_dir.iterdir():
                if icon.is_file() and icon.suffix.lower() == ".png":
                    arcname = f"icons/{icon.name}"
                    zf.write(icon, arcname=arcname)
                    included_entries.append(arcname)

    print(f"Successfully packaged {len(included_entries)} files into {output_zip}:")
    for e in sorted(included_entries):
        print(f"  + {e}")

    # Security verification
    with zipfile.ZipFile(output_zip, "r") as zf:
        names = zf.namelist()
        for bad_ext in [".pem", ".key", ".pfx"]:
            assert not any(n.endswith(bad_ext) for n in names), f"SECURITY FAILURE: Found {bad_ext} in package!"
        assert not any("native-messaging" in n for n in names), "Found native-messaging in store zip!"
        assert "manifest.json" in names, "manifest.json missing from zip!"

    print("[OK] Extension ZIP security and contents verified.")
    return output_zip

if __name__ == "__main__":
    package_chrome_extension()

