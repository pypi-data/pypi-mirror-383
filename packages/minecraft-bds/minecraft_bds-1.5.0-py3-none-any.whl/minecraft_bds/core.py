import asyncio
import re
from pathlib import Path
from .installer import ensure_bds_installed
import subprocess

class MinecraftBDS:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, base_path: Path | None = None, bds_path: Path | None = None):
        """
        Initialize the BDS manager.
        - base_path: where to install the server (defaults to ./server/)
        - bds_path: override the BDS executable path (optional)
        """
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.base_path = Path(base_path) if base_path else Path("./server")
        self.server_path = ensure_bds_installed(self.base_path)
        self.bds_path = bds_path if bds_path else self.server_path / ("bedrock_server.exe" if subprocess.os.name == "nt" else "bedrock_server")
        self.bds_process: asyncio.subprocess.Process | None = None
        self.event_handlers: dict[str, list] = {}
        self.log_pattern = re.compile(r"\[(\w+)\]:\s*([^,]+),?\s*(.*)")

    # ----------------------
    # Event decorator
    # ----------------------
    def event(self, func):
        """
        Decorator to register an async event handler.
        Event name must match the function name.
        """
        name = func.__name__
        if name not in self.event_handlers:
            self.event_handlers[name] = []
        self.event_handlers[name].append(func)
        return func

    async def _dispatch_event(self, event_name: str, data: dict):
        """
        Call all handlers registered for a given event name.
        """
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                print(f"[BDS] Error in event handler {handler.__name__}: {e}")

    # ----------------------
    # Run Minecraft command
    # ----------------------
    async def RunCommand(self, command: str):
        if self.bds_process and self.bds_process.stdin:
            self.bds_process.stdin.write(f"{command}\n".encode())
            await self.bds_process.stdin.drain()
        else:
            print("[BDS] Server not running. Cannot send command.")

    # ----------------------
    # Start server
    # ----------------------
    async def start(self):
        if self.bds_process:
            print("[BDS] Server is already running.")
            return

        print(f"[BDS] Starting server at {self.server_path} …")
        self.bds_process = await asyncio.create_subprocess_exec(
            str(self.bds_path),
            cwd=str(self.server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        asyncio.create_task(self._watch_logs())
        print("[BDS] Server started.")

    # ----------------------
    # Stop server
    # ----------------------
    async def stop(self):
        if not self.bds_process:
            return
        print("[BDS] Stopping server …")
        self.bds_process.terminate()
        await self.bds_process.wait()
        self.bds_process = None
        print("[BDS] Server stopped.")

    # ----------------------
    # Internal log watcher
    # ----------------------
    async def _watch_logs(self):
        if not self.bds_process:
            return

        while True:
            line = await self.bds_process.stdout.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue

            line = line.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print(f"[BDS LOG] {line}")

            # Check for events anywhere in the line
            match = self.log_pattern.search(line)
            if match:
                event_type, arg1, arg_rest = match.groups()
                args = [a.strip() for a in arg_rest.split(",")] if arg_rest else []

                data = {}
                # Predefine some common events
                if event_type == "Entity_Killed":
                    data = {"entity": arg1, "killer": args[0] if args else "unknown"}
                    await self._dispatch_event("Entity_Killed", data)
                elif event_type == "Block_Break":
                    data = {"player": arg1, "block": args[0] if args else "unknown"}
                    await self._dispatch_event("Block_Break", data)
                elif event_type == "World_Loaded":
                    data = {}
                    await self._dispatch_event("World_Loaded", data)
                elif event_type == "XP_Gain":
                    try:
                        xp_gain = int(args[-1])
                    except (ValueError, IndexError):
                        xp_gain = 0
                    data = {"player": arg1, "xp": xp_gain}
                    await self._dispatch_event("XP_Gain", data)
