"""
Phishing Awareness Multi-Agent System

Agents:
1. Message Analysis Agent
2. Security Guidance Agent
3. Coordinator Agent
"""

import json
import re

from llm.groq_client import chat_json, LLMError
from tools.tools import search_security_guidance
from memory import memory as mem


# ============================================================
# 1. MESSAGE ANALYSIS AGENT
# ============================================================

def message_analysis_agent(message):
    """
    Analyze a simulated email/message for phishing indicators.
    """

    system_prompt = """
You are the Message Analysis Agent in a defensive phishing awareness system.

Analyze ONLY the simulated message provided by the user.

Look for:
- Urgent or threatening language
- Requests for passwords, OTPs, or sensitive information
- Suspicious links
- Requests for money or payment
- Unexpected attachments
- Sender impersonation
- Account verification requests
- Grammar or wording anomalies

Return ONLY valid JSON in this format:

{
    "risk_level": "LOW|MEDIUM|HIGH",
    "indicators": ["indicator 1", "indicator 2"],
    "explanation": "short explanation"
}

Do not provide instructions for creating phishing messages.
This system is strictly defensive.
"""

    try:
        result = chat_json(
            system_prompt,
            f"Simulated message:\n\n{message}"
        )

        return {
            "risk_level": result.get("risk_level", "MEDIUM"),
            "indicators": result.get("indicators", []),
            "explanation": result.get("explanation", ""),
            "source": "LLM"
        }

    except (LLMError, TypeError, ValueError):
        return rule_based_message_analysis(message)


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def rule_based_message_analysis(message):
    """
    Simple fallback analysis if the LLM is unavailable.
    """

    text = message.lower()

    indicators = []

    # Urgency
    if re.search(
        r"\b(urgent|immediately|asap|act now|final warning|expires today)\b",
        text
    ):
        indicators.append("Urgent or threatening language")

    # Credential requests
    if re.search(
        r"\b(password|passcode|otp|one[- ]time password|login credentials)\b",
        text
    ):
        indicators.append("Requests sensitive credentials")

    # Link
    if re.search(r"https?://|www\.", text):
        indicators.append("Contains a link")

    # Payment
    if re.search(
        r"\b(payment|pay now|transfer|bank|credit card|debit card)\b",
        text
    ):
        indicators.append("Requests payment or financial information")

    # Account verification
    if re.search(
        r"\b(verify your account|account suspended|confirm your account)\b",
        text
    ):
        indicators.append("Unexpected account verification request")

    # Attachment
    if re.search(
        r"\b(attachment|attached file|document attached)\b",
        text
    ):
        indicators.append("Unexpected attachment")

    # Risk calculation
    if len(indicators) >= 3:
        risk = "HIGH"
    elif len(indicators) >= 1:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    if indicators:
        explanation = (
            "The message contains indicators commonly associated "
            "with phishing attempts."
        )
    else:
        explanation = (
            "No strong phishing indicators were detected, "
            "but users should still verify unexpected messages."
        )

    return {
        "risk_level": risk,
        "indicators": indicators,
        "explanation": explanation,
        "source": "rule-based fallback"
    }


# ============================================================
# 2. SECURITY GUIDANCE AGENT
# ============================================================

def security_guidance_agent(analysis):
    """
    Retrieve security guidance based on the analysis.
    """

    indicators = analysis.get("indicators", [])

    query = (
        "phishing awareness guidance for "
        + ", ".join(indicators)
    )

    try:
        guidance = search_security_guidance(query)

        return {
            "query": query,
            "guidance": guidance,
            "source": "security search tool"
        }

    except Exception as e:
        return {
            "query": query,
            "guidance": (
                "Do not click suspicious links, do not provide "
                "passwords or OTPs, and verify requests through "
                "the organization's official website."
            ),
            "source": f"fallback guidance ({str(e)[:50]})"
        }


# ============================================================
# 3. COORDINATOR AGENT
# ============================================================

def coordinator_agent(message):
    """
    Coordinate Message Analysis Agent and Security Guidance Agent.

    This demonstrates A2A-style communication:
    Coordinator -> Message Analysis Agent
    Coordinator -> Security Guidance Agent
    Coordinator -> Final Risk Explanation
    """

    # Agent 1
    analysis = message_analysis_agent(message)

    # Agent 2
    guidance = security_guidance_agent(analysis)

    # Combine outputs
    combined_data = {
        "message": message,
        "analysis": analysis,
        "security_guidance": guidance
    }

    system_prompt = """
You are the Coordinator Agent for a defensive phishing awareness system.

Combine the Message Analysis Agent's output and the Security Guidance
Agent's output.

Return ONLY valid JSON:

{
    "risk_level": "LOW|MEDIUM|HIGH",
    "risk_explanation": "clear explanation in simple language",
    "safe_recommendation": "safe action the user should take"
}

Do not reveal chain-of-thought or internal reasoning.

The recommendation must be defensive and safe.
"""

    try:
        final_result = chat_json(
            system_prompt,
            json.dumps(combined_data)
        )

    except (LLMError, TypeError, ValueError):
        final_result = {
            "risk_level": analysis["risk_level"],
            "risk_explanation": analysis["explanation"],
            "safe_recommendation": (
                "Do not click suspicious links or provide "
                "passwords/OTP. Verify the request using the "
                "organization's official website."
            )
        }

    result = {
        "message": message,
        "analysis": analysis,
        "guidance": guidance,
        "risk_level": final_result.get(
            "risk_level",
            analysis["risk_level"]
        ),
        "risk_explanation": final_result.get(
            "risk_explanation",
            analysis["explanation"]
        ),
        "safe_recommendation": final_result.get(
            "safe_recommendation",
            "Verify the message through an official channel."
        )
    }

    # Store analyzed message and result in memory
    try:
        mem.add(
            "phishing_system",
            "analysis",
            json.dumps(result)
        )
    except Exception:
        pass

    return result