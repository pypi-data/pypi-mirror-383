import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Callable, Dict, List, Awaitable, Optional
from .installer import ensure_bds_installed

logger = logging.getLogger("minecraft_bds")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] [BDS] %(message)s", "%H:%M:%S"))
logger.addHandler(handler)


class MinecraftBDS:
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable[..., Awaitable | None]]] = {}
        self.process: Optional[asyncio.subprocess.Process] = None
        self.running = False
        self.path: Path = ensure_bds_installed()

    # -------------------------------------------------
    # User-facing decorators / methods
    # -------------------------------------------------
    def event(self, func: Callable[..., Awaitable | None]):
        """Decorator: Register an event handler."""
        name = func.__name__.replace("_", " ").title()
        self.event_handlers.setdefault(name, []).append(func)
        logger.info(f"Registered handler for event '{name}'")
        return func

    async def RunCommand(self, command: str):
        if not self.process or not self.process.stdin:
            logger.warning("Cannot send command; server not running.")
            return
        self.process.stdin.write(f"{command}\n".encode())
        await self.process.stdin.drain()

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------
    async def start(self):
        """Start BDS and attach to stdout."""
        logger.info("Starting Minecraft Bedrock server...")
        exe = "bedrock_server.exe" if (self.path / "bedrock_server.exe").exists() else "./bedrock_server"
        self.process = await asyncio.create_subprocess_exec(
            str(self.path / exe),
            cwd=str(self.path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.running = True
        asyncio.create_task(self._watch_logs())
        logger.info("BDS started successfully with behaviour pack injected.")

    async def stop(self):
        if not self.process:
            return
        self.process.terminate()
        await self.process.wait()
        self.running = False
        logger.info("BDS stopped.")

    # -------------------------------------------------
    # Internal log watcher
    # -------------------------------------------------
    async def _watch_logs(self):
        assert self.process and self.process.stdout
        event_re = re.compile(r"\[(.*?)\]: (.*)")

        while self.running:
            line = await self.process.stdout.readline()
            if not line:
                await asyncio.sleep(0.05)
                continue

            text = line.decode("utf-8", errors="ignore").strip()
            if not text:
                continue
            logger.debug(text)

            # JSON-style or legacy event lines
            if text.startswith("{") and text.endswith("}"):
                try:
                    event = json.loads(text)
                    await self._dispatch(event.get("event"), event)
                    continue
                except Exception:
                    pass

            m = event_re.search(text)
            if m:
                await self._dispatch(m.group(1), {"raw": m.group(2)})

    async def _dispatch(self, event_name: str, data: dict):
        if not event_name:
            return
        handlers = self.event_handlers.get(event_name)
        if not handlers:
            return
        for h in handlers:
            try:
                if asyncio.iscoroutinefunction(h):
                    await h(data)
                else:
                    h(data)
            except Exception as e:
                logger.exception(f"Error in handler {h.__name__}: {e}")


# Singleton instance exported as `BDS`
BDS = MinecraftBDS()
