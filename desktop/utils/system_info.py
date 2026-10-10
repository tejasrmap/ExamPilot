"""
ExamPilot System Hardware Information & Model Advisor
GT InnoX LLP
"""

import os
import shutil
import platform
import psutil
from typing import Dict, Any, List, Optional

def get_installed_gpus() -> List[str]:
    """
    Detect display adapters / GPUs quickly and reliably across platforms.
    On Windows, queries the registry class for display adapters (zero external process overhead).
    """
    gpus: List[str] = []
    if platform.system() == "Windows":
        try:
            import winreg
            key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as base_key:
                i = 0
                while True:
                    try:
                        sub_name = winreg.EnumKey(base_key, i)
                        i += 1
                        if sub_name.isdigit():
                            with winreg.OpenKey(base_key, sub_name) as sub_key:
                                try:
                                    desc, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                                    # Filter out virtual display mirrors if real hardware exists
                                    if desc and desc not in gpus and not any(v in desc.lower() for v in ["mirage", "rdp", "virtual display"]):
                                        gpus.append(desc)
                                except FileNotFoundError:
                                    pass
                    except OSError:
                        break
        except Exception:
            pass

    elif platform.system() == "Linux":
        try:
            # Check lspci or sysfs
            if os.path.exists("/sys/class/drm"):
                for card in os.listdir("/sys/class/drm"):
                    if card.startswith("card") and "-" not in card:
                        gpus.append(f"Linux DRM Device ({card})")
        except Exception:
            pass

    return gpus

def get_disk_info(target_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely get disk usage without hardcoded drive assumptions.
    Supports Windows (any drive letter or UNC), Linux, and macOS.
    """
    path_to_check = target_path or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~") or os.getcwd()
    try:
        if platform.system() == "Windows":
            drive = os.path.splitdrive(os.path.abspath(path_to_check))[0]
            root = (drive + "\\") if drive else os.path.abspath(path_to_check)
        else:
            root = os.path.abspath(path_to_check)

        usage = shutil.disk_usage(root)
        return {
            "free_disk_gb": round(usage.free / (1024 ** 3), 1),
            "total_disk_gb": round(usage.total / (1024 ** 3), 1),
            "drive_path": root
        }
    except Exception:
        # Fallback to system root
        try:
            usage = shutil.disk_usage(os.path.abspath(os.sep))
            return {
                "free_disk_gb": round(usage.free / (1024 ** 3), 1),
                "total_disk_gb": round(usage.total / (1024 ** 3), 1),
                "drive_path": os.sep
            }
        except Exception:
            return {
                "free_disk_gb": 0.0,
                "total_disk_gb": 0.0,
                "drive_path": "Unknown"
            }

def get_system_hardware_info(target_path: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve system hardware specs including RAM, CPU, GPU, disk, and platform."""
    # Memory
    mem = psutil.virtual_memory()
    total_ram_gb = round(mem.total / (1024 ** 3), 1)
    available_ram_gb = round(mem.available / (1024 ** 3), 1)

    # CPU
    cpu_count = psutil.cpu_count(logical=True) or 2
    cpu_freq = psutil.cpu_freq()
    freq_ghz = round(cpu_freq.current / 1000, 2) if cpu_freq else 0.0

    # Disk
    disk_info = get_disk_info(target_path)
    free_disk_gb = disk_info["free_disk_gb"]
    total_disk_gb = disk_info["total_disk_gb"]
    drive_path = disk_info["drive_path"]

    # GPU
    gpus = get_installed_gpus()
    has_nvidia = any("nvidia" in g.lower() or "geforce" in g.lower() or "rtx" in g.lower() or "gtx" in g.lower() for g in gpus)
    gpu_desc = ", ".join(gpus) if gpus else "Integrated Graphics"

    # Classification & Model Guidance
    if total_ram_gb < 10.0:
        tier = "minimum"
        recommended_model = "qwen2.5:1.5b"
        tier_label = "Entry / 8 GB (Requires Lightweight Models)"
        recommendation_notes = "System has ≤ 8 GB RAM. Lightweight models (1.5B or 3B) are recommended to maintain responsiveness."
    elif total_ram_gb < 24.0:
        tier = "recommended"
        recommended_model = "qwen2.5:7b-instruct"
        tier_label = "Optimal / 16 GB (Recommended Configuration)"
        notes = "System has 16 GB RAM. Perfectly configured to run Qwen 2.5 7B Instruct with high accuracy."
        if has_nvidia:
            notes += f" Detected dedicated GPU ({gpus[0]}), enabling fast local inference."
        recommendation_notes = notes
    else:
        tier = "advanced"
        recommended_model = "qwen2.5:7b-instruct"
        tier_label = "Advanced / 32+ GB (High Performance)"
        recommendation_notes = f"System has 32+ GB RAM ({gpu_desc}). Capable of running 7B or 14B models with zero throttling."

    return {
        "platform": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
        "processor": platform.processor() or "Generic Processor",
        "cpu_threads": cpu_count,
        "cpu_freq_ghz": freq_ghz,
        "total_ram_gb": total_ram_gb,
        "available_ram_gb": available_ram_gb,
        "free_disk_gb": free_disk_gb,
        "total_disk_gb": total_disk_gb,
        "drive_path": drive_path,
        "gpus": gpus,
        "gpu_desc": gpu_desc,
        "has_discrete_gpu": has_nvidia,
        "tier": tier,
        "tier_label": tier_label,
        "recommended_model": recommended_model,
        "recommendation_notes": recommendation_notes
    }

def check_disk_space_for_model(required_gb: float, target_path: Optional[str] = None) -> bool:
    """Ensure there is enough free disk space before pulling a model."""
    disk_info = get_disk_info(target_path)
    free_gb = disk_info["free_disk_gb"]
    # Require model size + 2 GB safety margin
    return free_gb >= (required_gb + 2.0)
