from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from lifesaver_lite_llm.core.parser import _hash_content as _hhash  # type: ignore
from lifesaver_lite_llm.core.parser import _provider_from_host  # type: ignore
from lifesaver_lite_llm.core.parser import _session_id  # type: ignore
from lifesaver_lite_llm.core.templates import normalize_prompt


def _get(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10
) -> bytes:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    data = _get(url, headers=headers, timeout=timeout)
    return json.loads(data.decode("utf-8", errors="replace"))


def _ts_from_epoch(ts: Optional[float]) -> Optional[str]:
    if not ts:
        return None
    try:
        return datetime.utcfromtimestamp(ts).isoformat()
    except Exception:
        return None


def _build_record(flow: dict, base: str, headers: Dict[str, str]) -> dict:
    f_id = flow.get("id")
    req = flow.get("request") or {}
    resp = flow.get("response") or {}
    method = req.get("method")
    host = req.get("host")
    path = req.get("path")
    url = f"{req.get('scheme','http')}://{host}{path}"
    status = int(resp.get("status_code") or 0)
    # Fetch bodies
    req_body = ""
    resp_body = ""
    try:
        req_body = _get(
            urljoin(base, f"/flows/{f_id}/request/content.data"), headers=headers
        ).decode("utf-8", errors="replace")
    except Exception:
        req_body = ""
    try:
        resp_body = _get(
            urljoin(base, f"/flows/{f_id}/response/content.data"), headers=headers
        ).decode("utf-8", errors="replace")
    except Exception:
        resp_body = ""
    # Timestamps / latency
    ts_start = _ts_from_epoch((req or {}).get("timestamp_start"))
    ts_end = _ts_from_epoch((resp or {}).get("timestamp_end"))
    latency_ms = 0
    try:
        if req.get("timestamp_start") and resp.get("timestamp_end"):
            latency_ms = int((resp["timestamp_end"] - req["timestamp_start"]) * 1000)
    except Exception:
        latency_ms = 0
    # Headers JSON strings
    try:
        req_headers = json.dumps({k.lower(): v for k, v in (req.get("headers") or [])})
    except Exception:
        req_headers = "{}"
    try:
        resp_headers = json.dumps(
            {k.lower(): v for k, v in (resp.get("headers") or [])}
        )
    except Exception:
        resp_headers = "{}"

    model = ""
    try:
        body_json = json.loads(req_body) if req_body else None
        if isinstance(body_json, dict):
            model = (
                body_json.get("model")
                or body_json.get("model_id")
                or (body_json.get("parameters") or {}).get("model")
                or ""
            )
    except Exception:
        pass
    provider = _provider_from_host(host or "")
    # Session id using request headers
    hdrs_map = {}
    try:
        hdrs_map = {k.lower(): v for k, v in (req.get("headers") or [])}
    except Exception:
        hdrs_map = {}
    session_id = _session_id(hdrs_map)
    template_key = _hhash(normalize_prompt(req_body) if req_body else "")[:8]
    content_hash = _hhash(method or "", url, req_body or "")
    return {
        "ts_start": ts_start,
        "ts_end": ts_end,
        "method": method,
        "url": url,
        "host": host,
        "path": path,
        "status": status,
        "provider": provider,
        "model": model,
        "remote_flow_id": f_id,
        "req_headers": req_headers,
        "req_body": req_body[:200000],
        "resp_headers": resp_headers,
        "resp_body": resp_body[:200000],
        "tokens_in": 0,
        "tokens_out": 0,
        "latency_ms": latency_ms,
        "session_id": session_id,
        "template_key": template_key,
        "content_hash": content_hash,
        "raw": json.dumps(flow, ensure_ascii=False),
    }


def follow_mitmweb(
    base_url: str,
    db,
    interval_sec: float = 2.0,
    cookie: Optional[str] = None,
    stop_after: Optional[int] = None,
    status_path: Optional[str] = None,
):
    """
    Poll mitmweb REST API and ingest new flows into DB.
    - base_url: e.g., http://localhost:8081
    - cookie: optional 'Cookie' header value for authenticated instances
    - stop_after: optional max iterations for testing
    """
    base = base_url.rstrip("/")
    headers = {"Accept": "application/json"}
    if cookie:
        headers["Cookie"] = cookie
    seen: set[str] = set()
    iters = 0
    total_ingested = 0
    while True:
        iters += 1
        try:
            data = _json(urljoin(base, "/flows.json"), headers=headers)
            flows = data if isinstance(data, list) else []
            new_records: List[dict] = []
            for f in flows:
                fid = f.get("id")
                if not fid or fid in seen:
                    continue
                rec = _build_record(f, base, headers)
                new_records.append(rec)
                seen.add(fid)
            if new_records:
                inserted = db.ingest_flows(new_records)
                total_ingested += inserted
        except Exception:
            # swallow errors to keep running; consider logging
            pass
        # write status
        if status_path:
            try:
                with open(status_path, "w", encoding="utf-8") as fp:
                    json.dump(
                        {
                            "base_url": base,
                            "last_poll_epoch": time.time(),
                            "last_poll_iso": datetime.utcnow().isoformat(),
                            "seen_count": len(seen),
                            "total_ingested": total_ingested,
                            "interval_sec": interval_sec,
                        },
                        fp,
                        ensure_ascii=False,
                    )
            except Exception:
                pass
        if stop_after and iters >= stop_after:
            break
        time.sleep(interval_sec)
