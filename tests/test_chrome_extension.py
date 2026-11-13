import json
import os

def test_manifest_v3_security():
    manifest_path = "chrome-extension/manifest.json"
    assert os.path.exists(manifest_path)
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. Must be Manifest V3
    assert manifest.get("manifest_version") == 3

    # 2. Key must NOT be present
    assert "key" not in manifest, "Hardcoded extension key must be removed"

    # 3. Native Messaging must NOT be in permissions
    permissions = manifest.get("permissions", [])
    assert "nativeMessaging" not in permissions, "Native messaging permission must be removed"
    assert "activeTab" in permissions
    assert "storage" in permissions

    # 4. Service worker must be configured
    assert manifest.get("background", {}).get("service_worker") == "background.js"

def test_extension_files_exist():
    files = [
        "chrome-extension/manifest.json",
        "chrome-extension/background.js",
        "chrome-extension/popup.html",
        "chrome-extension/popup.js",
        "chrome-extension/popup.css"
    ]
    for f in files:
        assert os.path.exists(f), f"File {f} must exist"

