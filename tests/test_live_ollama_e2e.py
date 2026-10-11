"""
End-to-end live Ollama verification script.
Tests actual local AI inference without mocks against Ollama service.
"""

import sys
import os
import json
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.ai.ollama_client import ollama_client
from desktop.core.model_manager import model_manager
from desktop.core.answer_engine import answer_engine
from desktop.communication.message_handler import MessageHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_live_ollama")

def main():
    print("=" * 60)
    print("TESTING LIVE LOCAL OLLAMA INTEGRATION (ZERO MOCKS)")
    print("=" * 60)

    # 1. Health & Models
    status = model_manager.get_status()
    print(f"[*] Ollama CLI Installed: {status['cli_installed']}")
    print(f"[*] Ollama Service Running: {status['service_running']}")
    assert status['service_running'], "Ollama service is not running on localhost:11434!"

    installed = [m['name'] for m in status['installed_models']]
    print(f"[*] Available Local Models: {installed}")
    assert len(installed) > 0, "No models installed in Ollama!"

    # Choose model
    target_model = "qwen2.5:0.5b" if any("qwen2.5:0.5b" in m for m in installed) else installed[0]
    model_manager.set_active_model(target_model)
    print(f"[*] Active model configured: {target_model}")

    # 2. Test direct answer generation
    print("\n[*] Testing core AnswerEngine with real MCQ...")
    q_text = "What is the primary function of an operating system's CPU scheduler?"
    options = {
        "A": "To compile high-level source code into machine instructions",
        "B": "To decide which ready process should be allocated the CPU core",
        "C": "To manage physical sector allocation on magnetic hard disks",
        "D": "To encrypt network packets before transmission over the internet"
    }

    success, result, err = answer_engine.analyze(
        question_text=q_text,
        options=options,
        subject="Computer Science",
        model=target_model
    )

    print(f"[*] AnswerEngine Success: {success}")
    if not success:
        print(f"[!] Error: {err}")
        sys.exit(1)

    print(f"[*] Suggested Answer: {result.get('suggested_answer')}")
    print(f"[*] Confidence Score: {result.get('confidence')}")
    print(f"[*] Explanation: {result.get('explanation', '')[:150]}...")
    print(f"[*] Options Analyzed: {list(result.get('option_analysis', {}).keys())}")

    assert result.get("suggested_answer") == "B", f"Expected answer B, got {result.get('suggested_answer')}"
    assert result.get("confidence") > 0.0, "Confidence score must be greater than zero"

    # 3. Test MessageHandler (Chrome Extension Native Messaging interface)
    print("\n[*] Testing MessageHandler (Native Messaging Protocol with Live Model)...")
    handler = MessageHandler()

    test_msg = {
        "request_id": "test-req-001",
        "action": "analyze_question",
        "payload": {
            "question": "Which protocol is primarily used for secure communication over the web?",
            "options": {
                "A": "HTTP",
                "B": "FTP",
                "C": "HTTPS",
                "D": "Telnet"
            },
            "subject_name": "Networking"
        }
    }

    response = handler.handle(test_msg)
    print(f"[*] MessageHandler Response Success: {response.get('success')}")
    print(f"[*] Action: {response.get('action')}")
    data = response.get("data", {})
    print(f"[*] Suggested Option: {data.get('suggested_answer')}")
    print(f"[*] Explanation: {data.get('explanation', '')[:120]}...")

    assert response.get("success") is True, f"Handler failed: {response.get('error')}"
    assert data.get("suggested_answer") == "C", f"Expected answer C, got {data.get('suggested_answer')}"

    print("\n" + "=" * 60)
    print("ALL LIVE OLLAMA TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
