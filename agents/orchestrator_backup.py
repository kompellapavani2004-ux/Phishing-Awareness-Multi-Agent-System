"""Orchestrator Agent: delegates to every agent in order, records A2A messages, tool use and memory updates."""
from agents import agents as A
from tools.tools import call_tool, web_search
from memory import memory as mem


def run_pipeline(st, msg, history, on_step=None):
    log, trace, a2a = [], [], []

    def step(agent, task, fn, summarize, nxt):
        a2a.append({"from": "Orchestrator", "to": agent, "content": f"DELEGATE: {task}"})
        n = len(log)
        out = fn()
        t = {"agent": agent, "task": task, "summary": summarize(out), "tools": [x["tool"] for x in log[n:]]}
        trace.append(t)
        a2a.append({"from": agent, "to": nxt, "content": t["summary"]})
        if on_step:
            on_step(t)
        return out

    prev = [(r["name"], r["score"]) for r in (st.get("last_ranked") or [])]

    u = step("Student Understanding Agent", "Extract goal, time, scores, constraints",
             lambda: A.understanding_agent(st, msg, history),
             lambda o: f"intent={o['intent']}, scores={o['scores']}, hours={o['today_hours']} [{o['source']}]",
             "Progress Agent")
    search = call_tool(log, "search.web_search", web_search, u["search_query"]) if u["search_query"] else None
    notes = step("Progress Agent", "Update progress + long-term memory", lambda: A.progress_agent(st, u),
                 lambda o: "; ".join(o) or "No progress change", "Task Analysis Agent")
    hours = st.get("today_hours") or st["daily_hours"]
    rows = step("Task Analysis Agent", "Analyze urgency, importance, difficulty, time",
                lambda: A.task_analysis_agent(st, log),
                lambda o: f"{len(o)} open tasks analysed", "Planning Agent")
    if not rows:
        raise ValueError("All tasks are completed - add new tasks.")
    pinfo = step("Planning Agent", "Check workload vs available time",
                 lambda: A.planning_agent(st, rows, hours, log),
                 lambda o: f"needs {o['required_per_day']}h/day; {o['note']}", "Priority Decision Agent")
    pr = step("Priority Decision Agent", "Compute priority scores + today's time split",
              lambda: A.priority_agent(rows, hours, log),
              lambda o: "ranking: " + ", ".join(f"{r['name']}={r['score']}" for r in o["ranked"]),
              "Recommendation Agent")
    rec = step("Recommendation Agent", "Produce NEXT BEST ACTION",
               lambda: A.recommendation_agent(st, pr["ranked"], pr["plan"], hours),
               lambda o: f"{o['task']} for {o['minutes']} min [{o['source']}]", "Review/Guardrail Agent")
    rev = step("Review/Guardrail Agent", "Check realistic, safe, goal-related, fits time",
               lambda: A.review_agent(rec, st, hours, pr["ranked"]),
               lambda o: ("APPROVED" if o["approved"] else "ADJUSTED: " + "; ".join(o["fixes"])), "Student")

    final = rev["rec"]
    mem.add(st["name"], "recommendation", f"{final['task']} - {final['minutes']} min: {final['action']}")
    st["last_ranked"] = pr["ranked"]
    st["last_rec"] = final
    return {"notes": notes, "rows": rows, "pinfo": pinfo, "ranked": pr["ranked"], "plan": pr["plan"],
            "rec": final, "review": rev, "trace": trace, "a2a": a2a, "tools": log, "search": search,
            "hours": hours, "prev": prev, "replanned": bool(u["scores"] or u["completed"]), "understanding": u}
