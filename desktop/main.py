"""
ExamPilot — Desktop Application Entry Point
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

import sys
import os

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from desktop.app import create_application
from desktop.ui.main_window import MainWindow
from desktop.utils.logger import logger

def main():
    # Support launching the Native Messaging host directly from the compiled binary
    if "--native-host" in sys.argv:
        from desktop.communication.native_host import main as run_native_host
        run_native_host()
        sys.exit(0)

    logger.info("Starting ExamPilot Desktop Application...")
    from desktop.ai.ollama_client import ollama_client
    ollama_client.ensure_service_running()

    app = create_application()
    window = MainWindow()
    window.show()
    logger.info("ExamPilot Main Window displayed.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

