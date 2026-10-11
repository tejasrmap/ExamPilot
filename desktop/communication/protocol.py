"""
ExamPilot Chrome Native Messaging Protocol Module
GT InnoX LLP
"""

import sys
import struct
import json
from typing import Dict, Any, Optional
from desktop.utils.logger import logger

def read_native_message(stream = sys.stdin.buffer) -> Optional[Dict[str, Any]]:
    """
    Read a 32-bit little-endian length-prefixed JSON message from Chrome.
    Standard Manifest V3 Native Messaging Protocol.
    """
    try:
        raw_length = stream.read(4)
        if not raw_length or len(raw_length) < 4:
            return None
        msg_length = struct.unpack("@I", raw_length)[0]
        if msg_length == 0:
            return None
        raw_msg = stream.read(msg_length)
        if len(raw_msg) < msg_length:
            return None
        decoded = raw_msg.decode("utf-8")
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"Error reading native message: {e}", exc_info=True)
        return None

def write_native_message(message: Dict[str, Any], stream = sys.stdout.buffer) -> bool:
    """
    Send a 32-bit little-endian length-prefixed JSON message back to Chrome.
    """
    try:
        encoded = json.dumps(message, ensure_ascii=False).encode("utf-8")
        stream.write(struct.pack("@I", len(encoded)))
        stream.write(encoded)
        stream.flush()
        return True
    except Exception as e:
        logger.error(f"Error writing native message: {e}", exc_info=True)
        return False

