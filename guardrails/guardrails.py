"""Guardrails: input validation, LLM-output parsing, and recommendation review."""
import json
import re
import datetime as dt

UNSAFE = ("skip sleep", "no sleep", "all-nighter", "all nighter", "skip meals", "stop eating", "cheat", "copy answers")


def validate_message(msg):
    if not msg or not msg.strip():
        return False, "Please type a message."
    if len(msg) > 1000:
        return False, "Message too long (max 1000 characters)."
    return True, ""


def validate_task(t):
    errs = []
    if not str(t.get("name", "")).strip():
        errs.append("Task name is empty")
    if not str(t.get("subject", "")).strip():
        errs.append("Task subject is empty")
    for k in ("importance", "difficulty"):
        if not 1 <= t.get(k, 0) <= 10:
            errs.append(f"{k} must be 1-10")
    if t.get("est_hours", 0) <= 0:
        errs.append("estimated hours must be > 0")
    try:
        dt.date.fromisoformat(t.get("deadline", ""))
    except (ValueError, TypeError):
        errs.append("deadline is not a valid date")
    return errs


def validate_profile(s):
    errs = []
    if not s.get("name", "").strip():
        errs.append("Student name is missing")
    if not s.get("goal", "").strip():
        errs.append("Goal is missing")
    if not 0 < s.get("daily_hours", 0) <= 12:
        errs.append("Daily hours must be between 0 and 12")
    if not s.get("tasks"):
        errs.append("Add at least one task (or load the demo student)")
    for t in s.get("tasks", []):
        errs += [f"{t.get('name', '?')}: {e}" for e in validate_task(t)]
    return errs


def parse_json(text):
    """Extract a JSON object from LLM text (handles code fences / extra prose)."""
    text = re.sub(r"```(?:json)?", "", text or "").strip()
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b <= a:
        raise ValueError("no JSON object found")
    try:
        return json.loads(text[a:b + 1])
    except json.JSONDecodeError as e:
        raise ValueError(str(e))


def review_recommendation(rec, st, hours, ranked):
    """Checks: real task, fits time, safe, goal-related. Auto-fixes failures. Returns verdict dict."""
    fixes, checks = [], []
    names = {r["name"].lower(): r for r in ranked}
    top3 = [r["name"].lower() for r in ranked[:3]]
    task = str(rec.get("task", "")).lower()

    known = task in names
    if not known:
        rec["task"] = ranked[0]["name"]
        fixes.append("Task replaced with highest-priority task")
    else:
        rec["task"] = names[task]["name"]
    checks.append(("Task exists in student's task list", known))

    goal_ok = rec["task"].lower() in top3
    checks.append(("Goal-related (among top-priority tasks)", goal_ok))

    try:
        minutes = int(float(rec.get("minutes", 0)))
    except (TypeError, ValueError):
        minutes = 0
    fits = 0 < minutes <= hours * 60
    if not fits:
        minutes = int(min(max(minutes, 30) if minutes > 0 else 60, hours * 60))
        fixes.append(f"Duration adjusted to {minutes} min to fit available time")
    rec["minutes"] = minutes
    checks.append((f"Fits available time ({hours}h today)", fits))

    text = f"{rec.get('action', '')} {rec.get('reason', '')}".lower()
    safe = not any(w in text for w in UNSAFE) and st.get("daily_hours", 0) <= 12
    if not safe:
        rec["action"] = f"Do a focused, well-paced session on {rec['task']} with short breaks"
        fixes.append("Unsafe suggestion removed")
    checks.append(("Safe and healthy", safe))

    return {"approved": all(ok for _, ok in checks), "checks": checks, "fixes": fixes, "rec": rec}
