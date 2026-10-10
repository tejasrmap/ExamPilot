"""
ExamPilot Structured Logger Module
GT InnoX LLP
"""

import logging
import os
import re
from logging.handlers import RotatingFileHandler
from desktop.config import LOGS_DIR

# Sensitive data sanitization pattern (email, passwords, tokens)
REDACT_PATTERNS = [
    (re.compile(r'bearer\s+[A-Za-z0-9\-_\.=]+', re.IGNORECASE), "bearer [REDACTED]"),
    (re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE), "password: [REDACTED]"),
    (re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), "[EMAIL REDACTED]")
]

class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in REDACT_PATTERNS:
                record.msg = pattern.sub(repl, record.msg)
        return True

def setup_logger(name: str = "ExamPilot") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    log_file = LOGS_DIR / "exampilot.log"

    # Rotating File Handler (Max 5MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(SensitiveDataFilter())

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()

