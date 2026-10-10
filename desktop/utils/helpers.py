"""
ExamPilot Helpers and Utility Functions
GT InnoX LLP
"""

import datetime
from typing import Optional

def format_timestamp(ts_iso: Optional[str] = None) -> str:
    """Format an ISO timestamp to human friendly display."""
    if not ts_iso:
        dt = datetime.datetime.now()
    else:
        try:
            dt = datetime.datetime.fromisoformat(ts_iso)
        except Exception:
            return ts_iso
    return dt.strftime("%b %d, %Y • %I:%M %p")

def truncate_text(text: str, max_chars: int = 120) -> str:
    """Safely truncate text with an ellipsis."""
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."

