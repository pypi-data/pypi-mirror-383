from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List


SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  model TEXT,
  input_text TEXT,
  output_text TEXT,
  tokens_in INTEGER,
  tokens_out INTEGER,
  latency_ms INTEGER,
  content_hash TEXT UNIQUE,
  raw TEXT
);
"""

FLOWS_SCHEMA = """
CREATE TABLE IF NOT EXISTS flows (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_start TEXT,
  ts_end TEXT,
  method TEXT,
  url TEXT,
  host TEXT,
  path TEXT,
  status INTEGER,
  provider TEXT,
  model TEXT,
  remote_flow_id TEXT,
  req_headers TEXT,
  req_body TEXT,
  resp_headers TEXT,
  resp_body TEXT,
  tokens_in INTEGER,
  tokens_out INTEGER,
  latency_ms INTEGER,
  session_id TEXT,
  template_key TEXT,
  content_hash TEXT UNIQUE,
  raw TEXT
);
CREATE INDEX IF NOT EXISTS idx_flows_ts ON flows(ts_start);
CREATE INDEX IF NOT EXISTS idx_flows_provider ON flows(provider);
CREATE INDEX IF NOT EXISTS idx_flows_model ON flows(model);
CREATE INDEX IF NOT EXISTS idx_flows_session ON flows(session_id);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_flows_remote_id ON flows(remote_flow_id);
"""


class Database:
    def __init__(self, path: Path):
        self.path = path

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.path))

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as con:
            con.execute("PRAGMA journal_mode=WAL;")
            con.executescript(SCHEMA)
            con.executescript(FLOWS_SCHEMA)

    def ingest(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = [
            (
                r["ts"],
                r["model"],
                r["input_text"],
                r["output_text"],
                int(r.get("tokens_in", 0)),
                int(r.get("tokens_out", 0)),
                int(r.get("latency_ms", 0)),
                r["content_hash"],
                r["raw"],
            )
            for r in records
        ]
        with self._conn() as con:
            cur = con.executemany(
                """
                INSERT OR IGNORE INTO requests
                (ts, model, input_text, output_text, tokens_in, tokens_out, latency_ms, content_hash, raw)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            return cur.rowcount or 0

    def fetch_all(self) -> List[Dict[str, Any]]:
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM requests ORDER BY ts ASC").fetchall()
            return [dict(r) for r in rows]

    def ingest_flows(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = []
        for r in records:
            rows.append(
                (
                    r.get("ts_start"),
                    r.get("ts_end"),
                    r.get("method"),
                    r.get("url"),
                    r.get("host"),
                    r.get("path"),
                    int(r.get("status") or 0),
                    r.get("provider"),
                    r.get("model"),
                    r.get("remote_flow_id"),
                    r.get("req_headers"),
                    r.get("req_body"),
                    r.get("resp_headers"),
                    r.get("resp_body"),
                    int(r.get("tokens_in") or 0),
                    int(r.get("tokens_out") or 0),
                    int(r.get("latency_ms") or 0),
                    r.get("session_id"),
                    r.get("template_key"),
                    r.get("content_hash"),
                    r.get("raw"),
                )
            )
        with self._conn() as con:
            cur = con.executemany(
                """
                INSERT OR IGNORE INTO flows (
                  ts_start, ts_end, method, url, host, path, status, provider, model, remote_flow_id,
                  req_headers, req_body, resp_headers, resp_body,
                  tokens_in, tokens_out, latency_ms, session_id, template_key, content_hash, raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            return cur.rowcount or 0

    def fetch_flows(self, where: str = "", params: tuple = ()) -> List[Dict[str, Any]]:
        q = "SELECT * FROM flows"
        if where:
            q += " WHERE " + where
        q += " ORDER BY COALESCE(ts_start, ts_end) ASC"
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(q, params).fetchall()
            return [dict(r) for r in rows]
