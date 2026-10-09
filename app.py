import streamlit as st

from agents.orchestrator import run_pipeline
from memory import memory as mem


st.set_page_config(
    page_title="Phishing Awareness System",
    page_icon="🛡️",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🛡️ Phishing Awareness Multi-Agent System")

st.write(
    "A defensive multi-agent system that analyzes simulated "
    "emails and provides safe security recommendations."
)

st.info(
    "⚠️ Demo only: Use simulated messages. "
    "Do not enter real passwords, OTPs, bank details, or personal information."
)


# =========================================================
# DEMO MESSAGES
# =========================================================

st.subheader("🧪 Try a Demo Message")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 Phishing Example"):
        st.session_state.demo_message = (
            "URGENT: Your bank account will be blocked today. "
            "Click this link to verify your password."
        )

with col2:
    if st.button("🟢 Safe Example"):
        st.session_state.demo_message = (
            "Hello, your monthly bank statement is now available. "
            "Please open the official banking application to view it."
        )

with col3:
    if st.button("🟠 Suspicious Example"):
        st.session_state.demo_message = (
            "You have won a reward! Click this link immediately "
            "and provide your account details to claim it."
        )


# =========================================================
# MESSAGE INPUT
# =========================================================

message = st.text_area(
    "📩 Enter simulated email/message:",
    value=st.session_state.get("demo_message", ""),
    height=180,
    placeholder=(
        "Example: URGENT! Your account will be blocked. "
        "Click here to verify your password."
    )
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

if st.button("🔍 Analyze Message", type="primary"):

    if not message.strip():
        st.warning("Please enter a simulated message.")
        st.stop()

    with st.spinner("🤖 Agents are analyzing the message..."):

        result = run_pipeline(message)

    st.success("✅ Analysis completed!")


    # =====================================================
    # GET RESULT
    # =====================================================

    final_result = result.get("result", {})

    risk_level = final_result.get(
        "risk_level",
        "UNKNOWN"
    )


    # =====================================================
    # RISK LEVEL
    # =====================================================

    st.subheader("🚨 Risk Level")

    if risk_level == "HIGH":

        st.error(f"🔴 {risk_level} RISK")

    elif risk_level == "MEDIUM":

        st.warning(f"🟠 {risk_level} RISK")

    else:

        st.success(f"🟢 {risk_level} RISK")


    # =====================================================
    # RISK EXPLANATION
    # =====================================================

    st.subheader("📝 Risk Explanation")

    st.write(
        final_result.get(
            "risk_explanation",
            "No explanation available."
        )
    )


    # =====================================================
    # SAFE RECOMMENDATION
    # =====================================================

    st.subheader("🛡️ Safe Recommendation")

    st.success(
        final_result.get(
            "safe_recommendation",
            "No recommendation available."
        )
    )


    # =====================================================
    # MESSAGE ANALYSIS AGENT
    # =====================================================

    st.subheader("🔎 Message Analysis Agent")

    analysis = result.get("analysis", {})

    st.write(
        f"**Risk:** {analysis.get('risk_level', 'UNKNOWN')}"
    )

    indicators = analysis.get("indicators", [])

    if indicators:

        st.write("**🚩 Detected Indicators:**")

        for indicator in indicators:

            st.write(f"- {indicator}")

    st.write(
        f"**Explanation:** "
        f"{analysis.get('explanation', 'No explanation available.')}"
    )


    # =====================================================
    # SECURITY GUIDANCE AGENT
    # =====================================================

    st.subheader("🔐 Security Guidance Agent")

    guidance = result.get("guidance", {})

    st.write(
        guidance.get(
            "guidance",
            "No security guidance available."
        )
    )

    st.caption(
        f"Source: {guidance.get('source', 'Security Guidance Tool')}"
    )


    # =====================================================
    # COORDINATOR
    # =====================================================

    st.subheader("🤖 Coordinator Agent")

    st.write(
        "The Coordinator Agent combines the Message Analysis "
        "and Security Guidance results to produce the final "
        "risk explanation and safe recommendation."
    )


    # =====================================================
    # AGENT TRACE
    # =====================================================

    st.subheader("🔄 Agent Execution Trace")

    trace = result.get("trace", [])

    for i, step in enumerate(trace, start=1):

        st.write(
            f"**Step {i}: {step['agent']}** → "
            f"{step['action']}"
        )


    # =====================================================
    # WORKFLOW
    # =====================================================

    st.subheader("🏗️ Multi-Agent Workflow")

    st.code(
        """
Simulated Message
       ↓
Message Analysis Agent
       ↓
Security Guidance Agent
       ↓
Coordinator Agent
       ↓
Risk Explanation
       ↓
Safe Recommendation
       ↓
Memory
        """,
        language="text"
    )


# =========================================================
# MEMORY / HISTORY
# =========================================================

st.divider()

st.subheader("🧠 Analysis Memory")

history = mem.fetch(
    "phishing_user",
    "analysis",
    limit=5
)

if history:

    for item in history:

        with st.expander(
            f"🕒 {item['time']}"
        ):

            st.write(item["detail"])

else:

    st.write("No previous analysis stored.")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛡️ Phishing Awareness Multi-Agent System | "
    "Defensive cybersecurity demo using simulated messages only"
)