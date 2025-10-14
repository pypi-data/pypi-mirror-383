from .sessions import Session
from .logger import get_logger
from .config import load_config

from dataclasses import dataclass, field
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from textwrap import dedent
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
import asyncio
import json
import time

logger = get_logger(__name__)

ALLOWED_TOOLS = ["Read", "Write", "Edit", "mcp__cerb-subagent__send_message_to_session"]
PERMISSION_MODE = "acceptEdits"

# Batch processing configuration
BATCH_WAIT_TIME = 10  # Wait 2 seconds after first event before processing
MAX_BATCH_SIZE = 10  # Process immediately if 10 events accumulate
MAX_BATCH_WAIT = 20  # Never wait more than 5 seconds total

SYSTEM_PROMPT_TEMPLATE = dedent(
    """
    You are a monitoring subagent receiving structured HOOK events from Claude Code instances.

    **Session Being Monitored**: {session_id}
    **Agent Type**: {agent_type}

    Your job:

    - Understand the instructions given to the agent in instructions.md and how they interact with the codebase.
    - Output information in realtime about the agent's progress, given the various hooks and codebase access.
    - Do not execute commands. Do not run Bash or WebFetch unless explicitly asked. Only write to the monitor.md file.
    - **IMPORTANT**: You can communicate with the session you're monitoring using the MCP tool `send_message_to_session`

    ## When to Send Messages

    Use `send_message_to_session(session_id="{session_id}", message="...")` when you observe:

    - **Spec violations**: Agent is deviating significantly from instructions.md
    - **Confusion or incorrect approach**: Agent appears to be implementing something incorrectly
    - **Critical issues**: Agent is about to or has made changes that could be problematic
    - **Stuck or spinning**: Agent seems to be going in circles or not making progress

    Be direct but helpful in your messages. Don't send messages for minor issues or normal progress.

    ## Structure of monitor.md Report

    - **Current Status**: Describe what the agent is currently trying to do.
    - **Summary of changes**: For each file, what did the agent do, what choices were made, how did they do it, how does the whole thing get structured.
    - **Deviations from spec**: Detail potential choices the agent made that were not defined or were deviations from the spec given by the designer in the instructions file.

    Don't make it too verbose, it should be definitely less than a page. Think of this as a realtime dashboard, not a log. We do not want to be constantly adding new info, keep it lean, useful and informative.
    """
).strip()


def format_event_for_agent(evt: Dict[str, Any]) -> str:
    """Format event for the monitoring agent"""
    event_type = evt.get("event", "UnknownEvent")
    ts = evt.get("received_at", datetime.now(timezone.utc).isoformat())
    pretty_json = json.dumps(evt, indent=2, ensure_ascii=False)

    return f"HOOK EVENT: {event_type}\ntime: {ts}\n\n```json\n{pretty_json}\n```"


@dataclass
class SessionMonitor:
    session: Session
    allowed_tools: List[str] = field(default_factory=lambda: ALLOWED_TOOLS)
    permission_mode: str = PERMISSION_MODE
    system_prompt_template: str = SYSTEM_PROMPT_TEMPLATE

    client: Optional[ClaudeSDKClient] = None
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=1000))
    task: Optional[asyncio.Task] = None
    last_touch: float = field(default_factory=lambda: time.time())

    async def start(self) -> None:
        if self.client is not None:
            return

        # Format system prompt with session info
        system_prompt = self.system_prompt_template.format(
            session_id=self.session.session_id,
            agent_type=self.session.agent_type.value if self.session.agent_type else "unknown",
        )

        # MCP config to give monitor access to send_message_to_session via HTTP transport
        config = load_config()
        mcp_port = config.get("mcp_port", 8765)
        mcp_config = {
            "cerb-subagent": {
                "type": "http",
                "url": f"http://127.0.0.1:{mcp_port}/mcp",
            }
        }

        options = ClaudeAgentOptions(
            cwd=self.session.work_path,
            system_prompt=system_prompt,
            allowed_tools=self.allowed_tools,
            permission_mode=self.permission_mode,
            hooks={},
            mcp_servers=mcp_config,
        )

        self.client = ClaudeSDKClient(options=options)
        await self.client.__aenter__()
        self.task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except Exception:
                pass
            self.task = None
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None

    async def enqueue(self, evt: Dict[str, Any]) -> None:
        self.last_touch = time.time()
        self.queue.put_nowait(evt)

    async def _run(self) -> None:
        # Ensure .orchestra directory exists
        orchestra_dir = Path(self.session.work_path) / ".orchestra"
        orchestra_dir.mkdir(exist_ok=True)

        await self.client.query(
            f"Session online. Understand and update the .orchestra/monitor.md in the given format. Do NOT log every event, the whole point is to make this easier for the a human to understand what is going on."
        )

        async for chunk in self.client.receive_response():
            logger.info("[%s] startup> %s", self.session.session_id, chunk)

        while True:
            # Collect batch of events
            batch = []

            # Get first event (blocking)
            first_event = await self.queue.get()
            batch.append(first_event)
            batch_start = time.time()

            # Collect more events with timeout
            while True:
                batch_age = time.time() - batch_start

                # Stop if batch is full or too old
                if batch_age >= MAX_BATCH_WAIT:
                    break

                # Try to get more events (with timeout)
                try:
                    evt = await asyncio.wait_for(self.queue.get(), timeout=BATCH_WAIT_TIME)
                    batch.append(evt)
                except asyncio.TimeoutError:
                    break

            # Format all events and send as one message
            try:
                prompts = [format_event_for_agent(evt) for evt in batch]
                combined_prompt = "\n\n---\n\n".join(prompts)

                await self.client.query(combined_prompt)
                async for chunk in self.client.receive_response():
                    logger.info("[%s] batch[%d]> %s", self.session.session_id, len(batch), chunk)
            finally:
                # Mark all events as done
                for _ in batch:
                    self.queue.task_done()


@dataclass
class SessionMonitorWatcher:
    """Watches monitor.md files for a session and its children"""

    session: Session

    def get_monitor_files(self) -> Dict[str, Dict[str, Any]]:
        """
        Get monitor.md files for this session and all its children.
        Returns dict: {session_id: {"path": path, "content": content, "mtime": mtime}}
        """
        monitors = {}
        self._collect_from_session(self.session, monitors)
        return monitors

    def _collect_from_session(self, sess: Session, monitors: Dict[str, Dict[str, Any]]) -> None:
        """Recursively collect monitor files from a session and its children"""
        if not sess.work_path:
            return

        monitor_file = Path(sess.work_path) / ".orchestra" / "monitor.md"

        if monitor_file.exists():
            try:
                content = monitor_file.read_text()
                mtime = monitor_file.stat().st_mtime

                monitors[sess.session_id] = {
                    "path": str(monitor_file),
                    "content": content,
                    "mtime": mtime,
                    "last_updated": datetime.fromtimestamp(mtime).isoformat(),
                }
            except Exception as e:
                logger.error(f"Error reading {monitor_file}: {e}")

        # Process children
        for child in sess.children:
            self._collect_from_session(child, monitors)
