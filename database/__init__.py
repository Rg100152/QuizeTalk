"""SQLite storage layer for QuizeTalk.

Kept in a tiny package so both the app factory and the seed script can share
the exact same connection settings and schema.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g, has_app_context

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "quizetalk.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS quizzes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             TEXT    NOT NULL,
    category          TEXT    NOT NULL DEFAULT 'General',
    description       TEXT    NOT NULL DEFAULT '',
    time_per_question INTEGER NOT NULL DEFAULT 15,
    created_at        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id       INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT    NOT NULL,
    option_a      TEXT    NOT NULL,
    option_b      TEXT    NOT NULL,
    option_c      TEXT    NOT NULL,
    option_d      TEXT    NOT NULL,
    correct_option TEXT   NOT NULL CHECK (correct_option IN ('A','B','C','D')),
    explanation   TEXT    NOT NULL DEFAULT '',
    position      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id    INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    player_name TEXT   NOT NULL DEFAULT 'Player',
    score      INTEGER NOT NULL,
    total      INTEGER NOT NULL,
    accuracy   INTEGER NOT NULL,
    played_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS talks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id     INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    player_name TEXT    NOT NULL DEFAULT 'Player',
    score_text  TEXT    NOT NULL DEFAULT '',
    message     TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id, position);
CREATE INDEX IF NOT EXISTS idx_scores_quiz     ON scores(quiz_id, played_at);
CREATE INDEX IF NOT EXISTS idx_talks_quiz      ON talks(quiz_id, created_at);
"""


def db_path() -> str:
    """Path used by the current Flask app (or the default on-disk DB)."""
    if has_app_context():
        return str(current_app.config.get("DATABASE", DB_PATH))
    return str(DB_PATH)


def connect_db(path: str | None = None) -> sqlite3.Connection:
    connection = sqlite3.connect(path or db_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(path: str | None = None) -> None:
    """Create tables if needed. Safe to call on every startup."""
    connection = connect_db(path)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect_db()
    return g.db


def close_db(error=None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def count_quizzes(path: str | None = None) -> int:
    connection = connect_db(path)
    try:
        return int(connection.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0])
    finally:
        connection.close()
