"""The agents. Each agent is a function with one clear role; the Orchestrator delegates to them."""
import re
import json
from tools.tools import (call_tool, days_remaining, deadline_label, urgency_from_days, weakness_level,
                         priority_score, hours_per_day, today)
from llm.groq_client import chat_json, chat_stream, LLMError
from guardrails.guardrails import review_recommendation
from memory import memory as mem


# 2. Student Understanding Agent (LLM + rule-based fallback)
def understanding_agent(st, msg, history):
    subjects = [t["subject"] for t in st["tasks"]]
    system = ("You are the Student Understanding Agent. Extract structured info from the student's message. "
              'Reply ONLY with JSON: {"intent":"ask_next_action|report_score|report_completion|update_time|general_question",'
              '"today_hours":number|null,"scores":[{"subject":str,"percent":number}],'
              '"completed_tasks":[str],"search_query":str|null}. '
              f"Known subjects: {subjects}. Known tasks: {[t['name'] for t in st['tasks']]}. "
              "Set search_query only if the student asks for current career/academic information.")
    ctx = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
    try:
        d = chat_json(system, f"Recent conversation:\n{ctx}\n\nStudent message: {msg}")
        src = "LLM"
    except LLMError as e:
        d, src = _rule_extract(msg, subjects), f"rule-based fallback ({str(e)[:70]})"
    out = {"intent": str(d.get("intent", "ask_next_action")), "today_hours": None, "scores": [],
           "completed": [], "search_query": d.get("search_query") or None, "source": src}
    try:
        h = d.get("today_hours")
        if h is not None and 0 < float(h) <= 12:
            out["today_hours"] = float(h)
    except (TypeError, ValueError):
        pass
    for s in d.get("scores") or []:
        try:
            sub = next(x for x in subjects if x.lower() == str(s.get("subject", "")).lower())
            out["scores"].append({"subject": sub, "percent": max(0, min(100, float(s["percent"])))})
        except (StopIteration, KeyError, TypeError, ValueError, AttributeError):
            continue
    out["completed"] = [str(c) for c in (d.get("completed_tasks") or [])]
    return out


def _rule_extract(msg, subjects):
    d = {"scores": [], "completed_tasks": [], "search_query": None, "today_hours": None, "intent": "ask_next_action"}
    m = re.search(r"(\d{1,3})\s*%", msg)
    sub = next((s for s in subjects if s.lower() in msg.lower()), None)
    if m and sub:
        d["scores"].append({"subject": sub, "percent": float(m.group(1))})
        d["intent"] = "report_score"
    h = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours|hrs|hr|h)\b", msg.lower())
    if h:
        d["today_hours"] = float(h.group(1))
    if re.search(r"\b(finished|completed|done with)\b", msg.lower()) and sub:
        d["completed_tasks"].append(sub)
    if re.search(r"\b(search|latest|trend|salary|skills needed)\b", msg.lower()):
        d["search_query"] = msg
    return d


# 6. Progress Agent
def progress_agent(st, u):
    notes = []
    for s in u["scores"]:
        for t in st["tasks"]:
            if t["subject"] == s["subject"]:
                t["score"] = s["percent"]
        st["progress"]["scores"].append({"subject": s["subject"], "percent": s["percent"],
                                         "date": today().isoformat()})
        mem.add(st["name"], "score", f"{s['subject']}: {s['percent']:.0f}%")
        if s["percent"] < 50 and s["subject"] not in st["weak_areas"]:
            st["weak_areas"].append(s["subject"])
            mem.add(st["name"], "weak_area", s["subject"])
        notes.append(f"{s['subject']} score updated to {s['percent']:.0f}%")
    for c in u["completed"]:
        for t in st["tasks"]:
            if c.lower() in t["name"].lower() or c.lower() == t["subject"].lower():
                t["done"] = True
                mem.add(st["name"], "completed", t["name"])
                notes.append(f"Marked '{t['name']}' as completed")
    if u["today_hours"]:
        st["today_hours"] = u["today_hours"]
        notes.append(f"Available time today set to {u['today_hours']}h")
    return notes


# 3. Task Analysis Agent
def task_analysis_agent(st, log):
    rows = []
    weak = [w.lower() for w in st["weak_areas"]]
    for t in st["tasks"]:
        if t["done"]:
            continue
        days = call_tool(log, "date.days_remaining", days_remaining, t["deadline"])
        days = 30 if days is None else days
        urg = call_tool(log, "calc.urgency", urgency_from_days, days) or 1.0
        weakv = call_tool(log, "calc.weakness", weakness_level, t["score"], t["subject"].lower() in weak) or 2.0
        rem = max(t["est_hours"] - t.get("hours_done", 0), 0.25)
        rows.append({"name": t["name"], "subject": t["subject"], "days": days, "urgency": urg,
                     "importance": t["importance"], "difficulty": t["difficulty"], "weakness": weakv,
                     "remaining": rem, "label": deadline_label(days)})
    return rows


# 4. Planning Agent (realistic workload / feasibility check)
def planning_agent(st, rows, hours, log):
    total = 0
    for r in rows:
        r["req_per_day"] = call_tool(log, "calc.hours_per_day", hours_per_day, r["remaining"], r["days"]) or 0
        total += r["req_per_day"]
    total = round(total, 2)
    ok = total <= st["daily_hours"]
    return {"required_per_day": total, "available": hours, "feasible": ok,
            "note": "Workload fits daily time" if ok else "Workload exceeds daily time - strict prioritisation needed"}


# 5. Priority Decision Agent
def priority_agent(rows, hours, log):
    for r in rows:
        r["score"] = call_tool(log, "calc.priority_score", priority_score,
                               r["urgency"], r["importance"], r["weakness"], r["difficulty"]) or 0
    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
    top = ranked[:3]
    tot = sum(r["score"] for r in top) or 1
    plan, left = [], hours
    for r in top:
        h = min(round(hours * r["score"] / tot * 4) / 4, r["remaining"], left)
        if h > 0:
            plan.append({"task": r["name"], "hours": h})
            left = round(left - h, 2)
    if left > 0 and plan:
        plan[0]["hours"] = round(plan[0]["hours"] + min(left, max(ranked[0]["remaining"] - plan[0]["hours"], 0)), 2)
    return {"ranked": ranked, "plan": plan}


def default_action(r):
    if r["weakness"] >= 6.5:
        return f"Revise core {r['subject']} fundamentals, then solve easy-to-medium {r['subject']} problems"
    return f"Do focused practice on {r['subject']} for '{r['name']}'"


# 7. Recommendation Agent
def recommendation_agent(st, ranked, plan, hours):
    top = ranked[0]
    fallback = {"task": top["name"], "action": default_action(top),
                "minutes": int((plan[0]["hours"] if plan else hours) * 60),
                "reason": f"Highest priority score ({top['score']}) with deadline in {top['days']} days.",
                "source": "rule-based"}
    system = ("You are the Recommendation Agent. Choose the NEXT BEST ACTION from the ranked tasks (do not invent tasks; "
              "normally pick the highest score). Reply ONLY with JSON: "
              '{"task":str,"action":"one concrete study action","minutes":int,"reason":"max 25 words, no step-by-step reasoning"}.')
    data = {"goal": st["goal"], "hours_today": hours, "weak_areas": st["weak_areas"],
            "ranked": [{k: r[k] for k in ("name", "score", "days", "weakness")} for r in ranked[:4]],
            "time_plan": plan}
    try:
        d = chat_json(system, json.dumps(data))
        return {"task": d["task"], "action": d["action"], "minutes": d["minutes"],
                "reason": d.get("reason", ""), "source": "LLM"}
    except (LLMError, KeyError, TypeError):
        return fallback


# 8. Review / Guardrail Agent
def review_agent(rec, st, hours, ranked):
    return review_recommendation(rec, st, hours, ranked)


# Final student-facing reply (streamed)
def final_reply_stream(res, st):
    rec = res["rec"]
    fallback = (f"**Next best action:** {rec['action']} — {rec['minutes']} min on *{rec['task']}*.\n\n"
                f"**Why:** {rec['reason']}")
    msgs = [{"role": "system", "content": "You are StudentPilot AI. Write a short (max 110 words) friendly message: the "
             "next best action, time, and a one-line reason. If progress changed, say what was re-planned. "
             "Use any search info briefly. Never reveal internal reasoning."},
            {"role": "user", "content": json.dumps({"student": st["name"], "recommendation": rec,
                                                      "progress_updates": res["notes"], "replanned": res["replanned"],
                                                      "plan": res["plan"], "search_info": res["search"]})}]
    try:
        yield from chat_stream(msgs)
    except LLMError:
        yield fallback
