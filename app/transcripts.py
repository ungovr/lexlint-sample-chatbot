"""Stores every conversation, with the customer's name and email address.

Kept indefinitely so a business can review what its assistant said.
"""

import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "transcripts.db"


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            started_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            conversation_id TEXT NOT NULL REFERENCES conversations(id),
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            sent_at TEXT NOT NULL
        );
        """
    )
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_conversation(business_id: str, customer_name: str, customer_email: str) -> str:
    conversation_id = uuid.uuid4().hex
    with _db() as conn:
        conn.execute(
            "INSERT INTO conversations VALUES (?, ?, ?, ?, ?)",
            (conversation_id, business_id, customer_name, customer_email, _now()),
        )
    return conversation_id


def append(conversation_id: str, role: str, text: str) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT INTO messages VALUES (?, ?, ?, ?)",
            (conversation_id, role, text, _now()),
        )


def messages(conversation_id: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages WHERE conversation_id = ? ORDER BY sent_at",
            (conversation_id,),
        )
        return [dict(r) for r in rows]


def for_business(business_id: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM conversations WHERE business_id = ? ORDER BY started_at DESC",
            (business_id,),
        )
        return [dict(r) | {"messages": messages(r["id"])} for r in rows]
