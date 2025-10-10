import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class DaziStore:
    """
    Persistence layer for vibeDazi team-shared logs.

    Directory layout (under workspace root):
      .vibe-dazi/
        index.jsonl                    # one JSON object per line, append-only
        rounds/
          YYYY-MM/
            round-<session>-<n>.json  # detailed round events
    """

    def __init__(self, workspace_dir: str) -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.root_dir = self.workspace_dir / ".vibe-dazi"
        self.rounds_dir = self.root_dir / "rounds"
        self.index_file = self.root_dir / "index.jsonl"

    # ---------- filesystem helpers ----------
    def init(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.rounds_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.touch()

    def _month_dir(self, dt: datetime) -> Path:
        return self.rounds_dir / dt.strftime("%Y-%m")

    # ---------- sessions/rounds ----------
    def start_round(self, session_id: Optional[str], session_hint: Optional[str]) -> Dict[str, Any]:
        if not session_id:
            # new session id: date + random suffix
            session_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            if session_hint:
                session_id = f"{session_id}-{session_hint}"
        # naive unique round id using timestamp + monotonic suffix per start
        round_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
        return {"session_id": session_id, "round_id": round_id}

    def append_event(self, round_id: str, event: Dict[str, Any]) -> None:
        # temp accumulate events in memory via callers; no-op placeholder to keep parity
        pass

    def save_round(self, *,
                   session_id: str,
                   round_id: str,
                   status: str,
                   user: Dict[str, Any],
                   git: Dict[str, Any],
                   prompt: Dict[str, Any],
                   diffs: List[Dict[str, Any]],
                   events: List[Dict[str, Any]],
                   commits_since_last: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        self.init()
        now = datetime.utcnow()
        month_dir = self._month_dir(now)
        month_dir.mkdir(parents=True, exist_ok=True)

        filename = month_dir / f"round-{session_id}-{now.strftime('%d-%H%M%S')}.json"
        round_doc = {
            "round_id": round_id,
            "session_id": session_id,
            "recorded_at": now.isoformat(timespec="milliseconds") + "Z",
            "status": status,
            "user": user,            # { name, email }
            "git": git,              # { branch, commit, repo }
            "prompt": prompt,        # { text, model?, meta? }
            "diffs": diffs,          # [ { path, base_commit, head_commit, unified_diff } ]
            "events": events,        # chronological event list
        }
        if commits_since_last is not None:
            round_doc["commits_since_last"] = commits_since_last

        with filename.open("w", encoding="utf-8") as f:
            json.dump(round_doc, f, ensure_ascii=False, indent=2)

        # append a compact index line for fast scan
        index_line = {
            "round_id": round_id,
            "session_id": session_id,
            "ts": round_doc["recorded_at"],
            "status": status,
            "user": user,
            "git": {k: git.get(k) for k in ("branch", "commit", "repo")},
            "file_count": len(diffs),
            "event_count": len(events),
            "path": str(filename.relative_to(self.root_dir)),
        }
        with self.index_file.open("a", encoding="utf-8") as idx:
            idx.write(json.dumps(index_line, ensure_ascii=False) + "\n")

        return {"saved_file": str(filename)}

    # ---------- queries ----------
    def query_index(self, *,
                    branch: Optional[str] = None,
                    user_name: Optional[str] = None,
                    session_id: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Filter index.jsonl for quick alignment context."""
        self.init()
        results: List[Dict[str, Any]] = []
        if not self.index_file.exists():
            return results
        with self.index_file.open("r", encoding="utf-8") as f:
            for line in reversed(list(f)):
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if branch and (obj.get("git", {}).get("branch") != branch):
                    continue
                if user_name and (obj.get("user", {}).get("name") != user_name):
                    continue
                if session_id and (obj.get("session_id") != session_id):
                    continue
                results.append(obj)
                if len(results) >= limit:
                    break
        return results

    def get_last_index_entry(self) -> Optional[Dict[str, Any]]:
        """Return the most recent index row or None."""
        self.init()
        if not self.index_file.exists():
            return None
        try:
            with self.index_file.open("r", encoding="utf-8") as f:
                lines = [ln for ln in f if ln.strip()]
            if not lines:
                return None
            return json.loads(lines[-1])
        except Exception:
            return None


