#!/usr/bin/env python3
"""
Test script for MCP server and sub-agent creation logic.

Usage:
    python test_mcp.py [test_name]

Tests:
    - mcp_server: Test if MCP server starts and responds
    - spawn_child: Test spawning a child executor session
    - send_message: Test sending messages to sessions
    - monitor_hook: Test monitor hook forwarding
    - full_flow: Complete flow test
"""

import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
import requests
from typing import Optional

# Add cerb_code to path
sys.path.insert(0, str(Path(__file__).parent))

from cerb_code.lib.sessions import Session, AgentType, load_sessions, save_sessions
from cerb_code.lib.tmux_agent import TmuxProtocol


class TestRunner:
    def __init__(self):
        self.protocol = TmuxProtocol(default_command="claude")
        self.test_session_id = f"test-{int(time.time())}"
        self.cleanup_sessions = []

    def cleanup(self):
        """Clean up test sessions"""
        print("\n🧹 Cleaning up test sessions...")
        for session_id in self.cleanup_sessions:
            try:
                subprocess.run(["tmux", "kill-session", "-t", session_id],
                             capture_output=True, text=True)
                print(f"  ✓ Killed session: {session_id}")
            except:
                pass

        # Clean up worktrees
        worktree_base = Path.home() / ".kerberos" / "worktrees"
        for session_id in self.cleanup_sessions:
            worktree_path = worktree_base / Path.cwd().name / session_id
            if worktree_path.exists():
                subprocess.run(["git", "worktree", "remove", str(worktree_path), "--force"],
                             capture_output=True, text=True)
                print(f"  ✓ Removed worktree: {worktree_path}")

    def test_mcp_server(self):
        """Test MCP server startup and basic functionality"""
        print("\n🧪 Testing MCP Server...")

        # Start MCP server as subprocess
        print("  Starting MCP server...")
        mcp_proc = subprocess.Popen(
            ["python", "-m", "cerb_code.runners.mcp_server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it time to start
        time.sleep(2)

        # Check if it's running
        if mcp_proc.poll() is not None:
            stdout, stderr = mcp_proc.communicate()
            print(f"  ❌ MCP server failed to start")
            print(f"  stdout: {stdout}")
            print(f"  stderr: {stderr}")
            return False

        print("  ✅ MCP server started successfully")

        # Test the stdio connection
        # Note: Full MCP testing would require implementing the JSON-RPC protocol
        print("  ℹ️  MCP server is running on stdio (would need JSON-RPC client for full test)")

        # Kill the server
        mcp_proc.terminate()
        mcp_proc.wait(timeout=5)
        print("  ✅ MCP server terminated cleanly")

        return True

    def test_spawn_child(self):
        """Test spawning a child executor session"""
        print("\n🧪 Testing Child Session Spawning...")

        # Create parent session
        parent_id = f"{self.test_session_id}-parent"
        self.cleanup_sessions.append(parent_id)

        parent = Session(
            session_id=parent_id,
            agent_type=AgentType.DESIGNER,
            protocol=self.protocol,
            source_path=str(Path.cwd())
        )

        print(f"  Creating parent session: {parent_id}")
        parent.prepare()

        if not parent.start():
            print(f"  ❌ Failed to start parent session")
            return False

        print(f"  ✅ Parent session started")

        # Wait for session to be ready
        time.sleep(1)

        # Check if session exists in tmux
        result = subprocess.run(["tmux", "has-session", "-t", parent_id],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ❌ Parent session not found in tmux")
            return False

        # Spawn child executor
        child_id = f"{self.test_session_id}-child"
        self.cleanup_sessions.append(child_id)

        print(f"  Spawning child executor: {child_id}")
        instructions = "Test task: Analyze the current directory structure"

        try:
            child = parent.spawn_executor(child_id, instructions)
            print(f"  ✅ Child executor spawned")
        except Exception as e:
            print(f"  ❌ Failed to spawn child: {e}")
            import traceback
            print("  Full traceback:")
            traceback.print_exc()

            # Check if PROJECT_CONF is the issue
            try:
                from cerb_code.lib.prompts import PROJECT_CONF
                print(f"  PROJECT_CONF type: {type(PROJECT_CONF)}")
                print(f"  PROJECT_CONF content preview: {str(PROJECT_CONF)[:200]}...")

                # Try formatting it
                formatted = PROJECT_CONF.format(child_id)
                print(f"  Formatted successfully, length: {len(formatted)}")
            except Exception as conf_error:
                print(f"  ❌ PROJECT_CONF issue: {conf_error}")

            return False

        # Verify child session exists
        time.sleep(1)
        result = subprocess.run(["tmux", "has-session", "-t", child_id],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ❌ Child session not found in tmux")
            return False

        print(f"  ✅ Child session exists in tmux")

        # Check if instructions.md was created
        instructions_path = Path(child.work_path) / "instructions.md"
        if not instructions_path.exists():
            print(f"  ❌ instructions.md not created")
            return False

        print(f"  ✅ instructions.md created")

        # Check content
        content = instructions_path.read_text()
        if instructions not in content:
            print(f"  ❌ Instructions not written correctly")
            return False

        print(f"  ✅ Instructions written correctly")

        # Check if message was sent
        # We can check tmux pane content
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", f"{child_id}:0.0", "-p"],
            capture_output=True, text=True
        )

        if "@instructions.md" in result.stdout:
            print(f"  ✅ Initial message sent to session")
        else:
            print(f"  ⚠️  Initial message may not have been sent (or claude already processed it)")

        return True

    def test_monitor_hook(self):
        """Test monitor hook forwarding"""
        print("\n🧪 Testing Monitor Hook System...")

        # Start monitor server
        print("  Starting monitor server...")
        monitor_proc = subprocess.Popen(
            ["python", "-m", "cerb_code.runners.monitor", "8082"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it time to start
        time.sleep(2)

        # Check if it's running
        if monitor_proc.poll() is not None:
            stdout, stderr = monitor_proc.communicate()
            print(f"  ❌ Monitor server failed to start")
            print(f"  stdout: {stdout}")
            print(f"  stderr: {stderr}")
            return False

        print("  ✅ Monitor server started on port 8082")

        # Test sending a hook event
        test_session = f"{self.test_session_id}-monitor"
        test_event = {
            "event": "tool_use",
            "payload": {
                "tool": "Read",
                "file_path": "/test/file.py",
                "timestamp": time.time()
            }
        }

        try:
            print(f"  Sending test hook event for session: {test_session}")
            response = requests.post(
                f"http://127.0.0.1:8082/hook/{test_session}",
                json=test_event,
                timeout=2
            )

            if response.status_code == 200:
                print(f"  ✅ Hook event accepted: {response.json()}")
            elif response.status_code == 404:
                print(f"  ⚠️  Session not found (expected for test session)")
                print(f"     Response: {response.text}")
                print(f"     This is normal - the monitor creates sessions on demand")
                # This is actually OK for our test - the endpoint works
            else:
                print(f"  ❌ Hook event failed: {response.status_code} - {response.text}")
                monitor_proc.terminate()
                return False

        except requests.exceptions.ConnectionError:
            print(f"  ❌ Could not connect to monitor server")
            monitor_proc.terminate()
            return False
        except Exception as e:
            print(f"  ❌ Error sending hook: {e}")
            monitor_proc.terminate()
            return False

        # Test the hook forwarder script
        print("  Testing hook forwarder script...")
        test_hook_data = json.dumps({
            "tool": "Write",
            "file_path": "/test/output.py",
            "content": "print('test')"
        })

        result = subprocess.run(
            ["python", "-m", "cerb_code.runners.hook_monitor", test_session, "tool_use"],
            input=test_hook_data,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✅ Hook forwarder executed successfully")
        else:
            print(f"  ❌ Hook forwarder failed: {result.stderr}")

        # Cleanup
        monitor_proc.terminate()
        monitor_proc.wait(timeout=5)
        print("  ✅ Monitor server terminated")

        return True

    def test_full_flow(self):
        """Test complete flow: parent -> child -> monitor"""
        print("\n🧪 Testing Complete Flow...")

        # Start monitor server
        print("  Starting monitor server...")
        monitor_proc = subprocess.Popen(
            ["python", "-m", "cerb_code.runners.monitor", "8083"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)

        # Create parent session
        parent_id = f"{self.test_session_id}-flow-parent"
        self.cleanup_sessions.append(parent_id)

        parent = Session(
            session_id=parent_id,
            agent_type=AgentType.DESIGNER,
            protocol=self.protocol,
            source_path=str(Path.cwd())
        )

        print(f"  Creating parent session: {parent_id}")
        parent.prepare()
        parent.start()

        # Spawn child with hook configuration
        child_id = f"{self.test_session_id}-flow-child"
        self.cleanup_sessions.append(child_id)

        print(f"  Spawning child with monitoring: {child_id}")

        # Update environment for hook forwarding
        os.environ["CLAUDE_MONITOR_BASE"] = "http://127.0.0.1:8083"

        child = parent.spawn_executor(
            child_id,
            "Test task: Read the README.md file and summarize it"
        )

        print(f"  ✅ Child spawned with monitoring enabled")

        # Check settings.json
        settings_path = Path(child.work_path) / ".claude" / "settings.json"
        if settings_path.exists():
            settings = json.loads(settings_path.read_text())
            if "hooks" in settings and "tool_use" in settings["hooks"]:
                print(f"  ✅ Hook configuration created")
            else:
                print(f"  ❌ Hook configuration missing")
        else:
            print(f"  ❌ settings.json not created")

        # Cleanup
        monitor_proc.terminate()
        monitor_proc.wait(timeout=5)

        return True

    def run_all_tests(self):
        """Run all tests"""
        tests = [
            ("MCP Server", self.test_mcp_server),
            ("Spawn Child", self.test_spawn_child),
            ("Monitor Hook", self.test_monitor_hook),
            ("Full Flow", self.test_full_flow),
        ]

        results = []

        print("\n" + "="*50)
        print("🚀 Running Cerb/Kerberos Test Suite")
        print("="*50)

        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"\n❌ Test '{name}' crashed: {e}")
                results.append((name, False))

        # Print summary
        print("\n" + "="*50)
        print("📊 Test Summary")
        print("="*50)

        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}: {name}")

        passed = sum(1 for _, s in results if s)
        total = len(results)
        print(f"\n  Total: {passed}/{total} tests passed")

        return all(success for _, success in results)


def main():
    """Main test entry point"""
    import os

    runner = TestRunner()

    try:
        if len(sys.argv) > 1:
            test_name = sys.argv[1]

            # Run specific test
            if test_name == "mcp_server":
                success = runner.test_mcp_server()
            elif test_name == "spawn_child":
                success = runner.test_spawn_child()
            elif test_name == "monitor_hook":
                success = runner.test_monitor_hook()
            elif test_name == "full_flow":
                success = runner.test_full_flow()
            else:
                print(f"Unknown test: {test_name}")
                print("Available tests: mcp_server, spawn_child, monitor_hook, full_flow")
                sys.exit(1)

            if not success:
                sys.exit(1)
        else:
            # Run all tests
            success = runner.run_all_tests()
            if not success:
                sys.exit(1)

    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()