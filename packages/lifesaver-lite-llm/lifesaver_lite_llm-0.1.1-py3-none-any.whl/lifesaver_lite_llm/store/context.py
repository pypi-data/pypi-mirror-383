from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  cwd TEXT,
  labels TEXT,
  pinned_notes TEXT
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  metadata TEXT,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
"""


@dataclass
class Session:
    id: int
    name: str
    created_at: str
    cwd: str
    labels: Dict[str, Any]
    pinned_notes: str


class ContextStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as con:
            con.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def create_session(
        self,
        name: str,
        cwd: Optional[str] = None,
        labels: Optional[Dict[str, Any]] = None,
    ) -> Session:
        ts = datetime.utcnow().isoformat()
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO sessions(name, created_at, cwd, labels, pinned_notes) VALUES (?, ?, ?, ?, ?)",
                (name, ts, cwd or os.getcwd(), json.dumps(labels or {}), ""),
            )
            sid = cur.lastrowid
        return self.get_session(sid)

    def get_session(self, session_id: int) -> Session:
        with self._conn() as con:
            row = con.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if not row:
                raise ValueError("Session not found")
            return Session(
                id=row[0],
                name=row[1],
                created_at=row[2],
                cwd=row[3] or "",
                labels=json.loads(row[4] or "{}"),
                pinned_notes=row[5] or "",
            )

    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        ts = datetime.utcnow().isoformat()
        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO messages(session_id, role, content, created_at, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, ts, json.dumps(metadata or {})),
            )
            return cur.lastrowid

    def get_messages(self, session_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT role, content, created_at, metadata FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
            out = []
            for r in reversed(rows):
                out.append(
                    {
                        "role": r[0],
                        "content": r[1],
                        "created_at": r[2],
                        "metadata": json.loads(r[3] or "{}"),
                    }
                )
            return out

    def set_pinned_notes(self, session_id: int, notes: str) -> None:
        with self._conn() as con:
            con.execute(
                "UPDATE sessions SET pinned_notes = ? WHERE id = ?", (notes, session_id)
            )

    def get_pinned_notes(self, session_id: int) -> str:
        with self._conn() as con:
            row = con.execute(
                "SELECT pinned_notes FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            return (row[0] or "") if row else ""
