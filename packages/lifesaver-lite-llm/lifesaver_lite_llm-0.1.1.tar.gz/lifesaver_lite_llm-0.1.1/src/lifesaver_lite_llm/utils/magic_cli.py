from __future__ import annotations

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict

import requests
from lifesaver_lite_llm.store.context import ContextStore


MITM_CONTAINER = os.environ.get("MITM_CONTAINER", "mitmproxy-local")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8080"))
WEB_PORT = int(os.environ.get("WEB_PORT", "8081"))
PROXY_URL = os.environ.get("PROXY_URL", f"http://localhost:{PROXY_PORT}")
CA_DIR = Path(os.path.expanduser(os.environ.get("MITM_CERT_DIR", "~/.mitmproxy")))
CA_PATH = CA_DIR / "mitmproxy-ca.pem"
CONTEXT_DB = Path(
    os.environ.get("CONTEXT_DB", os.environ.get("DB_PATH", "data/analysis.db"))
)
SESSION_FILE = Path(os.getcwd()) / ".lifesaver" / "session.json"


def _run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode(), err.decode()


def ensure_mitm_running() -> None:
    # Check docker exists
    rc, _, _ = _run(["docker", "ps"])
    if rc != 0:
        print("Docker is required to start mitmproxy automatically.", file=sys.stderr)
        return
    # Check container running
    rc, out, _ = _run(["docker", "ps", "--format", "{{.Names}}"])
    if MITM_CONTAINER in out.split():
        return
    # Ensure cert dir exists
    CA_DIR.mkdir(parents=True, exist_ok=True)
    # Run mitmweb container
    vol = f"{str(CA_DIR)}:/home/mitmproxy/.mitmproxy"
    cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        MITM_CONTAINER,
        "-p",
        f"{PROXY_PORT}:8080",
        "-p",
        f"{WEB_PORT}:8081",
        "-v",
        vol,
        "mitmproxy/mitmproxy",
        "mitmweb",
        "--web-host",
        "0.0.0.0",
        "--listen-host",
        "0.0.0.0",
        "--listen-port",
        "8080",
    ]
    rc, out, err = _run(cmd)
    if rc != 0:
        print(f"Failed to start mitmproxy: {err}", file=sys.stderr)
        return
    # Give it a moment to boot
    time.sleep(2)


def ensure_ca_downloaded() -> Path | None:
    try:
        if CA_PATH.exists():
            return CA_PATH
        url = f"http://localhost:{WEB_PORT}/mitmproxy-ca.pem"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        CA_DIR.mkdir(parents=True, exist_ok=True)
        CA_PATH.write_bytes(r.content)
        return CA_PATH
    except Exception:
        return CA_PATH if CA_PATH.exists() else None


def ensure_session(session_name: str | None = None) -> int:
    store = ContextStore(CONTEXT_DB)
    # Try to load session id from .lifesaver file
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SESSION_FILE.exists():
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            sid = int(data.get("session_id"))
            return sid
        except Exception:
            pass
    # Create a new one
    s = store.create_session(name=session_name or "default", cwd=os.getcwd())
    SESSION_FILE.write_text(
        json.dumps({"session_id": s.id, "name": s.name}, indent=2), encoding="utf-8"
    )
    return s.id


def proxies() -> Dict[str, str]:
    return {"http": PROXY_URL, "https": PROXY_URL}


def do_anthropic(action: str, args: list[str], verify: Path | bool):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    if action == "models":
        url = "https://api.anthropic.com/v1/models"
        r = requests.get(
            url, headers=headers, proxies=proxies(), verify=verify, timeout=30
        )
        print(json.dumps(r.json(), indent=2))
    elif action == "chat":
        prompt = args[0] if args else "Hello from magic-cli"
        url = "https://api.anthropic.com/v1/messages"
        body = {
            "model": os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            "max_tokens": 128,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(
            url,
            headers={**headers, "content-type": "application/json"},
            json=body,
            proxies=proxies(),
            verify=verify,
            timeout=60,
        )
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Unknown action for claude: {action}", file=sys.stderr)
        sys.exit(1)


def do_openai(action: str, args: list[str], verify: Path | bool):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {key}"}
    if action == "models":
        url = "https://api.openai.com/v1/models"
        r = requests.get(
            url, headers=headers, proxies=proxies(), verify=verify, timeout=30
        )
        print(json.dumps(r.json(), indent=2))
    elif action == "chat":
        prompt = args[0] if args else "Hello from magic-cli"
        url = "https://api.openai.com/v1/chat/completions"
        body = {
            "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(
            url,
            headers={**headers, "content-type": "application/json"},
            json=body,
            proxies=proxies(),
            verify=verify,
            timeout=60,
        )
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Unknown action for openai: {action}", file=sys.stderr)
        sys.exit(1)


def do_gemini(action: str, args: list[str], verify: Path | bool):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("GEMINI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    base = "https://generativelanguage.googleapis.com/v1beta"
    if action == "models":
        url = f"{base}/models?key={key}"
        r = requests.get(url, proxies=proxies(), verify=verify, timeout=30)
        print(json.dumps(r.json(), indent=2))
    elif action == "chat":
        prompt = args[0] if args else "Hello from magic-cli"
        model = os.environ.get("GEMINI_MODEL", "models/gemini-1.5-flash")
        url = f"{base}/{model}:generateContent?key={key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=body, proxies=proxies(), verify=verify, timeout=60)
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Unknown action for gemini: {action}", file=sys.stderr)
        sys.exit(1)


def do_openrouter(action: str, args: list[str], verify: Path | bool):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("OPENROUTER_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {key}"}
    if action == "models":
        url = "https://openrouter.ai/api/v1/models"
        r = requests.get(
            url, headers=headers, proxies=proxies(), verify=verify, timeout=30
        )
        print(json.dumps(r.json(), indent=2))
    elif action == "chat":
        prompt = args[0] if args else "Hello from magic-cli"
        url = "https://openrouter.ai/api/v1/chat/completions"
        body = {
            "model": os.environ.get("OPENROUTER_MODEL", "openrouter/auto"),
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(
            url,
            headers={**headers, "content-type": "application/json"},
            json=body,
            proxies=proxies(),
            verify=verify,
            timeout=60,
        )
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Unknown action for openrouter: {action}", file=sys.stderr)
        sys.exit(1)


def do_groq(action: str, args: list[str], verify: Path | bool):
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY not set.", file=sys.stderr)
        sys.exit(1)


def do_router(action: str, args: list[str], verify: Path | bool) -> int:
    # Call a LiteLLM router endpoint
    url = os.environ.get("ROUTER_URL", "http://localhost:4000/v1/chat/completions")
    key = os.environ.get("LITELLM_MASTER_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    sid = ensure_session()
    store = ContextStore(CONTEXT_DB)
    pinned = store.get_pinned_notes(sid)
    history = store.get_messages(sid, limit=12)
    if action == "models":
        meta = requests.get(
            url.replace("/v1/chat/completions", "/v1/models"),
            headers=headers,
            proxies=proxies(),
            verify=verify,
            timeout=30,
        )
        print(json.dumps(meta.json(), indent=2))
        return 0
    elif action in ("chat", "repl"):
        if args:
            user_msg = args[0]
            store.add_message(sid, "user", user_msg)
        else:
            print(
                'Usage: magic-cli router chat "Hello" or magic-cli repl',
                file=sys.stderr,
            )
            return 1
        # Build messages: system pinned notes + history + new user
        messages = []
        if pinned:
            messages.append({"role": "system", "content": pinned})
        for m in history:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_msg})
        body = {"model": os.environ.get("ROUTER_MODEL", "auto"), "messages": messages}
        r = requests.post(
            url,
            headers={**headers, "content-type": "application/json"},
            json=body,
            proxies=proxies(),
            verify=verify,
            timeout=120,
        )
        data = r.json()
        # Try to extract assistant content (OpenAI-compatible)
        text = None
        try:
            text = data["choices"][0]["message"]["content"]
        except Exception:
            try:
                # Anthropic-like
                text = data.get("content", [{"text": ""}])[0].get("text", "")
            except Exception:
                text = json.dumps(data)
        print(text)
        store.add_message(sid, "assistant", text or "")
        return 0
    else:
        print(f"Unknown router action: {action}", file=sys.stderr)
        return 1


def repl(verify: Path | bool) -> int:
    ensure_mitm_running()
    ensure_ca_downloaded()
    sid = ensure_session()
    store = ContextStore(CONTEXT_DB)
    print("magic-cli REPL: /init, /context, /use <model>, /route <mode>, /exit")
    current_model = os.environ.get("ROUTER_MODEL", "auto")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            continue
        if line.startswith("/"):
            parts = line.strip().split()
            cmd = parts[0].lower()
            if cmd == "/exit":
                break
            elif cmd == "/init":
                # re-init session in cwd
                s = store.create_session(name="default", cwd=os.getcwd())
                SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
                SESSION_FILE.write_text(
                    json.dumps({"session_id": s.id, "name": s.name}, indent=2),
                    encoding="utf-8",
                )
                print(f"Initialized new session {s.id}")
                sid = s.id
            elif cmd == "/context":
                if len(parts) == 1:
                    print(
                        "Pinned notes:\n" + (store.get_pinned_notes(sid) or "<empty>")
                    )
                else:
                    notes = line[len("/context") :].strip()
                    store.set_pinned_notes(sid, notes)
                    print("Updated pinned notes.")
            elif cmd == "/use" and len(parts) >= 2:
                current_model = parts[1]
                os.environ["ROUTER_MODEL"] = current_model
                print(f"Using model: {current_model}")
            elif cmd == "/route" and len(parts) >= 2:
                # simple route intent flag
                os.environ["ROUTE_INTENT"] = parts[1]
                print(f"Route intent: {parts[1]}")
            else:
                print("Unknown command.")
            continue
        # Otherwise, treat as a user message
        do_router("chat", [line], verify)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 1:
        print("Usage: magic-cli <provider> [action] [args...]", file=sys.stderr)
        return 1
    provider = argv[0].lower()
    action = argv[1].lower() if len(argv) > 1 else "models"
    args = argv[2:]

    # Only GEMINI_API_KEY is recommended/mandatory by default; others are optional.
    ensure_mitm_running()
    ca = ensure_ca_downloaded()
    verify: Path | bool = ca if ca and ca.exists() else True

    if provider in ("claude", "anthropic"):
        do_anthropic(action, args, verify)
    elif provider in ("codex", "openai"):
        do_openai(action, args, verify)
    elif provider in ("gemini",):
        do_gemini(action, args, verify)
    elif provider in ("openrouter",):
        do_openrouter(action, args, verify)
    elif provider in ("groq",):
        do_groq(action, args, verify)
    elif provider in ("router",):
        return do_router(action, args, verify)
    elif provider in ("repl",):
        return repl(verify)
    else:
        print(f"Unknown provider: {provider}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
