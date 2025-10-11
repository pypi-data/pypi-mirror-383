#!/usr/bin/env python3
"""
Two-pane tmux launcher with a simple Textual controller on the left.

What it does:
- Creates an isolated tmux server (-L kerb), two sessions:
    * WORK: holds your real windows (code, logs, etc.)
    * VIEW: a "display" session the right pane's nested tmux client attaches to
- Creates/attaches an OUTER session with 2 panes:
    * Left  pane: runs this script in --controller mode (Textual list)
    * Right pane: runs `tmux -L kerb attach -t VIEW`
- Selecting a window in the left pane (↑/↓ then Enter) updates the right pane.
"""

import os
import sys
import time
import shlex
import argparse
import subprocess
from typing import List, Tuple

# ----------------------------- tmux helpers -----------------------------

def sh(sock: str, *args: str) -> subprocess.CompletedProcess:
    """Run tmux against a given socket; return CompletedProcess with text I/O."""
    return subprocess.run(
        ["tmux", "-L", sock, *args],
        check=False,
        capture_output=True,
        text=True,
    )

def ensure_sessions(sock: str, work: str, view: str) -> None:
    # WORK session (where your actual windows live)
    if sh(sock, "has-session", "-t", work).returncode != 0:
        sh(sock, "new-session", "-d", "-s", work, "-n", "shell")

    # VIEW session (what the right pane will attach to as a nested client)
    if sh(sock, "has-session", "-t", view).returncode != 0:
        sh(sock, "new-session", "-d", "-s", view, "-n", "view0")

def list_windows(sock: str, session: str) -> List[Tuple[int, str, bool]]:
    """
    Returns list of (index, name, active) for the given session.
    """
    out = sh(sock, "list-windows", "-t", session, "-F", "#{window_index}\t#{window_name}\t#{?window_active,1,0}")
    if out.returncode != 0:
        return []
    rows = []
    for line in out.stdout.strip().splitlines():
        if not line.strip():
            continue
        idx_s, name, active_s = line.split("\t")
        rows.append((int(idx_s), name, active_s == "1"))
    rows.sort(key=lambda r: r[0])
    return rows

def link_into_view(sock: str, work: str, view: str, idx: int) -> None:
    """Mirror WORK:idx into VIEW:idx so view can display it."""
    sh(sock, "unlink-window", "-t", f"{view}:{idx}")  # ok if absent
    sh(sock, "link-window", "-s", f"{work}:{idx}", "-t", f"{view}:{idx}")

def select_in_nested(sock: str, pane_r: str, view: str, idx: int) -> None:
    """
    Change the nested client's view by injecting a command into the right pane's shell.
    This avoids 'target-client' ambiguity and guarantees the right pane updates.
    """
    cmd = f"tmux -L {shlex.quote(sock)} select-window -t {shlex.quote(view)}:{idx}"
    sh(sock, "send-keys", "-t", pane_r, cmd, "C-m")

def split_outer(sock: str, outer: str) -> Tuple[str, str]:
    """
    Ensure OUTER session exists, split into left/right panes.
    Returns (left_pane_id, right_pane_id).
    """
    sh(sock, "new-session", "-Ad", "-s", outer, "-n", "ctrl")
    sh(sock, "switch-client", "-t", outer)
    # reset to single pane, then split
    sh(sock, "kill-pane", "-a")
    sh(sock, "split-window", "-h")
    out = sh(sock, "list-panes", "-F", "#{pane_index}\t#{pane_id}")
    panes = dict(line.split("\t") for line in out.stdout.strip().splitlines())
    left = panes.get("0")
    right = panes.get("1")
    return left, right

def send_cmd_to_pane(sock: str, pane: str, argv: List[str]) -> None:
    """
    Send a full shell command line to the pane and press Enter.
    """
    line = " ".join(shlex.quote(a) for a in argv)
    sh(sock, "send-keys", "-t", pane, line, "C-m")

# ----------------------------- Textual UI ------------------------------

# The controller is a tiny Textual app that lists WORK windows and on Enter:
# - links WORK:<idx> into VIEW:<idx>
# - tells the nested client (right pane) to select VIEW:<idx>

def run_controller(sock: str, work: str, view: str, pane_r: str) -> int:
    # Lazy import so users who only launch/attach don't need textual installed
    from textual.app import App, ComposeResult
    from textual.widgets import ListView, ListItem, Label, Static
    from textual.containers import Vertical
    from textual import on
    from textual.binding import Binding

    class ControllerApp(App):
        CSS = """
        Screen { background: #0a0a0a; color: #ddd; }
        #title { background: #111; padding: 0 1; height: 3; border-bottom: solid #333; }
        #title Static { color: #00ff9f; text-style: bold; }
        ListView { height: 1fr; }
        ListItem.--highlight { color: #00ff9f; text-style: bold; }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("r", "refresh", "Refresh"),
            Binding("enter", "activate", "Show"),
            Binding("up", "cursor_up", "Up"),
            Binding("down", "cursor_down", "Down"),
            Binding("k", "cursor_up"),
            Binding("j", "cursor_down"),
        ]

        def compose(self) -> ComposeResult:
            with Vertical():
                yield Static("Kerb Controller • ↑/↓ to select • Enter to show • r refresh • q quit", id="title")
                self.list = ListView(id="windows")
                yield self.list

        def on_mount(self) -> None:
            self.refresh_list()
            self.set_focus(self.list)

        def action_refresh(self) -> None:
            self.refresh_list()

        def refresh_list(self) -> None:
            self.list.clear()
            wins = list_windows(sock, work)
            if not wins:
                self.list.append(ListItem(Label("No windows found in WORK session")))
                return
            for idx, name, active in wins:
                label = f"[{idx}] {name}" + ("  *" if active else "")
                item = ListItem(Label(label))
                item.data = idx
                self.list.append(item)

        def action_cursor_up(self) -> None:
            self.list.cursor_up()

        def action_cursor_down(self) -> None:
            self.list.cursor_down()

        @on(ListView.Highlighted)
        def _on_highlight(self, event: ListView.Highlighted) -> None:
            # No side effects on highlight; Enter will trigger the switch.
            pass

        def action_activate(self) -> None:
            item = self.list.highlighted_child
            if not isinstance(item, ListItem) or not hasattr(item, "data"):
                return
            idx = int(item.data)
            # 1) ensure VIEW has a link for this index
            link_into_view(sock, work, view, idx)
            # 2) tell nested client to select it
            select_in_nested(sock, pane_r, view, idx)

    return ControllerApp().run()

# ----------------------------- Bootstrap -------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", action="store_true", help="Run the Textual controller UI (internal).")
    parser.add_argument("--sock", default="kerb")
    parser.add_argument("--work", default="work")
    parser.add_argument("--view", default="view")
    parser.add_argument("--outer", default="outer")
    parser.add_argument("--pane-r", default="", help="Right pane id (internal).")
    args = parser.parse_args()

    if args.controller:
        # Run the Textual UI in the left pane
        if not args.pane_r:
            print("Missing --pane-r for controller", file=sys.stderr)
            return 2
        os.environ.setdefault("TERM", "xterm-256color")
        return run_controller(args.sock, args.work, args.view, args.pane_r)

    # Launcher mode: set everything up, start panes, then ATTACH to OUTER
    sock, work, view, outer = args.sock, args.work, args.view, args.outer
    os.environ.setdefault("TERM", "xterm-256color")

    # 1) Ensure server & sessions
    ensure_sessions(sock, work, view)

    # 2) Create some demo windows in WORK so you can switch between them
    #    (skip if they already exist; tmux will just add duplicates otherwise)
    if not any(n == "code" for _, n, _ in list_windows(sock, work)):
        sh(sock, "new-window", "-t", work, "-n", "code",  "bash", "-lc", "watch -n1 ls -lah")
    if not any(n == "logs" for _, n, _ in list_windows(sock, work)):
        sh(sock, "new-window", "-t", work, "-n", "logs",  "bash", "-lc", "yes LOG | nl | sed -n '1,99999p'")

    # 3) Prepare OUTER session with two panes
    left_pane, right_pane = split_outer(sock, outer)

    # 4) Start nested client in the RIGHT pane (attaches to VIEW)
    send_cmd_to_pane(sock, right_pane, ["tmux", "-L", sock, "attach", "-t", view])

    # 5) Start our Textual controller in the LEFT pane (this script with --controller)
    script_path = os.path.abspath(sys.argv[0])
    send_cmd_to_pane(
        sock,
        left_pane,
        [sys.executable, script_path, "--controller", "--sock", sock, "--work", work, "--view", view, "--pane-r", right_pane],
    )

    # tiny delay to let both sides start
    time.sleep(0.2)

    # 6) Attach the user to OUTER (replace our process so we land *inside* tmux)
    os.execvp("tmux", ["tmux", "-L", sock, "attach", "-t", outer])

if __name__ == "__main__":
    raise SystemExit(main())

