import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import fnmatch

from mcp.server import FastMCP

from .store import DaziStore


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


app = FastMCP(name="vibedazi-mcp")


def _git_output(args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def _repo_root() -> str:
    # Prefer git to locate repository root; fallback to CWD
    root = _git_output(["rev-parse", "--show-toplevel"]) or "."
    return root


store = DaziStore(_repo_root())

# -------------------- Configuration --------------------
DEFAULT_CONFIG: Dict[str, Any] = {
    "log": {
        "ignore_paths": [
            ".vibe-dazi/rounds/**",
            "**/__pycache__/**",
            "**/*.egg-info/**",
            ".venv*/**",
            "**/.venv*/**",
            ".specstory/**",
        ],
        "max_events": 200,
        "per_file_diff_max_bytes": 120000,
        "snapshot_max_bytes": 240000,
        "snapshot_enabled": True,
        "include_commits_since_last": True,
    },
    "ai_squash_merge": {
        "model_name": None,
        "author_name": None,
        "author_email": None,
        "base_branch": None,
        "include_untracked": True,
        "co_author_trailer": True,
        "delete_ai_branch": True,
        "set_committer_to_ai": False,
        "auto_stash": False,
        "squash_author_is_ai": True,
        "exclude_paths": [
            ".vibe-dazi/index.jsonl",
            ".vibe-dazi/rounds/**",
            "**/__pycache__/**",
            "**/*.egg-info/**",
            ".venv*/**",
            "**/.venv*/**",
            ".specstory/**",
        ],
    },
    "flight_log": {
        "enabled": True,
        "path": ".vibe-dazi/flight-log.md",
        "auto_commit": True,
        "auto_append_on_log_round": False,
    },
}


def _config_path() -> Path:
    return store.root_dir / "config.json"


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def _load_config() -> Dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = _config_path()
    try:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            if isinstance(user_cfg, dict):
                _deep_merge(cfg, user_cfg)
    except Exception:
        # ignore invalid config, stick to defaults
        pass
    return cfg


def _model_identity(model_name: Optional[str]) -> Dict[str, Optional[str]]:
    if not model_name:
        return {"name": None, "email": None}
    label = (model_name or "").strip()
    low = label.lower()
    if ("gpt" in low) or ("openai" in low):
        return {"name": label, "email": "noreply@openai.com"}
    if ("claude" in low) or ("anthropic" in low):
        return {"name": label, "email": "noreply@anthropic.com"}
    if ("gemini" in low) or ("google" in low) or ("palm" in low):
        return {"name": label, "email": "noreply@google.com"}
    if ("llama" in low) or ("meta" in low):
        return {"name": label, "email": "noreply@meta.com"}
    if ("grok" in low) or ("xai" in low) or ("x.ai" in low):
        return {"name": label, "email": "noreply@x.ai"}
    if "mistral" in low:
        return {"name": label, "email": "noreply@mistral.ai"}
    if "cohere" in low:
        return {"name": label, "email": "noreply@cohere.com"}
    if "deepseek" in low:
        return {"name": label, "email": "noreply@deepseek.com"}
    return {"name": label, "email": "noreply@ai.local"}


def _flight_log_path() -> Path:
    cfg = _load_config().get("flight_log", {})
    p = cfg.get("path") or ".vibe-dazi/flight-log.md"
    return (store.workspace_dir / p).resolve()


def _ensure_flight_log_file() -> None:
    fp = _flight_log_path()
    fp.parent.mkdir(parents=True, exist_ok=True)
    if not fp.exists():
        with fp.open("w", encoding="utf-8") as f:
            f.write("# Flight Log\n\n")
            f.write(
                "Human-readable running changelog. Highest-signal items first, grouped by day.\n\n"
            )


def _append_flight_log_entry(*, headline: str, level: str, details: Optional[str], scope: Optional[str], labels: Optional[List[str]], related_paths: Optional[List[str]], round_id: Optional[str]) -> Dict[str, Any]:
    cfg = _load_config().get("flight_log", {})
    if not bool(cfg.get("enabled", True)):
        return {"status": "disabled"}
    level = (level or "medium").strip().lower()
    if level not in ("low", "medium", "high", "breaking"):
        level = "medium"
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%SZ")
    fp = _flight_log_path()
    _ensure_flight_log_file()

    # Read current content
    try:
        with fp.open("r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    # Ensure a section for today exists
    day_header = f"## {date_str}"
    if day_header not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += f"{day_header}\n\n"

    # Build entry
    badge = {
        "breaking": "[BREAKING]",
        "high": "[HIGH]",
        "medium": "[MED]",
        "low": "[LOW]",
    }[level]
    line = f"- {time_str} {badge} {headline.strip()}"
    if scope:
        line += f" — {scope.strip()}"
    blocks: List[str] = [line]
    meta_lines: List[str] = []
    if labels:
        meta_lines.append("labels: " + ", ".join(sorted(set([str(x) for x in labels]))))
    if related_paths:
        # trim to reasonable count
        short = related_paths[:10]
        if len(related_paths) > 10:
            short.append("…")
        meta_lines.append("files: " + ", ".join(short))
    if round_id:
        meta_lines.append(f"round: {round_id}")
    if details:
        blocks.append(f"  - {details.strip()}")
    for ml in meta_lines:
        blocks.append(f"  - {ml}")

    entry = "\n".join(blocks) + "\n"

    # Insert entry under today's section (append at end of that section)
    if day_header in content:
        parts = content.split(day_header)
        head = parts[0]
        rest = day_header.join(parts[1:])
        # rest starts with the actual section content
        new_content = head + day_header + rest
        # Place entry right after the day header if the day section is empty
        idx = new_content.find(day_header)
        idx_end = idx + len(day_header)
        # Find the next day header to append before it; otherwise append at end
        next_idx = new_content.find("\n## ", idx_end)
        if next_idx == -1:
            # append to end
            if not new_content.endswith("\n"):
                new_content += "\n"
            new_content += entry
        else:
            # insert before next header
            before = new_content[:next_idx]
            after = new_content[next_idx:]
            if not before.endswith("\n"):
                before += "\n"
            new_content = before + entry + after
    else:
        new_content = content + entry

    with fp.open("w", encoding="utf-8") as f:
        f.write(new_content)

    committed = None
    if bool(cfg.get("auto_commit", True)):
        _run_git(["add", "--", str(fp.relative_to(store.workspace_dir))])
        msg = f"docs(flight): {level} {headline.strip()}"
        # Use AI model identity for author if available
        mcfg = _load_config().get("ai_squash_merge", {})
        ident = _model_identity(mcfg.get("model_name"))
        name = ident.get("name")
        email = ident.get("email")
        if name and email:
            gc = _run_git(["commit", "--author", f"{name} <{email}>", "-m", msg])
        else:
            gc = _run_git(["commit", "-m", msg])
        if gc.get("code") == 0:
            committed = _git_output(["rev-parse", "HEAD"]) or None

    return {"status": "ok", "file": str(fp), "committed": committed}


def _match_any(path: str, patterns: List[str]) -> bool:
    p = str(Path(path)).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    for pat in patterns or []:
        if fnmatch.fnmatch(p, pat):
            return True
    return False


def _get_git_context() -> Dict[str, Any]:
    branch = _git_output(["rev-parse", "--abbrev-ref", "HEAD"]) or None
    commit = _git_output(["rev-parse", "HEAD"]) or None
    repo = _git_output(["rev-parse", "--show-toplevel"]) or None
    user_name = _git_output(["config", "user.name"]) or None
    user_email = _git_output(["config", "user.email"]) or None
    # derive display name from email when name is missing
    def _derive_name_from_email(email: Optional[str]) -> Optional[str]:
        if not email or "@" not in email:
            return None
        local = email.split("@", 1)[0]
        local = local.split("+", 1)[0]
        tmp = local.replace(".", " ").replace("_", " ").replace("-", " ")
        tokens = [t for t in tmp.split(" ") if t]
        if not tokens:
            return local
        return " ".join(t.capitalize() for t in tokens)

    if not user_name and user_email:
        user_name = _derive_name_from_email(user_email)

    return {
        "branch": branch,
        "commit": commit,
        "repo": repo,
        "user": {"name": user_name, "email": user_email},
    }


def _should_ignore_path(path: str) -> bool:
    """Return True if a path should be excluded from diffs/snapshots."""
    cfg = _load_config()
    p = str(Path(path)).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    for pat in cfg.get("log", {}).get("ignore_paths", []) or []:
        if fnmatch.fnmatch(p, pat):
            return True
    return False


def _collect_diffs(paths: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Collect unified diffs for provided paths or current workspace changes.

    Handles both tracked and untracked files and works even when the repo has
    no commits yet by falling back to `git diff --no-index`.
    """
    if not paths:
        name_only = set()
        # unstaged and staged changes
        for cmd in (["diff", "--name-only"], ["diff", "--name-only", "--cached"]):
            for p in _git_output(cmd).splitlines():
                if p and not _should_ignore_path(p):
                    name_only.add(p)
        # untracked files
        for p in _git_output(["ls-files", "--others", "--exclude-standard"]).splitlines():
            if p and not _should_ignore_path(p):
                name_only.add(p)
        paths = sorted(name_only)

    diffs: List[Dict[str, Any]] = []
    head_commit = _git_output(["rev-parse", "HEAD"]) or None
    base_commit = _git_output(["merge-base", "HEAD", "HEAD"]) or head_commit

    def tracked(path: str) -> bool:
        try:
            subprocess.check_output(["git", "ls-files", "--error-unmatch", path], stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    for p in paths:
        if _should_ignore_path(p):
            continue
        udiff = ""
        # Try normal diff for tracked changes
        if tracked(p):
            cp = subprocess.run(["git", "diff", "--", p], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
            udiff = cp.stdout or ""
        # If no output (possibly untracked or identical), use no-index fallback
        if not udiff:
            path_obj = Path(p)
            if path_obj.exists():
                # new or modified file not staged/tracked
                cp = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", p], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                udiff = cp.stdout or ""
            else:
                # deleted file
                cp = subprocess.run(["git", "diff", "--no-index", "--", p, "/dev/null"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                udiff = cp.stdout or ""

        # Trim large diffs per file
        cfg = _load_config()
        max_bytes = int(cfg.get("log", {}).get("per_file_diff_max_bytes", 120000) or 0)
        if max_bytes and len(udiff.encode("utf-8")) > max_bytes:
            udiff = udiff.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore") + "\n...<truncated>\n"

        diffs.append({
            "path": p,
            "base_commit": base_commit,
            "head_commit": head_commit,
            "unified_diff": udiff,
        })
    return diffs


def _collect_commits_since(commit_ref: Optional[str]) -> List[Dict[str, Any]]:
    """Return commits since the given commit (exclusive), categorized by likely author type."""
    if not commit_ref:
        # if no baseline, show last 5 commits as context
        log_range = ["-n", "5"]
    else:
        log_range = [f"{commit_ref}..HEAD"]
    try:
        out = subprocess.check_output(["git", "log", "--pretty=format:%H%x1f%an%x1f%ae%x1f%ad%x1f%s", *log_range]).decode()
    except Exception:
        return []
    commits: List[Dict[str, Any]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) < 5:
            continue
        sha, author, email, date, subject = parts[:5]
        category = "human"
        low = (author + " " + email + " " + subject).lower()
        if "ai(" in low or "claude" in low or "gpt" in low or "copilot" in low:
            category = "ai"
        commits.append({
            "sha": sha,
            "author": author,
            "email": email,
            "date": date,
            "subject": subject,
            "category": category,
        })
    return commits


def _validate_log_round(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload.get("user_message"):
        raise ValueError("user_message is required")
    assistant_messages = payload.get("assistant_messages") or []
    if not isinstance(assistant_messages, list) or not assistant_messages:
        raise ValueError("assistant_messages must be a non-empty list of strings")
    cfg = _load_config()
    # Limit total events per round from config
    file_views = payload.get("file_views") or []
    file_writes = payload.get("file_writes") or []
    tool_calls = payload.get("tool_calls") or []
    total = 1 + len(assistant_messages) + len(file_views) + len(file_writes) + len(tool_calls)
    max_events = int(cfg.get("log", {}).get("max_events", 200) or 0)
    if max_events and total > max_events:
        raise ValueError(f"too many events in one round (max {max_events})")

    return {
        "user_message": str(payload["user_message"]),
        "assistant_messages": [str(m) for m in assistant_messages],
        "session_id": payload.get("session_id"),
        "session_hint": payload.get("session_hint"),
        "file_views": file_views,
        "file_writes": file_writes,
        "tool_calls": tool_calls,
        "status": payload.get("status") or "ok",
        "prompt_text": payload.get("prompt_text") or "",
        "prompt_meta": payload.get("prompt_meta") or {},
    }


@app.tool()
def log_round(
    user_message: str,
    assistant_messages: List[str],
    session_id: Optional[str] = None,
    session_hint: Optional[str] = None,
    file_views: Optional[List[str]] = None,
    file_writes: Optional[List[str]] = None,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    status: str = "ok",
    prompt_text: Optional[str] = None,
    prompt_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record a conversation round with team context:
    - who: git user
    - when: timestamp in events
    - where: branch/commit/repo
    - what: file diffs and tool/file events
    - why: original prompt_text
    """
    v = _validate_log_round({
        "user_message": user_message,
        "assistant_messages": assistant_messages,
        "session_id": session_id,
        "session_hint": session_hint,
        "file_views": file_views,
        "file_writes": file_writes,
        "tool_calls": tool_calls,
        "status": status,
        "prompt_text": prompt_text,
        "prompt_meta": prompt_meta,
    })

    # session/round ids
    round_info = store.start_round(v["session_id"], v["session_hint"])
    round_id = round_info["round_id"]
    sess_id = round_info["session_id"]

    # time-sequenced events
    base = datetime.utcnow()
    seq = 0
    def next_ts() -> str:
        nonlocal seq
        t = (base + timedelta(milliseconds=seq)).isoformat(timespec="milliseconds") + "Z"
        seq += 1
        return t

    events: List[Dict[str, Any]] = []
    events.append({"ts": next_ts(), "type": "user_message", "content": v["user_message"], "meta": v["prompt_meta"]})
    for msg in v["assistant_messages"]:
        events.append({"ts": next_ts(), "type": "assistant_message", "content": msg})
    for p in v["file_views"]:
        events.append({"ts": next_ts(), "type": "file_view", "path": p})
    for p in v["file_writes"]:
        events.append({"ts": next_ts(), "type": "file_write", "path": p})
    for tc in v["tool_calls"]:
        ev = {"ts": next_ts(), "type": "tool_call", "name": tc.get("name")}
        if "args_summary" in tc:
            ev["args_summary"] = tc["args_summary"]
        events.append(ev)

    git_ctx = _get_git_context()
    user_ctx = git_ctx.get("user") or {"name": None, "email": None}
    diffs = _collect_diffs(v["file_writes"])  # focus diffs to touched files if provided

    # enrich with diffs since last log and commit categorization
    last = store.get_last_index_entry()
    last_commit = (last or {}).get("git", {}).get("commit")
    cfg = _load_config()
    commits_since = _collect_commits_since(last_commit) if cfg.get("log", {}).get("include_commits_since_last", True) else []
    # Build a unified diff snapshot since last log across all changed files (tracked+untracked)
    try:
        changed = set()
        for cmd in (["diff", "--name-only"], ["diff", "--name-only", "--cached"]):
            for p in _git_output(cmd).splitlines():
                if p and not _should_ignore_path(p):
                    changed.add(p)
        for p in _git_output(["ls-files", "--others", "--exclude-standard"]).splitlines():
            if p and not _should_ignore_path(p):
                changed.add(p)
        agg = []
        for p in sorted(changed):
            # concatenate individual diffs so the snapshot gives content
            part = ""
            cp = subprocess.run(["git", "diff", "--", p], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
            part = cp.stdout or ""
            if not part:
                if Path(p).exists():
                    cp = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", p], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                    part = cp.stdout or ""
                else:
                    cp = subprocess.run(["git", "diff", "--no-index", "--", p, "/dev/null"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                    part = cp.stdout or ""
            if part:
                agg.append(part)
        udiff = "\n".join(agg)
        snap_max = int(cfg.get("log", {}).get("snapshot_max_bytes", 240000) or 0)
        if snap_max and len(udiff.encode("utf-8")) > snap_max:
            udiff = udiff.encode("utf-8")[:snap_max].decode("utf-8", errors="ignore") + "\n...<truncated>\n"
    except Exception:
        udiff = ""
    diffs_since = [{
        "path": "<since_last_log>",
        "base_commit": last_commit,
        "head_commit": git_ctx.get("commit"),
        "unified_diff": udiff,
    }]

    saved = store.save_round(
        session_id=sess_id,
        round_id=round_id,
        status=v["status"],
        user=user_ctx,
        git={"branch": git_ctx.get("branch"), "commit": git_ctx.get("commit"), "repo": git_ctx.get("repo")},
        prompt={"text": v["prompt_text"], "meta": v["prompt_meta"]},
        diffs=diffs + diffs_since,
        events=events,
        commits_since_last=commits_since,
    )

    # Optionally append a stub entry to Flight Log
    cfg = _load_config()
    if cfg.get("flight_log", {}).get("auto_append_on_log_round"):
        headline = (v["prompt_text"] or v["user_message"]).strip()
        if len(headline) > 120:
            headline = headline[:117] + "…"
        # choose level based on status (simple heuristic)
        level = "low" if (v["status"] or "ok").lower() == "ok" else "high"
        try:
            _append_flight_log_entry(
                headline=headline or "log round",
                level=level,
                details=None,
                scope=git_ctx.get("branch") or None,
                labels=["auto"],
                related_paths=[d.get("path") for d in (diffs or []) if d.get("path")][:10],
                round_id=round_id,
            )
        except Exception:
            # Never fail the log_round on flight log errors
            pass

    return {
        "round_id": round_id,
        "session_id": sess_id,
        "saved": saved,
        "events_recorded": len(events),
        "file_diffs": len(diffs) + len(diffs_since),
        "branch": git_ctx.get("branch"),
        "user": user_ctx,
        "commits_since_last": commits_since,
    }


@app.tool()
def get_alignment_context(
    branch: Optional[str] = None,
    user_name: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Fast query for recent rounds filtered by branch/user/session to align with teammates.
    Returns compact index rows.
    """
    return store.query_index(branch=branch, user_name=user_name, session_id=session_id, limit=limit)


def _run_git(args: List[str]) -> Dict[str, Any]:
    cp = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    return {"code": cp.returncode, "out": cp.stdout.strip(), "err": cp.stderr.strip()}


def _sanitize_branch(name: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_/" else "-" for ch in name.strip())
    while "--" in safe:
        safe = safe.replace("--", "-")
    safe = safe.strip("-/")
    return safe or "ai"


@app.tool()
def ai_squash_merge(
    branch_hint: Optional[str] = None,
    model_name: Optional[str] = None,
    author_name: Optional[str] = None,
    author_email: Optional[str] = None,
    base_branch: Optional[str] = None,
    include_untracked: Optional[bool] = None,
    paths: Optional[List[str]] = None,
    commit_message: Optional[str] = None,
    co_author_trailer: Optional[bool] = None,
    delete_ai_branch: Optional[bool] = None,
    set_committer_to_ai: Optional[bool] = None,
    auto_stash: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Create a temporary AI-authored branch, commit current changes with AI author, switch back,
    and squash-merge into the base branch to keep history tidy while preserving AI credit.

    - branch_hint: optional suffix for ai branch name (e.g. "refactor-parser")
    - model_name: label for AI (default "Claude")
    - author_name/email: override AI author identity (defaults to model_name and noreply@anthropic.com)
    - base_branch: branch to squash into (default: current branch)
    - include_untracked: stage new files as well (default True)
    - paths: specific paths to stage; if omitted, add all per include_untracked
    - commit_message: message for AI commit (default: generated)
    - co_author_trailer: add Co-authored-by trailer on squashed commit (default True)
    - delete_ai_branch: delete the ai/* branch after squash (default False)
    - set_committer_to_ai: set committer to AI as well as author for the AI branch commit (default False)
    """
    # load config defaults
    cfg = _load_config().get("ai_squash_merge", {})
    if model_name is None:
        model_name = cfg.get("model_name")
    if author_name is None:
        author_name = cfg.get("author_name")
    if author_email is None:
        author_email = cfg.get("author_email")
    if base_branch is None:
        base_branch = cfg.get("base_branch")
    if include_untracked is None:
        include_untracked = bool(cfg.get("include_untracked", True))
    if co_author_trailer is None:
        co_author_trailer = bool(cfg.get("co_author_trailer", True))
    if delete_ai_branch is None:
        delete_ai_branch = bool(cfg.get("delete_ai_branch", True))
    if set_committer_to_ai is None:
        set_committer_to_ai = bool(cfg.get("set_committer_to_ai", False))
    if auto_stash is None:
        auto_stash = bool(cfg.get("auto_stash", False))

    # resolve identities
    ident = _model_identity(model_name)
    ai_name = (author_name or ident.get("name") or model_name or "AI").strip()
    ai_email = (author_email or ident.get("email") or "noreply@ai.local").strip()

    # original context
    orig_branch = _git_output(["rev-parse", "--abbrev-ref", "HEAD"]) or None
    base = base_branch or orig_branch
    head_sha = _git_output(["rev-parse", "HEAD"]) or None

    # construct ai branch name
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = _sanitize_branch(branch_hint or "")
    ai_branch = f"ai/{ts}{('-' + suffix) if suffix else ''}"

    # create/switch to ai branch
    created_from = head_sha or "<unborn>"
    sw = _run_git(["switch", "-c", ai_branch])
    if sw["code"] != 0 and auto_stash:
        tag = f"vibedazi-autostash-{ts}"
        _run_git(["stash", "push", "-u", "-k", "-m", tag])
        sw = _run_git(["switch", "-c", ai_branch])
        if sw["code"] == 0:
            pop = _run_git(["stash", "pop"])
            if pop["code"] != 0:
                return {"status": "conflict", "message": "stash pop had conflicts on ai branch; resolve then re-run", "stderr": pop["err"], "ai_branch": ai_branch}
    if sw["code"] != 0:
        return {"status": "error", "message": f"failed to create ai branch: {sw['err']}", "stderr": sw["err"]}

    # stage changes
    if paths:
        add = _run_git(["add", "--", *paths])
    else:
        add = _run_git(["add", "-A" if include_untracked else "-u"])
    if add["code"] != 0:
        # attempt to go back
        if base:
            _run_git(["switch", base])
        return {"status": "error", "message": f"git add failed: {add['err']}", "stderr": add["err"]}

    # unstage excluded paths from config
    exclude_patterns = _load_config().get("ai_squash_merge", {}).get("exclude_paths", []) or []
    staged_list = _run_git(["diff", "--cached", "--name-only"]).get("out", "").splitlines()
    for sp in staged_list:
        if _match_any(sp, exclude_patterns):
            # try restore --staged, fallback to reset
            rs = _run_git(["restore", "--staged", "--", sp])
            if rs["code"] != 0:
                _run_git(["reset", "--", sp])
    # recompute staged after exclusion
    staged_list = _run_git(["diff", "--cached", "--name-only"]).get("out", "").splitlines()

    # nothing staged?
    if not staged_list:
        # go back and drop empty branch if no changes
        if base:
            _run_git(["switch", base])
        _run_git(["branch", "-D", ai_branch])
        return {"status": "noop", "message": "no changes to commit", "ai_branch": ai_branch, "base_branch": base}

    # commit on ai branch with AI author
    msg = commit_message or f"ai: {ai_name} changes ({branch_hint or 'auto'})"
    env = dict(**{k: v for k, v in dict().items()})
    if set_committer_to_ai:
        env = {**env, "GIT_COMMITTER_NAME": ai_name, "GIT_COMMITTER_EMAIL": ai_email}
    cp = subprocess.run(
        ["git", "commit", "--author", f"{ai_name} <{ai_email}>", "-m", msg],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, env={**env, **dict(**{})}
    )
    if cp.returncode != 0:
        # attempt to restore original branch
        if base:
            _run_git(["switch", base])
        return {"status": "error", "message": "git commit failed", "stderr": cp.stderr}
    ai_commit = _git_output(["rev-parse", "HEAD"]) or None

    # if base has no commit, we cannot squash-merge; keep ai branch with the commit and report
    if not head_sha or not base:
        # switch back to original (which is unborn); leave ai branch for later PR/merge
        if base:
            _run_git(["switch", base])
        return {
            "status": "ai_committed_only",
            "message": "base branch has no commits; created AI commit on ai branch; squash skipped",
            "ai_branch": ai_branch,
            "ai_commit": ai_commit,
            "base_branch": base,
        }

    # switch back to base branch
    swb = _run_git(["switch", base])
    if swb["code"] != 0:
        return {"status": "error", "message": f"failed to switch to base branch {base}", "stderr": swb["err"]}

    # squash-merge AI branch into base
    m = _run_git(["merge", "--squash", "--allow-unrelated-histories", ai_branch])
    if m["code"] != 0:
        return {"status": "conflict", "message": "squash merge failed; resolve conflicts and commit manually", "stderr": m["err"], "base_branch": base, "ai_branch": ai_branch, "ai_commit": ai_commit}

    # create the squashed commit on base with optional co-author credit
    trailers = []
    if co_author_trailer:
        trailers.append(f"Co-authored-by: {ai_name} <{ai_email}>")
    trailers.append(f"Squashed-from: {ai_branch} {ai_commit}")
    squash_msg = f"merge(squash): {ai_branch} -> {base}\n\n" + "\n".join(trailers)
    cfg2 = _load_config().get("ai_squash_merge", {})
    if bool(cfg2.get("squash_author_is_ai", True)):
        sc = _run_git(["commit", "--author", f"{ai_name} <{ai_email}>", "-m", squash_msg])
    else:
        sc = _run_git(["commit", "-m", squash_msg])
    if sc["code"] != 0:
        return {"status": "error", "message": "failed to create squash commit", "stderr": sc["err"], "base_branch": base, "ai_branch": ai_branch, "ai_commit": ai_commit}
    squash_commit = _git_output(["rev-parse", "HEAD"]) or None

    if delete_ai_branch:
        _run_git(["branch", "-D", ai_branch])

    return {
        "status": "ok",
        "ai_branch": ai_branch,
        "ai_commit": ai_commit,
        "base_branch": base,
        "squash_commit": squash_commit,
        "deleted_ai_branch": bool(delete_ai_branch),
    }


@app.tool()
def append_flight_log(
    headline: str,
    level: Optional[str] = "medium",
    details: Optional[str] = None,
    scope: Optional[str] = None,
    labels: Optional[List[str]] = None,
    related_paths: Optional[List[str]] = None,
    auto_commit: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Append a human-readable entry to the Flight Log markdown and optionally commit it.

    - headline: short summary of the change
    - level: one of breaking|high|medium|low (default: medium)
    - details: extra context (1-3 sentences recommended)
    - scope: where/what area was touched (module, service, feature)
    - labels: optional tags to aid filtering
    - related_paths: optional list of file paths to hint where changes landed
    - auto_commit: override config to auto-commit the changed markdown
    """
    cfg = _load_config()
    if auto_commit is not None:
        cfg.setdefault("flight_log", {})["auto_commit"] = bool(auto_commit)
    return _append_flight_log_entry(
        headline=headline,
        level=(level or "medium"),
        details=details,
        scope=scope,
        labels=labels,
        related_paths=related_paths,
        round_id=None,
    )


def main() -> None:
    store.init()
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
