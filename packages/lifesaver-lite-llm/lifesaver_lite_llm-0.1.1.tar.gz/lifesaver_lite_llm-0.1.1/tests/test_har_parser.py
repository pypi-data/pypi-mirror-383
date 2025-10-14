import json
from pathlib import Path

from lifesaver_lite_llm.core.parser import load_flows


def make_har(tmp_path: Path) -> Path:
    har = {
        "log": {
            "version": "1.2",
            "entries": [
                {
                    "startedDateTime": "2025-01-01T00:00:00Z",
                    "time": 123,
                    "request": {
                        "method": "POST",
                        "url": "https://api.anthropic.com/v1/messages",
                        "headers": [
                            {"name": "content-type", "value": "application/json"}
                        ],
                        "postData": {
                            "mimeType": "application/json",
                            "text": json.dumps(
                                {"model": "claude-3-haiku-20240307", "messages": []}
                            ),
                        },
                    },
                    "response": {
                        "status": 200,
                        "headers": [
                            {"name": "content-type", "value": "application/json"}
                        ],
                        "content": {"text": '{"ok":true}'},
                    },
                }
            ],
        }
    }
    p = tmp_path / "sample.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    return p


def test_load_flows_har(tmp_path: Path):
    p = make_har(tmp_path)
    flows = load_flows(p)
    assert len(flows) == 1
    f = flows[0]
    assert f["provider"] == "anthropic"
    assert f["model"].startswith("claude-3")
    assert f["latency_ms"] == 123
