"""
Test packaged ExamPilot.exe Native Messaging Host.
Verifies that the compiled standalone binary runs without Python.
"""

import sys
import os
import subprocess
import struct
import json

def main():
    exe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist", "ExamPilot", "ExamPilot.exe")
    print(f"[*] Testing packaged executable at: {exe_path}")
    assert os.path.exists(exe_path), f"ExamPilot.exe not found at {exe_path}"

    proc = subprocess.Popen(
        [exe_path, "--native-host"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    msg = {"action": "ping", "request_id": "pkg-test-01"}
    encoded = json.dumps(msg).encode("utf-8")
    length = len(encoded)

    # Send 4-byte native messaging length prefix followed by JSON
    proc.stdin.write(struct.pack("=I", length))
    proc.stdin.write(encoded)
    proc.stdin.flush()

    # Read 4-byte response length
    raw_len = proc.stdout.read(4)
    if not raw_len or len(raw_len) < 4:
        stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
        print(f"[!] Stderr output: {stderr_out}")
        raise RuntimeError("No response from packaged executable!")

    resp_len = struct.unpack("=I", raw_len)[0]
    raw_resp = proc.stdout.read(resp_len).decode("utf-8")
    resp_obj = json.loads(raw_resp)

    print(f"[*] Response from packaged ExamPilot.exe: {resp_obj}")
    assert resp_obj.get("action") == "pong", f"Unexpected action: {resp_obj.get('action')}"
    assert resp_obj.get("status") == "connected", f"Unexpected status: {resp_obj.get('status')}"
    assert resp_obj.get("request_id") == "pkg-test-01", f"Unexpected request_id: {resp_obj.get('request_id')}"

    # Terminate process
    proc.terminate()
    print("[SUCCESS] Packaged Windows executable runs Native Messaging Host successfully!")

if __name__ == "__main__":
    main()

