# docker_daemon.py
import argparse
import asyncio
import json
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Any
from mloggerai.errorsolver import ErrorSolver

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

# --- PATTERN MULTI-LINGUAGGIO ---
LANGUAGE_PATTERNS = {
    "python": re.compile(r"(Traceback \(most recent call last\):|File \".+\.py\", line \d+|Exception|Error: .+)", re.IGNORECASE),
    "java": re.compile(r"(Exception in thread .+|at [\w\.]+\(.*\.java:\d+\)|Caused by: .+)", re.IGNORECASE),
    "rust": re.compile(r"(thread '.*' panicked at|RUST_BACKTRACE|error:\s.+|note:\s.+)", re.IGNORECASE),
    "javascript": re.compile(r"(TypeError:|ReferenceError:|SyntaxError:|UnhandledPromiseRejectionWarning|at .+\(.+:\d+:\d+\))", re.IGNORECASE),
    "kotlin": re.compile(r"(Exception in thread .+|at .+\.kt:\d+|Caused by: .+)", re.IGNORECASE),
}

ERROR_KEYWORDS = ["error", "exception", "failed", "panic", "fatal", "traceback", "segfault"]
EVENT_WINDOW_SECONDS = 1.5

# --- GLOBALI per la dashboard ---
active_clients: List[WebSocket] = []
recent_events: List[Dict[str, Any]] = []


# -------------------------------
# 🔍 CLASSE MONITOR DOCKER
# -------------------------------
class DockerMonitor:
    """Monitora i log di container Docker e invia errori a ErrorSolver."""

    def __init__(self, solver: ErrorSolver, json_log_path="logs/docker_events.jsonl", filter_pattern: str = None):
        self.solver = solver
        self.json_log_path = json_log_path
        self.filter_pattern = re.compile(filter_pattern, re.IGNORECASE) if filter_pattern else None
        self._buffers = {}
        self._last_times = {}
        self._active_tasks = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        import os
        os.makedirs("logs", exist_ok=True)

    def _detect_language(self, text: str) -> str:
        for lang, pattern in LANGUAGE_PATTERNS.items():
            if pattern.search(text):
                return lang
        return "generic"

    def _is_error_line(self, line: str) -> bool:
        l = line.lower()
        return any(k in l for k in ERROR_KEYWORDS) or any(p.search(line) for p in LANGUAGE_PATTERNS.values())

    def _matches_filter(self, container_name: str) -> bool:
        """Ritorna True se il container passa il filtro regex (o nessun filtro impostato)."""
        if not self.filter_pattern:
            return True
        return bool(self.filter_pattern.search(container_name))

    async def handle_line(self, container: str, line: str):
        now = datetime.now()
        line = line.rstrip("\n")
        if not line:
            return
        if self._is_error_line(line):
            last_time = self._last_times.get(container)
            if last_time is None or (now - last_time).total_seconds() > EVENT_WINDOW_SECONDS:
                self._buffers[container] = [line]
            else:
                self._buffers[container].append(line)
            self._last_times[container] = now
            await self._process_buffer(container)
        elif container in self._last_times and (now - self._last_times[container]).total_seconds() <= EVENT_WINDOW_SECONDS:
            self._buffers[container].append(line)
            self._last_times[container] = now

    async def _process_buffer(self, container: str):
        buf = self._buffers.get(container, [])
        if not buf:
            return
        text = "\n".join(buf)
        language = self._detect_language(text)
        timestamp = datetime.now().isoformat()

        try:
            solution = self.solver.solve_from_log(f"[{container}] {text}")
        except Exception as e:
            solution = f"Errore interno nel solver: {e}"

        event = {
            "timestamp": timestamp,
            "container": container,
            "language": language,
            "error": text,
            "solution": solution,
        }

        # dashboard buffer
        recent_events.append(event)
        if len(recent_events) > 100:
            recent_events.pop(0)

        await broadcast_json(event)

        # log file
        with open(self.json_log_path, "a", encoding="utf-8") as f:
            json.dump(event, f, ensure_ascii=False)
            f.write("\n")

        self.solver.logger.info(f"[{container}] {language}\n{text}\n💡 {solution}\n---")
        self._buffers[container] = []
        self._last_times[container] = None

    async def attach_to_container(self, container_name: str):
        """Attacca il monitor solo se il nome passa il filtro."""
        if not self._matches_filter(container_name):
            self.solver.logger.info(f"⏩ Ignoro container '{container_name}' (non corrisponde al filtro)")
            return
        if container_name in self._active_tasks:
            return
        self.solver.logger.info(f"🔗 Attacco ai log di {container_name}")
        task = asyncio.create_task(self._read_container_logs(container_name))
        self._active_tasks[container_name] = task

    async def _read_container_logs(self, container_name: str):
        cmd = ["docker", "logs", "-f", container_name]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def read_stream(stream):
            while True:
                line = await stream.readline()
                if not line:
                    break
                await self.handle_line(container_name, line.decode(errors="ignore"))

        await asyncio.gather(read_stream(proc.stdout), read_stream(proc.stderr))
        self._active_tasks.pop(container_name, None)
        self.solver.logger.info(f"📴 Container {container_name} terminato")

    async def monitor_existing_containers(self):
        proc = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
        containers = [c.strip() for c in proc.stdout.splitlines() if c.strip()]
        for c in containers:
            await self.attach_to_container(c)

    async def listen_for_new_containers(self):
        self.solver.logger.info("🎧 Ascolto eventi Docker...")
        proc = await asyncio.create_subprocess_exec(
            "docker", "events", "--format", "{{.Status}} {{.Actor.Attributes.name}}",
            stdout=asyncio.subprocess.PIPE,
        )
        async for line_bytes in proc.stdout:
            line = line_bytes.decode(errors="ignore").strip()
            if not line:
                continue
            try:
                status, name = line.split(" ", 1)
            except ValueError:
                continue
            if status == "start":
                self.solver.logger.info(f"🆕 Nuovo container: {name}")
                await self.attach_to_container(name)
            elif status == "die":
                self.solver.logger.info(f"💀 Container terminato: {name}")


# -------------------------------
# 🌐 DASHBOARD FASTAPI
# -------------------------------
app = FastAPI(title="ErrorSolver Docker Monitor")

html = """
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>ErrorSolver Docker Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background: #111; color: #ddd; font-family: monospace; block-size: 100vh; display: flex; flex-direction: column; margin: 0; }
#controls { padding: 0.5rem; }
#log { flex-grow: 1; overflow-y: auto; padding: 1rem; }
.card { background: #1a1a1a; margin-block-end: 0.5rem; border: 1px solid #333; }
.card-header { font-weight: bold; color: #00ffcc; display: flex; justify-content: space-between; }
.card-body { white-space: pre-wrap; }
.error { color: #ff4444; }
.solution { color: #88ff88; }
.lang { color: #ffaa00; margin-inline-start: 0.5rem; }
</style>
</head>
<body>
<div id="controls" class="d-flex gap-2 align-items-center">
    <button id="clear" class="btn btn-secondary btn-sm">Clear</button>
    <span id="status" class="badge bg-secondary">Offline</span>
</div>
<div id="log" class="container-fluid"></div>

<script>
const logDiv = document.getElementById("log");
const statusBadge = document.getElementById("status");
const ws = new WebSocket(`ws://${location.host}/ws`);

ws.onopen = () => { statusBadge.textContent = "Online"; statusBadge.className = "badge bg-success"; };
ws.onclose = () => { statusBadge.textContent = "Offline"; statusBadge.className = "badge bg-secondary"; };

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const card = document.createElement("div");
    card.className = "card";

    const header = document.createElement("div");
    header.className = "card-header";
    header.innerHTML = `<span>[${data.container}]</span> <span class="lang">(${data.language})</span>`;

    const body = document.createElement("div");
    body.className = "card-body";
    body.innerHTML = `<div class="error">${data.error}</div><div class="solution">💡 ${data.solution}</div>`;

    card.appendChild(header);
    card.appendChild(body);

    logDiv.prepend(card); // prepend per mostrare eventi più recenti sopra
};

document.getElementById("clear").onclick = () => { logDiv.innerHTML = ''; };
</script>
</body>
</html>

"""

@app.get("/")
async def dashboard():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_clients.append(ws)
    for ev in recent_events[-10:]:
        await ws.send_json(ev)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        active_clients.remove(ws)

async def broadcast_json(event: dict):
    dead = []
    for ws in active_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in active_clients:
            active_clients.remove(ws)


# -------------------------------
# 🧠 MAIN
# -------------------------------
async def main_async(args):
    solver = ErrorSolver(model=args.model, log_file=args.log_file, output_language=args.lang)
    monitor = DockerMonitor(solver, json_log_path=args.json_log, filter_pattern=args.filter)

    await monitor.monitor_existing_containers()
    asyncio.create_task(monitor.listen_for_new_containers())

    config = uvicorn.Config(app, host="0.0.0.0", port=8008, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


def main():
    parser = argparse.ArgumentParser(description="ErrorSolver Docker Daemon con dashboard e filtro container.")
    parser.add_argument("--model", help="Override modello ErrorSolver.")
    parser.add_argument("--log-file", default="logs/docker_daemon.log", help="File di log testuale.")
    parser.add_argument("--json-log", default="logs/docker_events.jsonl", help="File JSON di log errori.")
    parser.add_argument("--lang", default="italiano", help="Lingua di risposta del solver.")
    parser.add_argument("--filter", help="Regex o parole chiave per filtrare i container (es: 'web|api|nginx').")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_async(args))
    except KeyboardInterrupt:
        print("\n🛑 Interrotto manualmente.")
    finally:
        loop.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
