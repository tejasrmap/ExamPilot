"""
ExamPilot SQLite Database Management
GT InnoX LLP
"""

import sqlite3
import shutil
import os
from pathlib import Path
from typing import Optional
from desktop.config import DATABASE_PATH
from desktop.utils.logger import logger

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    options_json TEXT NOT NULL,
    suggested_answer TEXT,
    answer_text TEXT,
    explanation TEXT,
    option_analysis_json TEXT,
    confidence REAL DEFAULT 0.0,
    needs_review INTEGER DEFAULT 0,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS question_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_feedback TEXT NOT NULL,
    corrected_answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_created ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_question ON question_feedback(question_id);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(setting_key);
"""

DEFAULT_SUBJECTS = [
    "General",
    "Computer Science",
    "Mathematics",
    "Data Science",
    "Physics",
    "Chemistry",
    "Business & Finance",
    "Networking"
]

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def init_database(self):
        """Initialize tables, apply migrations, seed initial data."""
        try:
            with self.get_connection() as conn:
                conn.executescript(CREATE_TABLES_SQL)
                
                # Check migration version
                cur = conn.cursor()
                cur.execute("SELECT MAX(version) FROM schema_migrations")
                row = cur.fetchone()
                current_ver = row[0] if (row and row[0] is not None) else 0

                if current_ver < SCHEMA_VERSION:
                    cur.execute(
                        "INSERT INTO schema_migrations (version) VALUES (?)",
                        (SCHEMA_VERSION,)
                    )
                    conn.commit()
                    logger.info(f"Database migrated to schema version {SCHEMA_VERSION}")

                # Seed default subjects if empty
                cur.execute("SELECT COUNT(*) FROM subjects")
                if cur.fetchone()[0] == 0:
                    for s in DEFAULT_SUBJECTS:
                        cur.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (s,))
                    conn.commit()

                # Seed default user if empty
                cur.execute("SELECT COUNT(*) FROM users")
                if cur.fetchone()[0] == 0:
                    cur.execute("INSERT INTO users (display_name) VALUES ('Learner')")
                    conn.commit()

        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise

    def backup(self, destination_path: Path) -> bool:
        """Create a full database backup safely using sqlite3 backup API."""
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            with self.get_connection() as src_conn:
                dst_conn = sqlite3.connect(str(destination_path))
                src_conn.backup(dst_conn)
                dst_conn.close()
            logger.info(f"Database successfully backed up to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return False

    def restore(self, backup_path: Path) -> bool:
        """Restore database from an existing backup file."""
        if not backup_path.exists():
            logger.error(f"Backup file not found at {backup_path}")
            return False
        try:
            # First create an emergency backup of current db
            emergency_backup = self.db_path.with_suffix(".bak")
            shutil.copy2(self.db_path, emergency_backup)

            src_conn = sqlite3.connect(str(backup_path))
            with self.get_connection() as dst_conn:
                src_conn.backup(dst_conn)
            src_conn.close()
            logger.info(f"Database restored successfully from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}", exc_info=True)
            return False

    def clear_all_history(self) -> bool:
        """User-controlled complete history wipe."""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM question_feedback")
                conn.execute("DELETE FROM practice_sessions")
                conn.execute("DELETE FROM questions")
                conn.commit()

            # Run VACUUM with autocommit outside transaction
            conn2 = self.get_connection()
            conn2.isolation_level = None
            conn2.execute("VACUUM")
            conn2.close()

            logger.info("All question history wiped by user request.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}", exc_info=True)
            return False

db_manager = DatabaseManager()
