"""
Phishing Awareness Multi-Agent Orchestrator
"""

from agents import agents as A
from memory import memory as mem


def run_phishing_analysis(message):

    trace = []

    # Step 1: Message Analysis Agent
    trace.append({
        "agent": "Message Analysis Agent",
        "action": "Analyze message characteristics"
    })

    analysis = A.message_analysis_agent(message)

    # Step 2: Security Guidance Agent
    trace.append({
        "agent": "Security Guidance Agent",
        "action": "Retrieve defensive security guidance"
    })

    guidance = A.security_guidance_agent(analysis)

    # Step 3: Coordinator Agent
    trace.append({
        "agent": "Coordinator Agent",
        "action": "Combine analysis and security guidance"
    })

    result = A.coordinator_agent(message)  

    # Step 4: Store result in memory
    mem.add(
        "phishing_user",
        "analysis",
        str({
            "message": message,
            "risk": result.get("risk_level"),
            "recommendation": result.get("recommendation")
        })
    )

    return {
        "message": message,
        "analysis": analysis,
        "guidance": guidance,
        "result": result,
        "trace": trace
    }
run_pipeline = run_phishing_analysis
