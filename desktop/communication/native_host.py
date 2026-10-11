"""
ExamPilot Chrome Native Messaging Host Entrypoint
Invoked directly by Chrome browser according to Native Messaging Host Manifest.
GT InnoX LLP
"""

import sys
import os

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from desktop.communication.protocol import read_native_message, write_native_message
from desktop.communication.message_handler import message_handler
from desktop.utils.logger import logger

def main():
    logger.info("ExamPilot Native Messaging Host process started.")
    try:
        while True:
            message = read_native_message(sys.stdin.buffer)
            if message is None:
                # EOF reached (Chrome extension closed connection)
                logger.info("Chrome closed connection. Exiting native host.")
                break

            response = message_handler.handle(message)
            write_native_message(response, sys.stdout.buffer)

    except Exception as e:
        logger.error(f"Fatal error in Native Host: {e}", exc_info=True)
    finally:
        logger.info("ExamPilot Native Host shutdown.")

if __name__ == "__main__":
    main()

