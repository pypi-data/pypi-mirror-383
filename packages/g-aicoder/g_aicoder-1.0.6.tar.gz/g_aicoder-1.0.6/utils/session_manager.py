#!/usr/bin/env python3
"""
Session management module for Cline Clone
Handles conversation history, workspace persistence, and state management
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class SessionManager:
    """Manages conversation history and workspace state"""

    def __init__(self, session_dir: str = ".cline_sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.current_session = None
        self.load_default_session()

    def load_default_session(self):
        """Load or create default session"""
        self.current_session = {
            "id": "default",
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "conversation": [],
            "workspace": {
                "cwd": str(Path.cwd()),
                "open_files": [],
                "recent_commands": [],
                "bookmarks": []
            }
        }
        self.load_session("default")

    def load_session(self, session_id: str) -> bool:
        """Load a specific session from disk"""
        session_file = self.session_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    self.current_session = json.load(f)
                return True
            except Exception as e:
                print(f"[Warning] Failed to load session {session_id}: {e}")
        return False

    def save_session(self) -> bool:
        """Save current session to disk"""
        if not self.current_session:
            return False

        session_file = self.session_dir / f"{self.current_session['id']}.json"
        try:
            # Update last active time
            self.current_session["last_active"] = datetime.now().isoformat()

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Warning] Failed to save session: {e}")
            return False

    def create_session(self, session_id: str, description: str = "") -> bool:
        """Create a new session"""
        if self.session_exists(session_id):
            return False

        self.current_session = {
            "id": session_id,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "conversation": [],
            "workspace": {
                "cwd": str(Path.cwd()),
                "open_files": [],
                "recent_commands": [],
                "bookmarks": []
            }
        }
        return self.save_session()

    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        if session_id == self.current_session["id"]:
            return True  # Already current

        # Save current session first
        self.save_session()

        if self.load_session(session_id):
            return True

        # Create new session if it doesn't exist
        return self.create_session(session_id)

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        session_file = self.session_dir / f"{session_id}.json"
        return session_file.exists()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions = []
        if self.session_dir.exists():
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception:
                    continue
        return sessions

    def add_conversation_entry(self, user_msg: str, ai_response: str, metadata: Dict[str, Any] = None):
        """Add a conversation entry to current session"""
        if not self.current_session:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "assistant": ai_response,
            "metadata": metadata or {}
        }

        self.current_session["conversation"].append(entry)

        # Keep only last 50 conversations in memory for performance
        if len(self.current_session["conversation"]) > 50:
            # But save them to disk
            self.save_session()
            # Keep last 20 in memory
            self.current_session["conversation"] = self.current_session["conversation"][-20:]

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        if not self.current_session or not self.current_session["conversation"]:
            return []

        # If we have less than limit saved, return recent
        if len(self.current_session["conversation"]) <= limit:
            return self.current_session["conversation"][-limit:]

        # Otherwise, load from disk and get recent
        full_session = self.load_full_session()
        return full_session["conversation"][-limit:]

    def load_full_session(self) -> Dict[str, Any]:
        """Load complete session from disk"""
        session_id = self.current_session["id"]
        session_file = self.session_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.current_session
        return self.current_session

    def update_workspace(self, key: str, value: Any):
        """Update workspace state"""
        if self.current_session and "workspace" in self.current_session:
            self.current_session["workspace"][key] = value
            self.save_session()

    def get_workspace(self, key: str, default: Any = None) -> Any:
        """Get workspace value"""
        if self.current_session and "workspace" in self.current_session:
            return self.current_session["workspace"].get(key, default)
        return default

    def add_recent_command(self, command: str):
        """Add command to recent commands list"""
        if self.current_session:
            recent = self.current_session["workspace"]["recent_commands"]
            if command in recent:
                recent.remove(command)
            recent.append(command)
            # Keep only last 20
            self.current_session["workspace"]["recent_commands"] = recent[-20:]
            self.save_session()

    def get_recent_commands(self, limit: int = 5) -> List[str]:
        """Get recent commands"""
        if self.current_session:
            return self.current_session["workspace"]["recent_commands"][-limit:]
        return []

    def bookmark_path(self, path: str, alias: str = None):
        """Bookmark a file or directory path"""
        if self.current_session:
            if alias is None:
                alias = Path(path).name

            bookmark = {"alias": alias, "path": path, "added": datetime.now().isoformat()}
            self.current_session["workspace"]["bookmarks"].append(bookmark)
            self.save_session()

    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Get all bookmarks"""
        if self.current_session:
            return self.current_session["workspace"]["bookmarks"]
        return []

    def search_conversation(self, query: str) -> List[Dict[str, Any]]:
        """Search conversation history for a query"""
        full_session = self.load_full_session()
        matches = []

        for entry in full_session["conversation"]:
            if query.lower() in entry["user"].lower() or query.lower() in entry["assistant"].lower():
                matches.append(entry)

        return matches

    def cleanup_old_sessions(self, days: int = 30):
        """Remove sessions older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for session_file in self.session_dir.glob("*.json"):
            try:
                if session_file.stat().st_mtime < cutoff_date:
                    session_file.unlink()
                    print(f"Removed old session: {session_file.stem}")
            except Exception:
                continue

    def export_session(self, output_file: str) -> bool:
        """Export current session to a file"""
        try:
            full_session = self.load_full_session()
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(full_session, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def import_session(self, session_file: str, new_session_id: str) -> bool:
        """Import session from exported file"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Update session ID and timestamps
            session_data["id"] = new_session_id
            session_data["imported"] = datetime.now().isoformat()

            # Save as new session
            new_session_file = self.session_dir / f"{new_session_id}.json"
            with open(new_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False


class CommandHistory:
    """Manages command history with navigation"""

    def __init__(self):
        self.history = []
        self.history_index = -1
        self.temp_command = ""

    def add_command(self, command: str):
        """Add command to history"""
        if command and command.strip():
            # Don't add duplicates of last command
            if not self.history or self.history[-1] != command:
                self.history.append(command)
                # Keep only last 100 commands
                if len(self.history) > 100:
                    self.history = self.history[-100:]
        self.history_index = -1
        self.temp_command = ""

    def get_previous(self, current_command: str = "") -> str:
        """Get previous command in history"""
        if not self.history:
            return current_command

        if self.history_index == -1:
            self.temp_command = current_command
            self.history_index = len(self.history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)

        return self.history[self.history_index]

    def get_next(self) -> str:
        """Get next command in history"""
        if not self.history or self.history_index == -1:
            return self.temp_command

        self.history_index += 1

        if self.history_index >= len(self.history):
            self.history_index = -1
            return self.temp_command

        return self.history[self.history_index]

    def reset_navigation(self):
        """Reset navigation state"""
        self.history_index = -1
        self.temp_command = ""

    def search_history(self, query: str) -> List[str]:
        """Search command history"""
        return [cmd for cmd in self.history if query.lower() in cmd.lower()]
