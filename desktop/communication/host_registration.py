"""
ExamPilot Chrome Native Messaging Host Registration Module
GT InnoX LLP
"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, Optional

try:
    import winreg
except ImportError:
    winreg = None

HOST_NAME = "com.gtinnox.exampilot"
# New Replacement Extension ID derived from fresh keypair in manifest.json
EXTENSION_ID = "gdamjmdjoeegfhjolmnakjgphlgpckdh"
ALLOWED_ORIGIN = f"chrome-extension://{EXTENSION_ID}/"

def get_base_dir() -> Path:
    """Return the absolute path of the ExamPilot installation/workspace root."""
    return Path(__file__).resolve().parent.parent.parent

def generate_host_manifest(output_path: Optional[Path] = None, base_dir: Optional[Path] = None) -> Path:
    """
    Generate host manifest dynamically using the actual installation directory.
    Eliminates hardcoded user paths.
    """
    root = base_dir or get_base_dir()
    bat_path = root / "scripts" / "run_native_host.bat"
    
    if output_path is None:
        output_path = root / "chrome-extension" / "native-messaging" / "host-manifest.json"

    # Template reading with dynamic replacement if template exists
    template_path = root / "chrome-extension" / "native-messaging" / "host-manifest-template.json"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        manifest_str = template_str.replace("{{HOST_PATH}}", str(bat_path.resolve()).replace("\\", "\\\\"))
        manifest_str = manifest_str.replace("{{EXTENSION_ID}}", EXTENSION_ID)
        manifest_data = json.loads(manifest_str)
    else:
        manifest_data = {
            "name": HOST_NAME,
            "description": "ExamPilot Native Messaging Host for Windows Desktop Application",
            "path": str(bat_path.resolve()),
            "type": "stdio",
            "allowed_origins": [
                ALLOWED_ORIGIN
            ]
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return output_path

def register_host_in_registry(manifest_path: Path) -> Tuple[bool, str]:
    """Register the manifest path in Windows Registry under HKCU (platform-aware)."""
    if winreg is None:
        return True, "Non-Windows environment detected; Windows Registry registration skipped."

    try:
        reg_key_path = rf"Software\Google\Chrome\NativeMessagingHosts\{HOST_NAME}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path.resolve()))
        return True, "Successfully registered in Windows Registry (HKCU)."
    except Exception as e:
        return False, f"Failed to register in Windows Registry: {e}"

def unregister_host_from_registry() -> Tuple[bool, str]:
    """Remove the registry key on uninstallation (platform-aware)."""
    if winreg is None:
        return True, "Non-Windows environment detected; Windows Registry cleanup skipped."

    try:
        reg_key_path = rf"Software\Google\Chrome\NativeMessagingHosts\{HOST_NAME}"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_key_path)
        return True, "Successfully removed from Windows Registry (HKCU)."
    except FileNotFoundError:
        return True, "Key does not exist in HKCU."
    except Exception as e:
        return False, f"Failed to delete registry key: {e}"

def is_host_registered() -> bool:
    """Check if the registry key exists and points to an existing file (platform-aware)."""
    if winreg is None:
        # On non-Windows platforms, check if manifest exists
        base = get_base_dir()
        manifest_file = base / "chrome-extension" / "native-messaging" / "host-manifest.json"
        return manifest_file.exists()

    try:
        reg_key_path = rf"Software\Google\Chrome\NativeMessagingHosts\{HOST_NAME}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key_path) as key:
            val, _ = winreg.QueryValueEx(key, "")
            return Path(val).exists()
    except Exception:
        return False

if __name__ == "__main__":
    manifest_file = generate_host_manifest()
    success, msg = register_host_in_registry(manifest_file)
    print(f"Dynamic host manifest generated at: {manifest_file}")
    print(f"Registry registration: {msg}")
    sys.exit(0 if success else 1)
