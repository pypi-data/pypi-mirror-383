import argparse
import os
from pathlib import Path
import glob
import hashlib
import json as _json
from datetime import datetime, timedelta, timezone
from typing import Optional

from .core.parser import load_requests, load_flows
from .core.storage import Database
from .core.analytics import analyze_requests
from .core.templates import extract_templates
from .reporting.report import generate_markdown_report
from .core.suggestions import build_suggestions
from .agent.orchestrator import Orchestrator, load_providers_config
from .core.env import load_dotenv, missing_env
from .core.templates import normalize_prompt
from .ingest.mitmweb import follow_mitmweb
from .core.tags import tag_flow as tag_flow_util


def _iter_inputs(input_arg: str):
    # Expand ~ and env, then glob
    pat = os.path.expandvars(os.path.expanduser(input_arg))
    paths = glob.glob(pat)
    if not paths and os.path.isdir(pat):
        # If directory, search for known extensions
        for ext in ("*.har", "*.mitm", "*.flow", "*.flows", "*.json"):
            paths.extend(glob.glob(str(Path(pat) / ext)))
    if not paths:
        paths = [pat]
    # Deduplicate & sort by mtime if exists
    paths = list(dict.fromkeys(paths))
    try:
        paths.sort(key=lambda p: os.path.getmtime(p))
    except Exception:
        pass
    return [Path(p) for p in paths]


def cmd_ingest(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    total_flows = 0
    total_recs = 0
    for src in _iter_inputs(args.input):
        if src.suffix.lower() in {".har", ".mitm", ".flow", ".flows"}:
            flows = load_flows(src)
            inserted = db.ingest_flows(flows)
            total_flows += inserted
            print(f"Ingested {inserted} flows from {src}")
        elif src.suffix.lower() == ".json":
            # Try to detect HAR JSON first
            try:
                import json as _json

                data = _json.loads(src.read_text(encoding="utf-8"))
                if (
                    isinstance(data, dict)
                    and isinstance(data.get("log", {}), dict)
                    and isinstance(data["log"].get("entries"), list)
                ):
                    flows = load_flows(src)
                    inserted = db.ingest_flows(flows)
                    total_flows += inserted
                    print(f"Ingested {inserted} flows (HAR JSON) from {src}")
                    continue
            except Exception:
                pass
            items = load_requests(src)
            inserted = db.ingest(items)
            total_recs += inserted
            print(f"Ingested {inserted} records from {src}")
        else:
            items = load_requests(src)
            inserted = db.ingest(items)
            total_recs += inserted
            print(f"Ingested {inserted} records from {src}")
    if total_flows:
        print(f"Total flows inserted: {total_flows} into {args.db}")
    if total_recs:
        print(f"Total records inserted: {total_recs} into {args.db}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    requests = db.fetch_all()
    summary = analyze_requests(requests)
    templates = extract_templates([r["input_text"] for r in requests])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    report_md = generate_markdown_report(summary, templates)
    out.write_text(report_md, encoding="utf-8")
    print(f"Analysis written to {out}")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    # Ingest
    rc = cmd_ingest(args)
    if rc != 0:
        return rc
    # Analyze
    return cmd_analyze(args)


def cmd_dashboard(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    # Prefer flows if present; else fall back to legacy requests
    flows = db.fetch_flows()
    if flows:
        # Project flows to rows shape expected by analytics
        rows = []
        for f in flows:
            rows.append(
                {
                    "ts": f.get("ts_start") or f.get("ts_end") or "",
                    "model": f.get("model") or "",
                    "input_text": f.get("req_body") or "",
                    "output_text": f.get("resp_body") or "",
                    "tokens_in": int(f.get("tokens_in") or 0),
                    "tokens_out": int(f.get("tokens_out") or 0),
                    "latency_ms": int(f.get("latency_ms") or 0),
                    "raw": f.get("raw") or "",
                }
            )
    else:
        rows = db.fetch_all()
    providers = load_providers_config(Path(args.providers))
    summary = analyze_requests(rows)
    suggestions = build_suggestions(rows, providers)
    # Render to console
    print("== Dashboard ==")
    print(
        f"Total: {summary['total']} | Avg in: {summary['avg_tokens_in']:.1f} | Avg out: {summary['avg_tokens_out']:.1f} | Avg latency: {summary['avg_latency_ms']:.1f}ms"
    )
    print("By model:")
    for model, count in summary["by_model"].most_common():
        print(f"  - {model or 'unknown'}: {count}")
    print("\nTop tokens:")
    for tok, cnt in summary["top_tokens"][:10]:
        print(f"  - {tok}: {cnt}")
    print("\nRouting suggestions:")
    for s in suggestions["routing_rules"]:
        print(f"  - {s}")
    print("\nOptimization tips:")
    for tip in suggestions["tips"]:
        print(f"  - {tip}")
    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    providers = load_providers_config(Path(args.providers))
    orch = Orchestrator(providers)
    plan = orch.plan(args.task, preferred=args.provider)
    if args.mode == "plan":
        print("== Plan ==")
        for k, v in plan.items():
            print(f"{k}: {v}")
        return 0
    result = orch.run(args.task, preferred=args.provider)
    print("== Result ==")
    for k, v in result.items():
        print(f"{k}: {v}")
    return 0


def cmd_migrate_flows_backfill(args: argparse.Namespace) -> int:
    """Backfill flows from legacy requests table."""
    db = Database(Path(args.db))
    db.init()
    rows = db.fetch_all()
    if not rows:
        print("No legacy requests found to backfill.")
        return 0
    flows = []
    for r in rows:
        prompt = r.get("input_text") or ""
        output = r.get("output_text") or ""
        tpl_key = hashlib.sha1(normalize_prompt(prompt).encode("utf-8")).hexdigest()[:8]
        content_hash = hashlib.sha256(
            (prompt + "|" + (r.get("model") or "")).encode("utf-8")
        ).hexdigest()
        flows.append(
            {
                "ts_start": r.get("ts"),
                "ts_end": r.get("ts"),
                "method": "POST",
                "url": "",
                "host": "",
                "path": "",
                "status": 0,
                "provider": "",
                "model": r.get("model") or "",
                "req_headers": "{}",
                "req_body": prompt[:200000],
                "resp_headers": "{}",
                "resp_body": output[:200000],
                "tokens_in": int(r.get("tokens_in") or 0),
                "tokens_out": int(r.get("tokens_out") or 0),
                "latency_ms": int(r.get("latency_ms") or 0),
                "session_id": "",
                "template_key": tpl_key,
                "content_hash": content_hash,
                "raw": r.get("raw") or "{}",
            }
        )
    inserted = db.ingest_flows(flows)
    print(f"Backfilled {inserted} flows from legacy requests into flows table.")
    return 0


def cmd_migrate_add_remote_id(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    # Add column and unique index if missing
    with db._conn() as con:  # type: ignore[attr-defined]
        try:
            con.execute("ALTER TABLE flows ADD COLUMN remote_flow_id TEXT")
        except Exception:
            pass
        try:
            con.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS uniq_flows_remote_id ON flows(remote_flow_id)"
            )
        except Exception:
            pass
    print("Ensured remote_flow_id column and unique index exist on flows table.")
    return 0


def _since_cutoff(since: Optional[str]) -> Optional[str]:
    if not since:
        return None
    s = since.strip().lower()
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
            return dt.isoformat()
        except Exception:
            return None
    return s


def cmd_export_flows(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    flows = db.fetch_flows()
    cutoff = _since_cutoff(args.since)

    def ok(f: dict) -> bool:
        if args.model and (f.get("model") or "").lower() != args.model.lower():
            return False
        if args.provider and (f.get("provider") or "").lower() != args.provider.lower():
            return False
        if args.status is not None and int(f.get("status") or 0) != int(args.status):
            return False
        if args.tag:
            # Build a row-like structure for tagging
            row = {
                "input_text": f.get("req_body") or "",
                "output_text": f.get("resp_body") or "",
                "tokens_out": f.get("tokens_out") or 0,
            }
            tags = [t.lower() for t in tag_flow_util(row)]
            if args.tag.lower() not in tags:
                return False
        if cutoff:
            ts = f.get("ts_start") or f.get("ts_end") or ""
            return ts >= cutoff
        return True

    rows = [f for f in flows if ok(f)]
    # slice
    off = max(0, int(args.offset or 0))
    lim = int(args.limit or 0)
    if lim > 0:
        rows = rows[off : off + lim]
    else:
        rows = rows[off:]
    # redact if requested
    if int(args.redact or 0) == 1:
        try:
            from .core.redact import redact_text
        except Exception:

            def redact_text(x):
                return x

        for r in rows:
            if r.get("req_body"):
                r["req_body"] = redact_text(r["req_body"])  # type: ignore
            if r.get("resp_body"):
                r["resp_body"] = redact_text(r["resp_body"])  # type: ignore
            if r.get("req_headers"):
                r["req_headers"] = r["req_headers"]  # could redact further if needed
            if r.get("resp_headers"):
                r["resp_headers"] = r["resp_headers"]
    # ensure parent
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(rows)} flows to {out}")
    return 0


def cmd_env_check(args: argparse.Namespace) -> int:
    # Required base var
    required = ["LITELLM_MASTER_KEY"]
    opt = ["LITELLM_SALT_KEY", "PORT", "STORE_MODEL_IN_DB", "DATABASE_URL"]
    miss = missing_env(required)
    # DATABASE_URL is required only if STORE_MODEL_IN_DB=true
    need_db = str(os.environ.get("STORE_MODEL_IN_DB", "")).lower() in {
        "1",
        "true",
        "yes",
    }
    if need_db and not os.environ.get("DATABASE_URL"):
        miss.append("DATABASE_URL")
    if miss:
        print("Missing Environment Variables")
        print(", ".join(miss))
        return 1
    print("All required environment variables are set.")
    print("Optional variables:", ", ".join([k for k in opt if os.environ.get(k)]))
    return 0


def cmd_env_example(args: argparse.Namespace) -> int:
    example = Path("configs/.env.example").read_text(encoding="utf-8")
    print(example)
    return 0


def cmd_providers_list(args: argparse.Namespace) -> int:
    providers = load_providers_config(Path("configs/providers.json"))
    print("ID | match | $/1k in | $/1k out | quality")
    for pid, meta in providers.items():
        p = meta.get("pricing", {})
        print(
            f"{pid} | {meta.get('match','')} | {p.get('input_per_1k',0)} | {p.get('output_per_1k',0)} | {meta.get('quality',0)}"
        )
    return 0


_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": "OLLAMA_BASE_URL",
}


def cmd_providers_check(args: argparse.Namespace) -> int:
    present = []
    missing = []
    for provider, envkey in _KEY_ENV.items():
        if os.environ.get(envkey):
            present.append((provider, envkey))
        else:
            missing.append((provider, envkey))
    print("Configured keys/endpoints:")
    for p, k in present:
        print(f"- {p}: {k} set")
    if missing:
        print("\nMissing keys/endpoints:")
        for p, k in missing:
            print(f"- {p}: set {k}")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lifesaver-lite-llm",
        description="Ingest and analyze Anthropic/Claude request logs to optimize LLM usage.",
    )
    p.add_argument("--db", default="data/analysis.db", help="Path to SQLite DB file")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser(
        "ingest", help="Ingest files (HAR/.mitm/.json); supports globs/dirs"
    )
    pi.add_argument(
        "--input",
        required=True,
        help="Path or glob (e.g., ~/Downloads/flows*) or directory",
    )
    pi.set_defaults(func=cmd_ingest)

    pa = sub.add_parser("analyze", help="Analyze data and produce a Markdown report")
    pa.add_argument("--out", default="reports/report.md", help="Output report path")
    pa.set_defaults(func=cmd_analyze)

    pall = sub.add_parser("all", help="Ingest then analyze in a single run")
    pall.add_argument("--input", required=True, help="Path to exported JSON file")
    pall.add_argument("--out", default="reports/report.md", help="Output report path")
    pall.set_defaults(func=cmd_all)

    pd = sub.add_parser("dashboard", help="Show monitoring metrics and suggestions")
    pd.add_argument(
        "--providers", default="configs/providers.json", help="Providers config JSON"
    )
    pd.set_defaults(func=cmd_dashboard)

    pag = sub.add_parser("agent", help="Agent mode: plan or run a task with routing")
    pag.add_argument(
        "--providers", default="configs/providers.json", help="Providers config JSON"
    )
    pag.add_argument("--task", required=True, help="Task description")
    pag.add_argument("--mode", choices=["plan", "run"], default="plan")
    pag.add_argument("--provider", default="auto", help="Force provider id or 'auto'")
    pag.set_defaults(func=cmd_agent)

    pe = sub.add_parser("env", help="Environment utilities")
    pe_sub = pe.add_subparsers(dest="env_cmd", required=True)
    pec = pe_sub.add_parser("check", help="Check required environment variables")
    pec.set_defaults(func=cmd_env_check)
    pee = pe_sub.add_parser("example", help="Print example .env contents")
    pee.set_defaults(func=cmd_env_example)

    pprov = sub.add_parser("providers", help="Provider utilities")
    pprov_sub = pprov.add_subparsers(dest="providers_cmd", required=True)
    ppl = pprov_sub.add_parser("list", help="List providers and pricing/quality")
    ppl.set_defaults(func=cmd_providers_list)
    ppc = pprov_sub.add_parser("check-keys", help="Check for configured API keys")
    ppc.set_defaults(func=cmd_providers_check)

    # Migrations
    pm = sub.add_parser("migrate", help="Database migrations and backfills")
    pm_sub = pm.add_subparsers(dest="mig_cmd", required=True)
    pfb = pm_sub.add_parser(
        "flows-backfill", help="Backfill flows table from legacy requests table"
    )
    pfb.set_defaults(func=cmd_migrate_flows_backfill)
    pfcol = pm_sub.add_parser(
        "flows-add-remote-id",
        help="Add remote_flow_id column + unique index to flows table",
    )
    pfcol.set_defaults(func=cmd_migrate_add_remote_id)

    # Mitmweb live ingest
    pmw = sub.add_parser("mitmweb", help="Ingest from a running mitmweb instance")
    pmw_sub = pmw.add_subparsers(dest="mitm_cmd", required=True)
    pmwf = pmw_sub.add_parser("follow", help="Poll mitmweb flows and ingest new ones")
    pmwf.add_argument(
        "--url",
        default=os.environ.get("MITMWEB_URL", "http://localhost:8081"),
        help="mitmweb base URL",
    )
    pmwf.add_argument(
        "--interval",
        type=float,
        default=float(os.environ.get("MITMWEB_INTERVAL", 2.0)),
        help="poll interval seconds",
    )
    pmwf.add_argument(
        "--cookie",
        default=os.environ.get("MITMWEB_COOKIE", ""),
        help="Cookie header for authenticated mitmweb",
    )
    pmwf.set_defaults(func=cmd_mitmweb_follow)

    # Export flows
    pexp = sub.add_parser("export", help="Export data snapshots")
    pexp_sub = pexp.add_subparsers(dest="export_cmd", required=True)
    pexpf = pexp_sub.add_parser("flows", help="Export flows to JSON")
    pexpf.add_argument("--out", required=True, help="Output JSON path")
    pexpf.add_argument(
        "--since", default=None, help="ISO timestamp or relative now-5m/now-1h/now-24h"
    )
    pexpf.add_argument("--model", default=None)
    pexpf.add_argument("--provider", default=None)
    pexpf.add_argument("--status", type=int, default=None)
    pexpf.add_argument("--tag", default=None, help="(reserved)")
    pexpf.add_argument("--offset", type=int, default=0)
    pexpf.add_argument("--limit", type=int, default=0)
    pexpf.add_argument(
        "--redact", type=int, default=1, help="1 to mask bodies/headers; 0 to disable"
    )
    pexpf.set_defaults(func=cmd_export_flows)

    return p


def main(argv=None) -> int:
    # Load .env early (non-invasive)
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    # Ensure parent dirs
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    return int(args.func(args) or 0)


def cmd_mitmweb_follow(args: argparse.Namespace) -> int:
    db = Database(Path(args.db))
    db.init()
    status_path = os.environ.get("MITMWEB_STATUS_PATH", "") or None
    follow_mitmweb(
        args.url,
        db,
        interval_sec=args.interval,
        cookie=(args.cookie or None),
        status_path=status_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
