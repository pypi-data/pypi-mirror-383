import os
from pathlib import Path

from fastapi.testclient import TestClient


def test_api_status_and_flows(tmp_path: Path):
    # Set DB path before import
    os.environ["DB_PATH"] = str(tmp_path / "flows.db")
    from lifesaver_lite_llm.core.storage import Database
    from lifesaver_lite_llm.web.app import app

    db = Database(Path(os.environ["DB_PATH"]))
    db.init()
    # insert a minimal flow
    db.ingest_flows(
        [
            {
                "ts_start": "2025-01-01T00:00:00+00:00",
                "ts_end": "2025-01-01T00:00:01+00:00",
                "method": "POST",
                "url": "https://api.openai.com/v1/chat/completions",
                "host": "api.openai.com",
                "path": "/v1/chat/completions",
                "status": 200,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "remote_flow_id": None,
                "req_headers": "{}",
                "req_body": "hello",
                "resp_headers": "{}",
                "resp_body": "hi",
                "tokens_in": 5,
                "tokens_out": 2,
                "latency_ms": 1000,
                "session_id": "",
                "template_key": "tpl:abc12345",
                "content_hash": "hash123",
                "raw": "{}",
            }
        ]
    )

    client = TestClient(app)
    r = client.get("/api/status")
    assert r.status_code == 200
    j = r.json()
    assert j["flows_count"] >= 1

    r2 = client.get("/api/flows?provider=openai&redact=1")
    assert r2.status_code == 200
    j2 = r2.json()
    assert j2["total"] >= 1
    assert "data" in j2
