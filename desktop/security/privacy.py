"""
ExamPilot Privacy & Local-First Guard Module
GT InnoX LLP
"""

import urllib.parse
from desktop.utils.logger import logger

class PrivacyGuard:
    """Enforces strict offline-first guarantees and local-only network traffic."""

    ALLOWED_LOCAL_HOSTS = ["localhost", "127.0.0.1", "::1"]

    @classmethod
    def verify_url_is_local(cls, url: str) -> bool:
        """
        Verify that an AI endpoint points strictly to a local loopback interface.
        Blocks external telemetry or unpermitted cloud APIs.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            hostname = parsed.hostname or ""
            is_local = hostname.lower() in cls.ALLOWED_LOCAL_HOSTS
            if not is_local:
                logger.warning(f"PrivacyGuard blocked non-local connection attempt to: {url}")
            return is_local
        except Exception as e:
            logger.error(f"PrivacyGuard failed to parse URL: {e}")
            return False

    @staticmethod
    def get_privacy_declarations() -> dict:
        """Returns the formal privacy factsheet for ExamPilot."""
        return {
            "offline_first": True,
            "cloud_telemetry": False,
            "credential_collection": False,
            "screen_monitoring": "User-initiated only via deliberate hotkey or button click",
            "storage_location": "Local SQLite database on user's machine only",
            "data_retention": "Full user control with one-click instant history wipe"
        }

