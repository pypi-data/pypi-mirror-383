from __future__ import annotations

import os
from pathlib import Path
import json
from typing import Any, Dict
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import secrets as _secrets
from typing import Optional

from lifesaver_lite_llm.core.storage import Database
from lifesaver_lite_llm.core.analytics import analyze_requests
from lifesaver_lite_llm.agent.orchestrator import load_providers_config
from lifesaver_lite_llm.core.suggestions import build_suggestions
from lifesaver_lite_llm.core.templates import normalize_prompt
from lifesaver_lite_llm.core.techniques import extract_prompting_techniques
import hashlib
from lifesaver_lite_llm.core.redact import redact_text
from lifesaver_lite_llm.core.tags import tag_flow


DB_PATH = Path(os.environ.get("DB_PATH", "data/analysis.db"))
PROVIDERS_PATH = Path(os.environ.get("PROVIDERS_PATH", "configs/providers.json"))
STATUS_PATH = Path(os.environ.get("MITMWEB_STATUS_PATH", "/data/mitmweb_status.json"))
UPLOAD_STATUS_PATH = Path("/data/upload_status.json")

app = FastAPI(title="Lifesaver Lite LLM Dashboard")

# Static assets (vendored) for offline use
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Basic Auth
_BASIC_USER = os.environ.get("DASH_BASIC_USER")
_BASIC_PASS = os.environ.get("DASH_BASIC_PASS")


def require_auth():
    if not _BASIC_USER or not _BASIC_PASS:
        return True  # auth disabled
    # FastAPI's HTTPBasic is optional to avoid adding extra deps here; parse header manually
    import base64
    from starlette.requests import Request as StarletteRequest

    async def _inner(request: StarletteRequest):
        auth = request.headers.get("authorization") or request.headers.get(
            "Authorization"
        )
        if not auth or not auth.lower().startswith("basic "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )
        try:
            decoded = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8")
            user, pwd = decoded.split(":", 1)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )
        if not (
            _secrets.compare_digest(user, _BASIC_USER)
            and _secrets.compare_digest(pwd, _BASIC_PASS)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )
        return True

    return Depends(_inner)


def compute_summary() -> Dict[str, Any]:
    rows = load_rows()
    providers = load_providers_config(PROVIDERS_PATH)
    summary = analyze_requests(rows)
    suggestions = build_suggestions(rows, providers)
    # Prompting techniques summary (category counts)
    techniques = extract_prompting_techniques([r.get("input_text", "") for r in rows])
    cat_counts = {
        k: v.get("count", 0) for k, v in techniques.get("categories", {}).items()
    }
    return {
        "summary": summary,
        "suggestions": suggestions,
        "technique_counts": cat_counts,
    }


def compute_insights() -> list[str]:
    rows = load_rows()
    if not rows:
        return ["No data available yet."]
    dag = build_dag(rows)
    # Top nodes by count
    nodes = sorted(dag["nodes"], key=lambda n: n.get("count", 0), reverse=True)
    top_templates = [n for n in nodes if n.get("type") == "template"][:3]
    top_models = [n for n in nodes if n.get("type") == "model"][:3]
    # Latency observations
    lat = [
        int(r.get("latency_ms", 0))
        for r in rows
        if isinstance(r.get("latency_ms"), (int, float))
    ]
    avg_lat = sum(lat) / len(lat) if lat else 0
    # Token observations
    ti = [int(r.get("tokens_in", 0)) for r in rows]
    to = [int(r.get("tokens_out", 0)) for r in rows]
    avg_ti = sum(ti) / len(ti) if ti else 0
    avg_to = sum(to) / len(to) if to else 0
    insights: list[str] = []
    if top_templates:
        insights.append(
            f"Dominant templates: {', '.join(t['label'][:40] + ('…' if len(t['label'])>40 else '') for t in top_templates)}"
        )
    if top_models:
        insights.append(
            f"Most used models: {', '.join(m['label'] for m in top_models)}"
        )
    insights.append(
        f"Typical prompt size/output: ~{avg_ti:.0f} in / ~{avg_to:.0f} out tokens; Avg latency ~{avg_lat:.0f} ms"
    )
    # Skeleton projection
    multimodal = any(
        "multimodal" in (r.get("output_text", "") + r.get("raw", "")).lower()
        for r in rows
    )
    skeleton = "Template → Model → Output(Text)"
    if multimodal:
        skeleton = "Template → Model → Output(Multimodal)"
    insights.append(f"Agent skeleton (observed DAG): {skeleton}")
    # Workflow tagging distribution
    all_tags: dict[str, int] = {}
    for r in rows:
        for t in tag_flow(r):
            all_tags[t] = all_tags.get(t, 0) + 1
    if all_tags:
        tags_sorted = sorted(all_tags.items(), key=lambda kv: kv[1], reverse=True)
        insights.append(
            "Workflow tags: " + ", ".join(f"{k} ({v})" for k, v in tags_sorted)
        )
    return insights


def load_flows_raw() -> list[dict[str, Any]]:
    db = Database(DB_PATH)
    db.init()
    return db.fetch_flows()


def load_rows() -> list[dict[str, Any]]:
    db = Database(DB_PATH)
    db.init()
    flows = db.fetch_flows()
    if flows:
        rows = []
        for f in flows:
            rows.append(
                {
                    "id": f.get("id"),
                    "ts": f.get("ts_start") or f.get("ts_end") or "",
                    "model": f.get("model") or "",
                    "input_text": f.get("req_body") or "",
                    "output_text": f.get("resp_body") or "",
                    "tokens_in": int(f.get("tokens_in") or 0),
                    "tokens_out": int(f.get("tokens_out") or 0),
                    "latency_ms": int(f.get("latency_ms") or 0),
                    "raw": f.get("raw") or "",
                    "provider": f.get("provider") or "",
                    "status": int(f.get("status") or 0),
                }
            )
        return rows
    return db.fetch_all()


def template_key(prompt: str) -> str:
    if not prompt:
        return ""
    norm = normalize_prompt(prompt)
    h = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:8]
    return f"tpl:{h}"


def build_dag(rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Aggregate a lightweight DAG: Template -> Model -> {Tool?, Retrieval?} -> OutputType
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str], int] = {}

    def add_node(nid: str, label: str, ntype: str):
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label, "type": ntype, "count": 0}
        nodes[nid]["count"] += 1

    def add_edge(a: str, b: str):
        edges[(a, b)] = edges.get((a, b), 0) + 1

    for r in rows:
        tpl_id = template_key(r.get("input_text", "")) or "tpl:unknown"
        tpl_label = (normalize_prompt(r.get("input_text", "")) or "<no prompt>")[:80]
        model_id = f"model:{r.get('model') or 'unknown'}"
        out_text = (r.get("output_text") or "") + " " + (r.get("raw") or "")
        out_type = (
            "multimodal"
            if any(k in out_text.lower() for k in ["image", "vision", "audio"])
            else "text"
        )
        out_id = f"out:{out_type}"

        add_node(tpl_id, tpl_label, "template")
        add_node(model_id, r.get("model") or "unknown", "model")
        add_node(out_id, out_type, "output")
        # optional nodes based on tags
        tags = tag_flow(r)
        maybe_mid = []
        if "tooling" in tags:
            tool_id = "tool:call"
            add_node(tool_id, "Tool Call", "tool")
            maybe_mid.append(tool_id)
        if "retrieval" in tags:
            ret_id = "retrieval:op"
            add_node(ret_id, "Retrieval", "retrieval")
            maybe_mid.append(ret_id)
        add_edge(tpl_id, model_id)
        if maybe_mid:
            for mid in maybe_mid:
                add_edge(model_id, mid)
                add_edge(mid, out_id)
        else:
            add_edge(model_id, out_id)

    return {
        "nodes": list(nodes.values()),
        "edges": [
            {"source": a, "target": b, "weight": w} for (a, b), w in edges.items()
        ],
    }


@app.get("/api/summary")
def api_summary(_auth=require_auth()):
    return JSONResponse(compute_summary())


@app.get("/api/flows")
def api_flows(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    model: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[int] = None,
    tag: Optional[str] = None,
    since: Optional[str] = None,
    redact: str = "0",
    _auth=require_auth(),
):
    rows = load_rows()

    # filter
    def ok(r: dict) -> bool:
        if model and (r.get("model") or "").lower() != model.lower():
            return False
        if provider and (r.get("provider") or "").lower() != provider.lower():
            return False
        if status is not None and int(r.get("status") or 0) != int(status):
            return False
        if tag:
            if tag.lower() not in [t.lower() for t in tag_flow(r)]:
                return False
        if since:
            s = since.strip().lower()
            cutoff_iso = None
            if s.startswith("now-"):
                try:
                    amt = s.split("now-", 1)[1]
                    unit = amt[-1]
                    num = int(amt[:-1])
                    now = datetime.now(timezone.utc)
                    if unit == "m":
                        dt = now - timedelta(minutes=num)
                    elif unit == "h":
                        dt = now - timedelta(hours=num)
                    elif unit == "d":
                        dt = now - timedelta(days=num)
                    else:
                        dt = now
                    cutoff_iso = dt.isoformat()
                except Exception:
                    cutoff_iso = None
            else:
                cutoff_iso = s
            if cutoff_iso:
                return (r.get("ts") or "") >= cutoff_iso
            return True
        return True

    rows_f = [r for r in rows if ok(r)]
    total = len(rows_f)
    page = rows_f[offset : offset + limit]
    # attach tags and template key
    out = []
    red = str(redact).lower()
    redact_body = red in {"1", "true", "yes", "body", "all"}
    redact_headers = red in {"all", "headers"}
    for r in page:
        r2 = dict(r)
        r2["tags"] = tag_flow(r)
        r2["template_key"] = template_key(r.get("input_text", ""))
        if redact_body:
            try:
                r2["input_text"] = redact_text(r2.get("input_text") or "")
            except Exception:
                pass
        if redact_headers:
            # headers not present in rows projection; kept for completeness if extended
            pass
        out.append(r2)
    return JSONResponse({"total": total, "offset": offset, "limit": limit, "data": out})


@app.get("/api/graph")
def api_graph(_auth=require_auth()):
    rows = load_rows()
    return JSONResponse(build_dag(rows))


@app.get("/api/techniques")
def api_techniques(_auth=require_auth()):
    rows = load_rows()
    tech = extract_prompting_techniques([r.get("input_text", "") for r in rows])
    return JSONResponse(tech)


@app.get("/")
def index(_auth=require_auth()):
    data = compute_summary()
    s = data["summary"]
    sug = data["suggestions"]
    by_model = "".join(
        f"<li><code>{m or 'unknown'}</code>: {c}</li>"
        for m, c in s["by_model"].most_common()
    )
    top_tokens = "".join(
        f"<li><code>{t}</code>: {n}</li>" for t, n in s["top_tokens"][:20]
    )
    tips = "".join(f"<li>{t}</li>" for t in sug["tips"]) or "<li>No tips yet</li>"
    insights = "".join(f"<li>{line}</li>" for line in compute_insights())
    rules = (
        "".join(f"<li>{r}</li>" for r in sug["routing_rules"])
        or "<li>No routing rules</li>"
    )
    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset=\"utf-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>Lifesaver Lite LLM Dashboard</title>
      <style>
        body {{ font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif; margin: 24px; }}
        code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
        .card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
        h1 {{ margin-top: 0; }}
        h2 {{ margin: 8px 0 12px; font-size: 1.1rem; }}
        ul {{ margin: 0; padding-left: 18px; }}
        .nav a {{ margin-right: 12px; }}
      </style>
    </head>
    <body>
      <h1>Lifesaver Lite LLM Dashboard</h1>
      <p class="nav">
        <a href="/flows">Flows</a>
        <a href="/timeline">Timeline</a>
        <a href="/graph">Graph</a>
        <a href="/techniques">Techniques</a>
      </p>
      <div id="status" style="margin:8px 0; padding:8px; border:1px solid #e5e7eb; border-radius:8px; background:#fafafa; font-size: 0.95rem">Loading status…</div>
      <script>
        function refreshStatus(){{
          fetch('/api/status').then(r=>r.json()).then(s=>{{
            const el=document.getElementById('status');
            const mode = s.mode || 'idle';
            const lf = s.last_flow_ts || '—';
            const lr = s.last_request_ts || '—';
            const mu = s.mitmweb && s.mitmweb.base_url ? s.mitmweb.base_url : '';
            const lp = s.mitmweb && s.mitmweb.last_poll_iso ? s.mitmweb.last_poll_iso : '';
            el.innerHTML = `Mode: <b>$${{mode}}</b>$${{mu?` · mitmweb: <code>$${{mu}}</code>`:''}}$${{lp?` · last poll: ${{lp}}`:''}} · last flow: $${{lf}} · legacy last request: $${{lr}} · flows: $${{s.flows_count}} · records: $${{s.requests_count}}`;
          }}).catch(()=>{{document.getElementById('status').innerText='Status unavailable';}});
        }}
        refreshStatus();
        setInterval(refreshStatus, 5000);
      </script>
      <p>Total: <b>{s['total']}</b> | Avg in: <b>{s['avg_tokens_in']:.1f}</b> | Avg out: <b>{s['avg_tokens_out']:.1f}</b> | Avg latency: <b>{s['avg_latency_ms']:.1f} ms</b></p>
      <div class="grid">
        <div class="card">
          <h2>By Model</h2>
          <ul>{by_model}</ul>
        </div>
        <div class="card">
          <h2>Top Tokens</h2>
          <ul>{top_tokens}</ul>
        </div>
        <div class="card">
          <h2>Routing Suggestions</h2>
          <ul>{rules}</ul>
        </div>
        <div class="card">
          <h2>Optimization Tips</h2>
          <ul>{tips}</ul>
        </div>
        <div class="card">
          <h2>Analysis & Projection</h2>
          <ul>{insights}</ul>
        </div>
        <div class="card">
          <h2>Prompting Techniques</h2>
          <ul>{''.join(f'<li>{k}: {v}</li>' for k, v in data.get('technique_counts', {}).items()) or '<li>No techniques detected</li>'}</ul>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/flows")
def flows(
    offset: int = 0,
    limit: int = 100,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[int] = None,
    tag: Optional[str] = None,
    since: Optional[str] = None,
    reveal: int = 0,
    _auth=require_auth(),
):
    rows = api_flows(
        offset=0,
        limit=1000000,
        model=model,
        provider=provider,
        status=status,
        tag=tag,
        since=since,
        redact=(0 if reveal else 1),
    ).body
    import json as _json

    rows_parsed = _json.loads(rows.decode("utf-8"))
    page = rows_parsed.get("data", [])
    items = []
    for r in page:
        prompt = r.get("input_text", "") or ""
        if not reveal:
            prompt = redact_text(prompt)
        items.append(
            f"<tr><td>{r.get('ts','')}</td><td>{r.get('model','')}</td><td>{r.get('tokens_in',0)}/{r.get('tokens_out',0)}</td><td>{r.get('latency_ms',0)} ms</td><td>{prompt.replace('<','&lt;')[:160]}</td><td>{', '.join(tag_flow(r))}</td></tr>"
        )
    html = f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Flows</title>
    <style>table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #e5e7eb;padding:6px;text-align:left}} .nav a{{margin-right:12px}}</style>
    </head><body>
    <p class="nav"><a href="/">Home</a> <a href="/timeline">Timeline</a> <a href="/graph">Graph</a></p>
    <h2>Flows</h2>
    <form method="get" style="margin-bottom:8px">
      <input name="provider" placeholder="provider" value="{provider or ''}" />
      <input name="model" placeholder="model" value="{model or ''}" />
      <input name="status" placeholder="status" value="{status or ''}" />
      <input name="tag" placeholder="tag" value="{tag or ''}" />
      <input name="since" placeholder="since ISO ts" value="{since or ''}" />
      <button>Filter</button>
      <label style="margin-left:8px"><input type="checkbox" name="reveal" value="1" {('checked' if reveal else '')}> reveal bodies</label>
    </form>
    <script>
      function reloadTable(){{
        const params = new URLSearchParams(window.location.search);
        if (!params.get('reveal')) {{ params.set('redact','1'); }} else {{ params.delete('redact'); }}
        fetch('/api/flows?'+params.toString()).then(r=>r.json()).then(j=>{{
          const tbody = document.querySelector('tbody');
          const rows = (j.data||[]).map(r=>{{
            const prompt = r.input_text||'';
            const tags = (r.tags||[]).join(', ');
            const link = r.id ? `<a href=\"/flow/$${{r.id}}\">details</a>` : '';
            return `<tr><td>$${{r.ts||''}}</td><td>$${{r.model||''}}</td><td>$${{r.tokens_in||0}}/$${{r.tokens_out||0}}</td><td>$${{r.latency_ms||0}} ms</td><td>$${{(prompt||'').slice(0,160).replaceAll('<','&lt;')}}</td><td>$${{tags}} $${{link?(' · '+link):''}}</td></tr>`;
          }}).join('');
          tbody.innerHTML = rows || '<tr><td colspan=\"6\">No data</td></tr>';
        }}).catch(() => {{}});
      }}
      setInterval(reloadTable, 5000);
    </script>
    <table>
    <thead><tr><th>TS</th><th>Model</th><th>Tokens in/out</th><th>Latency</th><th>Prompt</th><th>Tags</th></tr></thead>
    <tbody>{''.join(items) or '<tr><td colspan="6">No data</td></tr>'}</tbody>
    </table>
    </body></html>
    """
    return HTMLResponse(html)


@app.get("/api/flow/{flow_id}")
def api_flow(flow_id: int, _auth=require_auth()):
    db = Database(DB_PATH)
    db.init()
    rows = db.fetch_flows("id = ?", (flow_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Flow not found")
    return JSONResponse(rows[0])


@app.get("/flow/{flow_id}")
def flow_detail(flow_id: int, reveal: int = 0, _auth=require_auth()):
    db = Database(DB_PATH)
    db.init()
    rows = db.fetch_flows("id = ?", (flow_id,))
    if not rows:
        return HTMLResponse("<h3>Not found</h3>", status_code=404)
    f = rows[0]

    def esc(x: str) -> str:
        return (x or "").replace("<", "&lt;")

    reqb = f.get("req_body") or ""
    respb = f.get("resp_body") or ""
    if not reveal:
        reqb = redact_text(reqb)
        respb = redact_text(respb)
    html = f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Flow {flow_id}</title>
    <style>body{{font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;margin:24px}} pre{{white-space:pre-wrap;word-break:break-word;background:#f6f8fa;padding:12px;border-radius:8px}}</style>
    </head><body>
    <p class="nav"><a href="/">Home</a> <a href="/flows">Flows</a></p>
    <h2>Flow {flow_id}</h2>
    <p><b>Time</b> {esc(f.get('ts_start') or f.get('ts_end') or '')} · <b>Status</b> {f.get('status') or ''} · <b>Provider</b> {esc(f.get('provider') or '')} · <b>Model</b> {esc(f.get('model') or '')}</p>
    <p><b>Method</b> {esc(f.get('method') or '')} <b>URL</b> {esc(f.get('url') or '')}</p>
    <h3>Request Headers</h3>
    <pre>{esc(f.get('req_headers') if reveal else '<REDACTED_HEADERS>')}</pre>
    <h3>Request Body</h3>
    <pre>{esc(reqb)}</pre>
    <h3>Response Headers</h3>
    <pre>{esc(f.get('resp_headers') if reveal else '<REDACTED_HEADERS>')}</pre>
    <h3>Response Body</h3>
    <pre>{esc(respb)}</pre>
    <p><a href="/flow/{flow_id}?reveal={0 if reveal else 1}">{'Hide' if reveal else 'Reveal'} bodies</a></p>
    </body></html>
    """
    return HTMLResponse(html)


@app.get("/timeline")
def timeline(_auth=require_auth()):
    rows = load_rows()
    # Group into simple sessions by 2-minute gaps
    from datetime import datetime

    def parse_ts(ts: str) -> float:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    rows_sorted = sorted(rows, key=lambda r: r.get("ts", ""))
    sessions: list[list[dict[str, Any]]] = []
    cur: list[dict[str, Any]] = []
    last_ts = None
    for r in rows_sorted:
        t = parse_ts(r.get("ts", ""))
        if last_ts is None or (t - last_ts) <= 120:
            cur.append(r)
        else:
            if cur:
                sessions.append(cur)
            cur = [r]
        last_ts = t
    if cur:
        sessions.append(cur)

    blocks = []
    for i, sess in enumerate(sessions, 1):
        lis = []
        for r in sess:
            tpl = normalize_prompt(r.get("input_text", ""))[:120]
            lis.append(
                f"<li><b>{r.get('ts','')}</b> · <code>{r.get('model','')}</code> · {', '.join(tag_flow(r))}<br/><small>{tpl}</small></li>"
            )
        blocks.append(
            f"<div class='card'><h3>Session {i}</h3><ol>{''.join(lis)}</ol></div>"
        )

    html = f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Timeline</title>
    <style>body{{font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;margin:24px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}} .card{{border:1px solid #e5e7eb;border-radius:8px;padding:12px}} .nav a{{margin-right:12px}}</style>
    </head><body>
    <p class="nav"><a href="/">Home</a> <a href="/flows">Flows</a> <a href="/graph">Graph</a></p>
    <h2>Prompting Timeline</h2>
    <div class='grid'>{''.join(blocks) or '<p>No sessions.</p>'}</div>
    </body></html>
    """
    return HTMLResponse(html)


@app.get("/graph")
def graph(_auth=require_auth()):
    html = """
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'>
      <title>Graph</title>
      <style>body{font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;margin:24px} #cy{width:100%;height:75vh;border:1px solid #e5e7eb;border-radius:8px} .nav a{margin-right:12px}</style>
      <script src="/static/js/cytoscape.min.js"></script>
      <script src="/static/js/dagre.min.js"></script>
      <script src="/static/js/cytoscape-dagre.js"></script>
    </head>
    <body>
      <p class="nav"><a href="/">Home</a> <a href="/flows">Flows</a> <a href="/timeline">Timeline</a></p>
      <h2>Knowledge Graph / DAG</h2>
      <div id="cy"></div>
      <script>
        fetch('/api/graph').then(r=>r.json()).then(data=>{
          const nodes = data.nodes.map(n=>({ data: { id: n.id, label: n.label, type: n.type, count: n.count } }));
          const edges = data.edges.map(e=>({ data: { source: e.source, target: e.target, weight: e.weight } }));
          const cy = cytoscape({ container: document.getElementById('cy'), elements: { nodes, edges }, style: [
            { selector: 'node', style: { 'label': 'data(label)', 'text-wrap':'wrap','text-max-width': 200, 'font-size': 10, 'background-color': '#60a5fa' } },
            { selector: 'node[type="model"]', style: { 'background-color': '#34d399' } },
            { selector: 'node[type="output"]', style: { 'background-color': '#fbbf24' } },
            { selector: 'node[type="tool"]', style: { 'background-color': '#f472b6' } },
            { selector: 'node[type="retrieval"]', style: { 'background-color': '#a78bfa' } },
            { selector: 'edge', style: { 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'width': 'mapData(weight, 1, 10, 1, 6)', 'line-color':'#9ca3af', 'target-arrow-color':'#9ca3af' } }
          ], layout: { name: 'dagre', padding: 10 } });
        }).catch(err=>{ document.getElementById('cy').innerText = 'Failed to load graph: '+err; });
      </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/techniques")
def techniques_page(_auth=require_auth()):
    html = """
    <!doctype html>
    <html>
    <head>
      <meta charset='utf-8'>
      <title>Techniques</title>
      <style>body{font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;margin:24px} .nav a{margin-right:12px} .card{border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin-bottom:12px}</style>
    </head>
    <body>
      <p class=\"nav\"><a href=\"/\">Home</a> <a href=\"/flows\">Flows</a> <a href=\"/timeline\">Timeline</a> <a href=\"/graph\">Graph</a></p>
      <h2>Prompting Techniques, Workflows, and Templates</h2>
      <div id=\"root\">Loading…</div>
      <script>
        fetch('/api/techniques').then(r=>r.json()).then(data=>{
          const root = document.getElementById('root');
          const cats = data.categories || {};
          const order = Object.entries(cats).sort((a,b)=> (b[1].count||0)-(a[1].count||0));
          let html = '';
          for (const [cid, cat] of order) {
            html += `<div class=\"card\"><h3>$${{cat.label}} <small>($${{cat.count}})</small></h3><ul>`;
            for (const t of (cat.techniques||[])) {
              const ex = (t.examples||[]).map(s=>`<li><code>$${{s.replaceAll('<','&lt;')}}</code></li>`).join('');
              const conf = t.confidence != null ? ` <small>(conf $${{t.confidence}})</small>` : '';
              html += `<li><b>$${{t.label}}</b> — $${{t.count}}$${{conf}}<details><summary>examples</summary><ul>$${{ex || '<li>—</li>'}}</ul></details></li>`;
            }
            html += '</ul></div>';
          }
          const templates = (data.templates||[]).slice(0, 20);
          html += `<div class=\"card\"><h3>Top Templates</h3><ol>`;
          for (const tpl of templates) {
            html += `<li><code>$${{tpl.template.replaceAll('<','&lt;')}}</code> — $${{tpl.occurrences}}</li>`;
          }
          html += `</ol></div>`;
          root.innerHTML = html || '<p>No techniques detected.</p>';
        }).catch(err=>{
          document.getElementById('root').innerText = 'Failed to load: '+err;
        });
      </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def compute_status() -> Dict[str, Any]:
    db = Database(DB_PATH)
    db.init()
    flows = db.fetch_flows()
    last_flow_ts = None
    if flows:
        last = flows[-1]
        last_flow_ts = last.get("ts_start") or last.get("ts_end")
    # legacy requests
    reqs = db.fetch_all()
    last_req_ts = reqs[-1]["ts"] if reqs else None
    mitm_status = None
    try:
        if STATUS_PATH.exists():
            mitm_status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except Exception:
        mitm_status = None
    upload_status = None
    try:
        if UPLOAD_STATUS_PATH.exists():
            upload_status = json.loads(UPLOAD_STATUS_PATH.read_text(encoding="utf-8"))
    except Exception:
        upload_status = None
    mode = (
        "live"
        if mitm_status
        else (upload_status.get("mode") if upload_status else "idle")
    )
    return {
        "mode": mode,
        "last_flow_ts": last_flow_ts,
        "last_request_ts": last_req_ts,
        "mitmweb": mitm_status,
        "upload": upload_status,
        "flows_count": len(flows),
        "requests_count": len(reqs),
    }


@app.get("/api/status")
def api_status(_auth=require_auth()):
    return JSONResponse(compute_status())
