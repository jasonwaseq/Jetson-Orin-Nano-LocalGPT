#!/usr/bin/env python3
import json
import time
import urllib.request
import urllib.error
import os
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = os.environ.get("PORT", "8080")
URL = f"http://{HOST}:{PORT}/completion"

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

URL = "http://127.0.0.1:8080/completion"

BASE = Path.home() / ".localgpt"
SESS = BASE / "sessions"
SESS.mkdir(parents=True, exist_ok=True)

console = Console()

MODES = {
    "default": "You are a helpful assistant.",
    "coding":  "You are a senior software engineer. Be concise. Provide code blocks when useful.",
    "tutor":   "You are a patient tutor. Explain step-by-step and check for understanding.",
    "snark":   "You are witty and playful, but still helpful.",
}

STOP_STRINGS = ["<|im_end|>"]

def now_id():
    return time.strftime("%Y%m%d-%H%M%S")

def save_session(session_id: str, state: dict):
    path = SESS / f"{session_id}.json"
    path.write_text(json.dumps(state, indent=2))
    return path

def load_session(session_id: str):
    path = SESS / f"{session_id}.json"
    return json.loads(path.read_text())

def list_sessions():
    files = sorted(SESS.glob("*.json"), reverse=True)
    return [f.stem for f in files]

def build_prompt(system_prompt: str, turns: list[dict]):
    # This matches the template your llama-server printed earlier.
    p = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
    for t in turns:
        p += f"<|im_start|>{t['role']}\n{t['content']}<|im_end|>\n"
    p += "<|im_start|>assistant\n"
    return p

def sse_stream_completion(prompt: str, n_predict=512, temperature=0.7):
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "stop": STOP_STRINGS,
        "stream": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",  # avoid gzip issues
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=600) as r:
        for raw in r:
            if not raw:
                continue
            line = raw.decode("utf-8", errors="ignore").strip()
            # SSE lines look like: "data: {...}"
            if not line.startswith("data:"):
                continue
            chunk = line[len("data:"):].strip()
            if not chunk:
                continue
            try:
                obj = json.loads(chunk)
            except Exception:
                continue
            if obj.get("stop") is True:
                break
            content = obj.get("content")
            if content:
                yield content

def header(session_id, mode, temp, ctx_chars):
    t = Text()
    t.append("LocalGPT", style="bold")
    t.append(f"  session={session_id}  mode={mode}  temp={temp}  ctx_chars={ctx_chars}", style="dim")
    console.print(Panel(t, expand=False))

def help_panel():
    console.print(Panel(
        "[bold]Commands[/bold]\n"
        "  /help                 show this\n"
        "  /exit                 quit\n"
        "  /new                  new chat\n"
        "  /save                 save chat\n"
        "  /load <id>            load saved chat\n"
        "  /list                 list saved chats\n"
        "  /mode <name>          default|coding|tutor|snark\n"
        "  /temp <0.0-2.0>       set temperature\n"
        "  /ctx <N>              set max context chars\n"
        "  /clear                clear history\n"
        "\n[dim]Tip: Ctrl+C during generation cancels the answer (app stays open).[/dim]\n",
        title="LocalGPT Help",
        expand=False
    ))

def main():
    session_id = now_id()
    mode = "default"
    temperature = 0.7
    max_ctx_chars = 12000
    turns = []

    header(session_id, mode, temperature, max_ctx_chars)
    console.print("[dim]Type /help for commands.[/dim]\n")

    while True:
        try:
            user = console.input("[bold cyan]> [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]bye[/dim]")
            return

        if not user:
            continue

        if user.startswith("/"):
            parts = user.split()
            cmd = parts[0].lower()

            if cmd == "/help":
                help_panel()
                continue
            if cmd in ("/exit", "/quit"):
                console.print("[dim]bye[/dim]")
                return
            if cmd == "/new":
                session_id = now_id()
                turns = []
                header(session_id, mode, temperature, max_ctx_chars)
                console.print()
                continue
            if cmd == "/clear":
                turns = []
                console.print("[dim](cleared)[/dim]\n")
                continue
            if cmd == "/mode":
                if len(parts) < 2 or parts[1] not in MODES:
                    console.print(f"[red]Modes:[/red] {', '.join(MODES.keys())}\n")
                else:
                    mode = parts[1]
                    console.print(f"[green](mode={mode})[/green]\n")
                continue
            if cmd == "/temp":
                if len(parts) < 2:
                    console.print(f"[dim]temp={temperature}[/dim]\n")
                else:
                    try:
                        temperature = max(0.0, min(2.0, float(parts[1])))
                        console.print(f"[green](temp={temperature})[/green]\n")
                    except ValueError:
                        console.print("[red]Invalid temperature[/red]\n")
                continue
            if cmd == "/ctx":
                if len(parts) < 2:
                    console.print(f"[dim]ctx_chars={max_ctx_chars}[/dim]\n")
                else:
                    try:
                        max_ctx_chars = max(2000, int(parts[1]))
                        console.print(f"[green](ctx_chars={max_ctx_chars})[/green]\n")
                    except ValueError:
                        console.print("[red]Invalid ctx[/red]\n")
                continue
            if cmd == "/save":
                state = {
                    "session_id": session_id,
                    "mode": mode,
                    "temperature": temperature,
                    "max_ctx_chars": max_ctx_chars,
                    "turns": turns,
                    "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                path = save_session(session_id, state)
                console.print(f"[green](saved)[/green] {path}\n")
                continue
            if cmd == "/list":
                ids = list_sessions()
                if not ids:
                    console.print("[dim](no saved sessions)[/dim]\n")
                else:
                    console.print(Panel("\n".join(ids), title="Saved sessions", expand=False))
                continue
            if cmd == "/load":
                if len(parts) < 2:
                    console.print("[red]Usage:[/red] /load <session_id>\n")
                    continue
                sid = parts[1]
                try:
                    state = load_session(sid)
                    session_id = state["session_id"]
                    mode = state.get("mode", "default")
                    temperature = state.get("temperature", 0.7)
                    max_ctx_chars = state.get("max_ctx_chars", 12000)
                    turns = state.get("turns", [])
                    header(session_id, mode, temperature, max_ctx_chars)
                    console.print("[green](loaded)[/green]\n")
                except Exception as e:
                    console.print(f"[red](failed to load)[/red] {e}\n")
                continue

            console.print("[red]Unknown command[/red] (try /help)\n")
            continue

        # Append user turn
        turns.append({"role": "user", "content": user})

        # Trim history by char length for stable latency
        while True:
            prompt = build_prompt(MODES[mode], turns)
            if len(prompt) <= max_ctx_chars:
                break
            if len(turns) >= 2:
                turns = turns[2:]
            else:
                turns = turns[1:]

        console.print(Panel("", title="assistant", border_style="green"))
        buf = ""
        try:
            for chunk in sse_stream_completion(prompt, n_predict=512, temperature=temperature):
                buf += chunk
                console.print(chunk, end="")
            console.print("\n")
        except KeyboardInterrupt:
            console.print("\n[dim](cancelled)[/dim]\n")
            # Don't append partial assistant message if cancelled
            continue
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            console.print(f"\n[red]API error:[/red] {e}\n")
            continue

        turns.append({"role": "assistant", "content": buf.strip()})

if __name__ == "__main__":
    main()
