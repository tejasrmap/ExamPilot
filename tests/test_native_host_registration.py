"""
Unit Tests for ExamPilot Native Messaging Host Registration
GT InnoX LLP
"""

import sys
import json
import tempfile
from pathlib import Path
from desktop.communication.host_registration import (
    generate_host_manifest, is_host_registered, HOST_NAME, EXTENSION_ID, ALLOWED_ORIGIN, get_base_dir
)

def test_host_manifest_no_wildcards_and_dynamic_path():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        manifest_path = Path(tmp.name)

    try:
        generate_host_manifest(manifest_path)
        assert manifest_path.exists()

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["name"] == HOST_NAME
        assert data["type"] == "stdio"
        assert "allowed_origins" in data
        assert len(data["allowed_origins"]) == 1

        # Must NOT contain wildcard
        assert "chrome-extension://*/" not in data["allowed_origins"]
        assert data["allowed_origins"][0] == ALLOWED_ORIGIN
        assert EXTENSION_ID in data["allowed_origins"][0]

        # Verify dynamic path is based on actual root
        base_dir = get_base_dir()
        expected_script_path = str((base_dir / "scripts" / "run_native_host.bat").resolve())
        assert data["path"] == expected_script_path
    finally:
        try:
            manifest_path.unlink(missing_ok=True)
        except Exception:
            pass

def test_host_manifest_custom_installation_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_install_root = Path(tmp_dir) / "CustomExamPilot"
        fake_manifest = fake_install_root / "manifest.json"

        generate_host_manifest(output_path=fake_manifest, base_dir=fake_install_root)
        assert fake_manifest.exists()

        with open(fake_manifest, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected_target = str((fake_install_root / "scripts" / "run_native_host.bat").resolve())
        assert data["path"] == expected_target

def test_registry_registration_status_platform_aware():
    # Platform-aware registry check: executes on Windows, handles non-Windows gracefully
    registered = is_host_registered()
    if sys.platform == "win32":
        assert registered is True
    else:
        assert isinstance(registered, bool)
