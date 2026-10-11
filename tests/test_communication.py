"""
Unit Tests for Chrome Native Messaging Protocol & Bridge
GT InnoX LLP
"""

import io
import struct
import json
from desktop.communication.protocol import read_native_message, write_native_message
from desktop.communication.message_handler import message_handler
from desktop.security.validation import validate_native_message

def test_native_messaging_framing():
    # Test message serialization
    test_msg = {"action": "ping", "request_id": "test_123"}
    buffer = io.BytesIO()

    success = write_native_message(test_msg, buffer)
    assert success is True

    # Rewind buffer and read back
    buffer.seek(0)
    read_back = read_native_message(buffer)
    assert read_back is not None
    assert read_back["action"] == "ping"
    assert read_back["request_id"] == "test_123"

def test_native_message_handler_ping():
    msg = {"action": "ping", "request_id": "req_001"}
    resp = message_handler.handle(msg)
    assert resp["success"] is True
    assert resp["action"] == "pong"
    assert resp["request_id"] == "req_001"

def test_native_message_handler_get_status():
    msg = {"action": "get_status", "request_id": "req_002"}
    resp = message_handler.handle(msg)
    assert resp["success"] is True
    assert "service_running" in resp
    assert "active_model" in resp

def test_native_message_validation():
    # Valid
    valid, _ = validate_native_message({"action": "ping"})
    assert valid is True

    # Invalid action
    valid, err = validate_native_message({"action": "unauthorized_command"})
    assert valid is False

    # Non-dict
    valid, _ = validate_native_message("string_not_dict")
    assert valid is False

