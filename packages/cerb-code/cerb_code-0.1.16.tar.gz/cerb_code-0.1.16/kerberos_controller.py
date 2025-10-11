#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Static, ListView, ListItem, Label

# ------------- tmux helpers -------------

def tmux(sock: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["tmux", "-L", sock, *args],
        check=False,
        capture_output=True,
        text=True,
    )

@dataclass
class WorkWindow:
    index: int
    name: str
    active: bool

def list_work_windows(sock: str, work: str) -> List[WorkWindow]:
    out = tmux(sock, "list-windows", "-t", work,
               "-F", "#{window_index}\t#{window_name}\t#{?window_active,1,0}")
    if out.returncode != 0:
        return []
    rows: List[WorkWindow] = []
    for line in out.stdout.strip().splitlines():
        if not line.strip():
            continue
        idx_s, name, active_s = line.split("\t")
        rows.append(WorkWindow(index=int(idx_s), name=name, active=(active_s == "1")))
    rows.sort(key=lambda w: w.index)
    return rows

def show_in_view(sock: str, work: str, view: str, pane_l: str, target_idx: int, slot: int = 0) -> None:
    """Link WORK:target_idx into VIEW:slot, then tell the left pane’s nested client to select it."""
    tmux(sock, "unlink-window", "-t", f"{view}:{slot}")
    tmux(sock, "link-window", "-s", f"{work}:{target_idx}", "-t", f"{view}:{slot}")
    inner_cmd = f"tmux -L {sock} select-window -t {view}:{slot}"
    tmux(sock, "send-keys", "-t", pane_l, inner_cmd, "C-m")

# ------------- UI (sidebar-only) -------------

SIDEBAR_WIDTH = 32  # purely cosmetic here; real width set by tmux split

class KerberosController(App):
    """Right-pane controller with only the sidebar list."""
    CSS = f"""
    Screen {{
        background: #0a0a0a;
    }}
    #wrap {{
        layout: vertical;
        height: 100%;
        padding: 1 1;
    }}
    #title {{
        color: #00ff9f;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }}
    ListView {{
        height: 1fr;
        background: transparent;
    }}
    ListItem {{
        color: #cccccc;
        background: transparent;
        padding: 0 1;
    }}
    ListItem:hover {{
        background: #222222;
        color: #ffffff;
    }}
    ListView > ListItem.--highlight {{
        background: #1a1a1a;
        color: #00ff9f;
        text-style: bold;
        border-left: thick #00ff9f;
    }}
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+r", "refresh", "Refresh", priority=True),
        Binding("enter", "activate", "Show", priority=True),
        Binding("up", "cursor_up", show=False),
        Binding("down", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("j", "cursor_down", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        if not shutil.which("tmux"):
            raise SystemExit("tmux not found. Install tmux first (apt/brew).")

        # Provided by launcher:
        self.sock   = os.environ.get("KERB_SOCK", "kerb")
        self.work   = os.environ.get("KERB_WORK", "work")
        self.view   = os.environ.get("KERB_VIEW", "view")
        self.pane_l = os.environ.get("KERB_PANE_L", "")  # LEFT pane id (e.g., %1)

        self.windows: List[WorkWindow] = []

    def compose(self) -> ComposeResult:
        with Container(id="wrap"):
            yield Static("● SESSIONS", id="title")
            self.list = ListView(id="session-list")
            yield self.list

    async def on_ready(self) -> None:
        self.action_refresh()
        self.set_focus(self.list)

    def action_refresh(self) -> None:
        self.windows = list_work_windows(self.sock, self.work)
        self.list.clear()
        if not self.windows:
            self.list.append(ListItem(Label("No windows yet", markup=False)))
            return
        for w in self.windows:
            # Avoid Rich markup parsing:
            label = f"{w.name}  [{w.index}]{' *' if w.active else ''}"
            self.list.append(ListItem(Label(label, markup=False)))

    def action_cursor_up(self) -> None:
        self.list.cursor_up()

    def action_cursor_down(self) -> None:
        self.list.cursor_down()

    def action_activate(self) -> None:
        item = self.list.highlighted_child
        if not isinstance(item, ListItem):
            return
        # Figure out which WorkWindow was highlighted
        idx = self.list.index
        if idx is None or idx < 0 or idx >= len(self.windows):
            return
        w = self.windows[idx]
        # Mirror & select on the LEFT nested client
        if self.pane_l:
            show_in_view(self.sock, self.work, self.view, self.pane_l, w.index, slot=0)

if __name__ == "__main__":
    os.environ.setdefault("TERM", "xterm-256color")
    KerberosController().run()

