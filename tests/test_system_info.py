"""
Unit Tests for ExamPilot Hardware Detection & System Info
GT InnoX LLP
"""

import os
from desktop.utils.system_info import (
    get_system_hardware_info, get_disk_info, check_disk_space_for_model, get_installed_gpus
)

def test_hardware_info_structure():
    info = get_system_hardware_info()
    assert "total_ram_gb" in info
    assert "available_ram_gb" in info
    assert info["total_ram_gb"] > 0
    assert info["cpu_threads"] >= 1
    assert "tier" in info
    assert info["tier"] in ["minimum", "recommended", "advanced"]
    assert "gpus" in info
    assert isinstance(info["gpus"], list)

def test_disk_info_non_hardcoded():
    # Test current working directory
    disk_info = get_disk_info(os.getcwd())
    assert disk_info["total_disk_gb"] > 0
    assert disk_info["free_disk_gb"] > 0
    assert "drive_path" in disk_info

    # Test invalid / fallback path
    fallback_info = get_disk_info("Z:\\NonExistentPath\\FakeFolder")
    assert "free_disk_gb" in fallback_info

def test_check_disk_space():
    # 0.1 GB should comfortably pass
    assert check_disk_space_for_model(0.1) is True
    # 99999 GB should fail
    assert check_disk_space_for_model(99999.0) is False

def test_gpu_detection():
    gpus = get_installed_gpus()
    assert isinstance(gpus, list)
    # On Windows, at least one display adapter is registered
    if os.name == "nt":
        assert len(gpus) >= 1

