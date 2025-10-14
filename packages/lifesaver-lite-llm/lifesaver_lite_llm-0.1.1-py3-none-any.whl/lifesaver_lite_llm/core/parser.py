from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from .templates import normalize_prompt


def _coerce_ts(value: Any) -> str:
    if value is None:
        return datetime.utcnow().isoformat()
    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(value)).isoformat()
        except Exception:
            return datetime.utcnow().isoformat()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        except Exception:
            return value
    return datetime.utcnow().isoformat()


def _text_from_record(rec: Dict[str, Any]) -> str:
    # Try likely keys for input prompt
    for k in ("prompt", "input", "user_input", "request", "messages"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v
        if k == "messages" and isinstance(v, list):
            # concatenate user/assistant roles
            chunks = []
            for m in v:
                role = m.get("role", "") if isinstance(m, dict) else ""
                content = m.get("content", "") if isinstance(m, dict) else ""
                if isinstance(content, list):
                    # Anthropic messages can be list of content blocks
                    text = " ".join(
                        c.get("text", "") if isinstance(c, dict) else str(c)
                        for c in content
                    )
                else:
                    text = str(content)
                chunks.append(f"[{role}] {text}".strip())
            if chunks:
                return "\n".join(chunks)
    return ""


def _output_from_record(rec: Dict[str, Any]) -> str:
    for k in ("completion", "output", "response", "assistant_output"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _int_safe(obj: Any, *keys: str) -> int:
    for k in keys:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, (int, float)):
            return int(v)
    return 0


def normalize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    usage = rec.get("usage", {}) if isinstance(rec.get("usage"), dict) else {}
    metrics = rec.get("metrics", {}) if isinstance(rec.get("metrics"), dict) else {}
    model = (
        rec.get("model")
        or rec.get("model_id")
        or rec.get("parameters", {}).get("model")
    )
    input_text = _text_from_record(rec)
    output_text = _output_from_record(rec)
    tokens_in = _int_safe(usage, "input_tokens", "prompt_tokens")
    tokens_out = _int_safe(usage, "output_tokens", "completion_tokens")
    latency_ms = _int_safe(metrics, "latency_ms", "latency")
    ts = _coerce_ts(rec.get("timestamp") or rec.get("created_at") or rec.get("time"))
    raw = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
    content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return {
        "ts": ts,
        "model": str(model) if model else "",
        "input_text": input_text,
        "output_text": output_text,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency_ms,
        "content_hash": content_hash,
        "raw": raw,
    }


def _records_from_har(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Very lightweight HAR -> normalized records
    # Expects https://w3c.github.io/web-performance/specs/HAR/Overview.html format
    log = data.get("log", {}) if isinstance(data, dict) else {}
    entries = log.get("entries", []) if isinstance(log, dict) else []
    out: List[Dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        req = e.get("request", {}) if isinstance(e.get("request"), dict) else {}
        _resp = e.get("response", {}) if isinstance(e.get("response"), dict) else {}
        started = e.get("startedDateTime")
        total_time_ms = e.get("time")
        method = req.get("method")
        url = req.get("url", "")
        if method != "POST":
            continue
        post = req.get("postData", {}) if isinstance(req.get("postData"), dict) else {}
        mime = (post.get("mimeType") or "").lower()
        text = post.get("text") or ""
        body_json = None
        if "json" in mime or mime.endswith("/json"):
            try:
                body_json = json.loads(text)
            except Exception:
                body_json = None
        # Build a record-like object geared for normalize_record
        rec: Dict[str, Any] = {}
        if isinstance(body_json, dict):
            rec.update(body_json)
        # Try to populate model if missing
        if not rec.get("model"):
            # Common provider-specific hints
            # Anthropics often uses 'model' in body; fallback to URL path
            if "anthropic" in url:
                # Nothing reliable in URL; leave empty if not in body
                rec.setdefault("model", "")
            elif (
                "openai" in url
                or "openrouter" in url
                or "groq" in url
                or "mistral" in url
            ):
                rec.setdefault("model", "")
        # Timestamp and latency
        if started:
            rec.setdefault("timestamp", started)
        if isinstance(total_time_ms, (int, float)):
            rec.setdefault("metrics", {"latency_ms": int(total_time_ms)})
        # If no messages but raw text exists, store it as 'input'
        if "messages" not in rec and isinstance(text, str) and text:
            rec.setdefault("input", text[:10000])  # guard against very large payloads
        out.append(normalize_record(rec))
    return out


def load_requests(path: Path) -> List[Dict[str, Any]]:
    # Support native .mitm flow files exported/recorded by mitmproxy
    suffix = path.suffix.lower()
    if suffix == ".mitm" or suffix == ".flow" or suffix == ".flows":
        try:
            from mitmproxy.io import FlowReader  # type: ignore
        except Exception as e:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "mitmproxy is required to parse .mitm flow files. pip install mitmproxy"
            ) from e
        out: List[Dict[str, Any]] = []
        with open(path, "rb") as fp:
            reader = FlowReader(fp)
            for flow in reader.stream():
                try:
                    req = flow.request
                    _resp = getattr(flow, "response", None)
                    rec: Dict[str, Any] = {}
                    # Timestamp
                    if getattr(flow, "timestamp_start", None):
                        rec["timestamp"] = datetime.utcfromtimestamp(
                            flow.timestamp_start
                        ).isoformat()
                    # Latency
                    if getattr(flow, "timestamp_end", None) and getattr(
                        flow, "timestamp_start", None
                    ):
                        rec["metrics"] = {
                            "latency_ms": int(
                                (flow.timestamp_end - flow.timestamp_start) * 1000
                            )
                        }
                    # Request body
                    body_text = ""
                    try:
                        body_text = req.get_text(strict=False) or ""
                    except Exception:
                        body_text = ""
                    # Attempt JSON decode
                    body_json = None
                    if body_text:
                        try:
                            body_json = json.loads(body_text)
                        except Exception:
                            body_json = None
                    if isinstance(body_json, dict):
                        rec.update(body_json)
                    else:
                        if body_text:
                            rec.setdefault("input", body_text[:10000])
                    # Model hint
                    if not rec.get("model"):
                        rec.setdefault("model", "")
                    out.append(normalize_record(rec))
                except Exception:
                    continue
        return out

    # JSON/HTTP Archive inputs
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    # Detect HAR export from mitmweb
    if (
        isinstance(data, dict)
        and isinstance(data.get("log"), dict)
        and isinstance(data["log"].get("entries"), list)
    ):
        return _records_from_har(data)
    # Generic list or envelope {data: [...]} of request-like objects
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        records = data["data"]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(
            'Unsupported JSON format. Provide a list of request objects, {"data": [...]}, or a HAR export.'
        )
    return [normalize_record(r) for r in records if isinstance(r, dict)]


# Enriched flow ingestion for HAR and .mitm
_PROVIDER_HOST_MAP = {
    "api.anthropic.com": "anthropic",
    "api.openai.com": "openai",
    "openrouter.ai": "openrouter",
    "api.groq.com": "groq",
    "api.mistral.ai": "mistral",
}


def _headers_to_json(hlist) -> str:
    try:
        if isinstance(hlist, dict):
            return json.dumps(hlist, ensure_ascii=False)
        if isinstance(hlist, list):
            # har format: [{name, value}]
            return json.dumps(
                {
                    (x.get("name") or "").lower(): x.get("value")
                    for x in hlist
                    if isinstance(x, dict)
                },
                ensure_ascii=False,
            )
        return json.dumps({}, ensure_ascii=False)
    except Exception:
        return json.dumps({}, ensure_ascii=False)


def _hash_content(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        if p:
            h.update(p.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _session_id(headers: Dict[str, Any], peer: str = "") -> str:
    auth = (headers.get("authorization") or headers.get("x-api-key") or "").strip()
    ua = (headers.get("user-agent") or "").strip()
    base = f"{auth}|{ua}|{peer}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def _provider_from_host(host: str) -> str:
    host = (host or "").lower()
    for key, prov in _PROVIDER_HOST_MAP.items():
        if key in host:
            return prov
    return ""


def load_flows(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    out: List[Dict[str, Any]] = []
    if suffix == ".har":
        data = json.loads(path.read_text(encoding="utf-8"))
        log = data.get("log", {}) if isinstance(data, dict) else {}
        entries = log.get("entries", []) if isinstance(log, dict) else []
        for e in entries:
            if not isinstance(e, dict):
                continue
            req = e.get("request", {}) if isinstance(e.get("request"), dict) else {}
            resp = e.get("response", {}) if isinstance(e.get("response"), dict) else {}
            started = e.get("startedDateTime")
            total_time_ms = int(e.get("time") or 0)
            method = req.get("method")
            url = req.get("url", "")
            headers_list = req.get("headers") or []
            hdrs = {
                (h.get("name") or "").lower(): h.get("value")
                for h in headers_list
                if isinstance(h, dict)
            }
            host = ""
            path_s = ""
            try:
                from urllib.parse import urlparse

                p = urlparse(url)
                host = p.netloc
                path_s = p.path
            except Exception:
                pass
            provider = _provider_from_host(host)
            post = (
                req.get("postData", {}) if isinstance(req.get("postData"), dict) else {}
            )
            mime = (post.get("mimeType") or "").lower()
            text = post.get("text") or ""
            body_json = None
            if "json" in mime or mime.endswith("/json"):
                try:
                    body_json = json.loads(text)
                except Exception:
                    body_json = None
            model = None
            if isinstance(body_json, dict):
                model = (
                    body_json.get("model")
                    or body_json.get("model_id")
                    or body_json.get("parameters", {}).get("model")
                )
            status = int(resp.get("status") or 0)
            # content-type header if present (unused in current logic)
            _resp_ct_placeholder = ""
            try:
                rh = {
                    (h.get("name") or "").lower(): h.get("value")
                    for h in (resp.get("headers") or [])
                }
                _resp_ct = rh.get("content-type", "")
            except Exception:
                pass
            # Response body in HAR may be encoded; we keep placeholder unless present
            resp_text = (resp.get("content", {}) or {}).get("text") or ""
            # Build flow record
            headers_json = _headers_to_json(headers_list)
            resp_headers_json = _headers_to_json(resp.get("headers") or [])
            # Compute a short template key for grouping similar prompts
            template_key = _hash_content(normalize_prompt(text) if text else "")[:8]
            sess = _session_id(hdrs)
            out.append(
                {
                    "ts_start": started,
                    "ts_end": None,
                    "method": method,
                    "url": url,
                    "host": host,
                    "path": path_s,
                    "status": status,
                    "provider": provider,
                    "model": model or "",
                    "remote_flow_id": None,
                    "req_headers": headers_json,
                    "req_body": text[:200000],
                    "resp_headers": resp_headers_json,
                    "resp_body": resp_text[:200000],
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "latency_ms": total_time_ms,
                    "session_id": sess,
                    "template_key": template_key,
                    "content_hash": _hash_content(method or "", url, text or ""),
                    "raw": json.dumps(e, ensure_ascii=False),
                }
            )
        return out

    if suffix in {".mitm", ".flow", ".flows"}:
        try:
            from mitmproxy.io import FlowReader  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "mitmproxy is required to parse .mitm flow files. pip install mitmproxy"
            ) from e
        with open(path, "rb") as fp:
            reader = FlowReader(fp)
            for flow in reader.stream():
                try:
                    req = flow.request
                    resp = getattr(flow, "response", None)
                    ts_start = None
                    ts_end = None
                    if getattr(req, "timestamp_start", None):
                        ts_start = datetime.utcfromtimestamp(
                            req.timestamp_start
                        ).isoformat()
                    if getattr(resp, "timestamp_end", None):
                        ts_end = datetime.utcfromtimestamp(
                            resp.timestamp_end
                        ).isoformat()
                    latency_ms = 0
                    if getattr(flow, "timestamp_start", None) and getattr(
                        flow, "timestamp_end", None
                    ):
                        latency_ms = int(
                            (flow.timestamp_end - flow.timestamp_start) * 1000
                        )
                    method = req.method
                    url = req.url
                    host = req.host
                    path_s = req.path
                    status = int(resp.status_code) if resp else 0
                    headers = {k.lower(): v for k, v in req.headers.items(multi=True)}
                    headers_json = json.dumps(
                        {k: v for k, v in headers.items()}, ensure_ascii=False
                    )
                    resp_headers_json = json.dumps(
                        {
                            k.lower(): v
                            for k, v in (resp.headers.items(multi=True) if resp else [])
                        },
                        ensure_ascii=False,
                    )
                    body_text = ""
                    try:
                        body_text = req.get_text(strict=False) or ""
                    except Exception:
                        body_text = ""
                    resp_text = ""
                    try:
                        if resp:
                            resp_text = resp.get_text(strict=False) or ""
                    except Exception:
                        resp_text = ""
                    model = None
                    try:
                        bj = json.loads(body_text) if body_text else None
                        if isinstance(bj, dict):
                            model = (
                                bj.get("model")
                                or bj.get("model_id")
                                or bj.get("parameters", {}).get("model")
                            )
                    except Exception:
                        pass
                    provider = _provider_from_host(host)
                    sess = _session_id(
                        headers, peer=str(getattr(flow.client_conn, "peername", ""))
                    )
                    template_key = _hash_content(
                        normalize_prompt(body_text) if body_text else ""
                    )[:8]
                    out.append(
                        {
                            "ts_start": ts_start,
                            "ts_end": ts_end,
                            "method": method,
                            "url": url,
                            "host": host,
                            "path": path_s,
                            "status": status,
                            "provider": provider,
                            "model": model or "",
                            "remote_flow_id": None,
                            "req_headers": headers_json,
                            "req_body": (body_text or "")[:200000],
                            "resp_headers": resp_headers_json,
                            "resp_body": (resp_text or "")[:200000],
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "latency_ms": latency_ms,
                            "session_id": sess,
                            "template_key": template_key,
                            "content_hash": _hash_content(
                                method or "", url, body_text or ""
                            ),
                            "raw": "{}",
                        }
                    )
                except Exception:
                    continue
        return out

    raise ValueError("Unsupported flow format: expected .har or .mitm")
