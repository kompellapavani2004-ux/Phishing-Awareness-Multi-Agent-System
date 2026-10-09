```python
import streamlit as st
from datetime import datetime

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Phishing Awareness Multi-Agent System",
    page_icon="🛡️",
    layout="wide"
)

# =====================================================
# SESSION STATE / MEMORY
# =====================================================

if "analysis_memory" not in st.session_state:
    st.session_state.analysis_memory = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# =====================================================
# MESSAGE ANALYSIS AGENT
# =====================================================

def message_analysis_agent(message):

    text = message.lower()
    indicators = []

    urgent_words = [
        "urgent",
        "immediately",
        "act now",
        "right now",
        "expires today"
    ]

    otp_words = [
        "otp",
        "one-time password",
        "verification code",
        "pin number"
    ]

    password_words = [
        "password",
        "login credentials",
        "bank details",
        "credit card details"
    ]

    suspicious_words = [
        "click here",
        "verify your account",
        "claim your prize",
        "free reward",
        "suspended account"
    ]

    account_block_words = [
        "account blocked",
        "account will be blocked",
        "account will be suspended",
        "account suspended",
        "account will be closed"
    ]

    # Detect urgency
    if any(word in text for word in urgent_words):
        indicators.append("Urgent language")

    # Detect OTP requests
    if any(word in text for word in otp_words):
        indicators.append("Request involving OTP or verification code")

    # Detect password or financial information requests
    if any(word in text for word in password_words):
        indicators.append("Request for password or sensitive information")

    # Detect suspicious calls to action
    if any(word in text for word in suspicious_words):
        indicators.append("Suspicious call to action")

    # Detect threats about account blocking
    if any(word in text for word in account_block_words):
        indicators.append("Threat of account block or suspension")

    # Detect URLs
    if (
        "http://" in text
        or "https://" in text
        or "www." in text
    ):
        indicators.append("Contains a URL that needs verification")

    # Calculate demo risk score
    score = len(indicators)

    if score >= 3:
        risk = "HIGH"
        explanation = (
            "Multiple phishing warning signs were detected. "
            "The message may use urgency, sensitive information "
            "requests, suspicious links, or account threats "
            "to manipulate the recipient."
        )

    elif score >= 1:
        risk = "MEDIUM"
        explanation = (
            "One or more warning signs were detected. "
            "Verify the sender and request independently "
            "before taking any action."
        )

    else:
        risk = "LOW"
        explanation = (
            "No configured warning signs were detected. "
            "This does not guarantee that the message is safe."
        )

    return {
        "risk": risk,
        "score": score,
        "indicators": indicators,
        "explanation": explanation
    }


# =====================================================
# SECURITY GUIDANCE AGENT
# =====================================================

def security_guidance_agent(analysis):

    if analysis["risk"] == "HIGH":

        return (
            "Do not click suspicious links or open unexpected "
            "attachments. Never share your password, OTP, or "
            "financial information. Visit the organization's "
            "official website directly or contact its verified "
            "customer support. Report the suspicious message "
            "if an appropriate reporting channel is available."
        )

    elif analysis["risk"] == "MEDIUM":

        return (
            "Check the sender's address carefully. Avoid "
            "unexpected links and requests for sensitive data. "
            "Verify the request through the organization's "
            "official website or a trusted contact."
        )

    else:

        return (
            "No configured warning signs were detected, but "
            "the message is not guaranteed to be safe. Verify "
            "unexpected requests, inspect links carefully, "
            "and never share passwords or OTPs."
        )


# =====================================================
# COORDINATOR AGENT
# =====================================================

def coordinator_agent(analysis, guidance):

    return {
        "risk": analysis["risk"],
        "score": analysis["score"],
        "indicators": analysis["indicators"],
        "explanation": analysis["explanation"],
        "recommendation": guidance,

        "trace": [
            {
                "agent": "Message Analysis Agent",
                "action": "Analyze message and detect warning signs"
            },
            {
                "agent": "Security Guidance Agent",
                "action": "Generate defensive security guidance"
            },
            {
                "agent": "Coordinator Agent",
                "action": "Combine agent results into a final response"
            }
        ]
    }


# =====================================================
# APP HEADER
# =====================================================

st.title("🛡️ Phishing Awareness Multi-Agent System")

st.write(
    "A defensive multi-agent system that analyzes "
    "simulated emails and provides safe security recommendations."
)

st.warning(
    "DEMO ONLY: Use simulated messages. Do not enter real "
    "passwords, OTPs, bank details, or personal information."
)


# =====================================================
# LOCATION SELECTOR - DISPLAY AT THE TOP
# =====================================================

st.markdown("### 📍 Select Your Location")

locations = [
    "Hyderabad, Telangana",
    "Visakhapatnam (Vizag), Andhra Pradesh",
    "Vijayawada, Andhra Pradesh",
    "Amaravati, Andhra Pradesh",
    "Tirupati, Andhra Pradesh",
    "Guntur, Andhra Pradesh",
    "Kakinada, Andhra Pradesh",
    "Rajahmundry, Andhra Pradesh",
    "Warangal, Telangana",
    "Bengaluru, Karnataka",
    "Chennai, Tamil Nadu",
    "Other"
]

selected_location = st.selectbox(
    "Choose your city",
    locations,
    index=0,
    key="city_selector"
)

if selected_location == "Other":

    custom_location = st.text_input(
        "Enter your city",
        placeholder="Example: Eluru, Andhra Pradesh",
        key="custom_city"
    )

    if custom_location.strip():
        selected_location = custom_location.strip()

st.info(f"📍 Selected Location: {selected_location}")

st.divider()


# =====================================================
# DEMO MESSAGE SECTION
# =====================================================

st.subheader("🧪 Try a Demo Message")

demo_messages = {
    "Select a demo example": "",

    "High Risk - Password and Suspicious Link": (
        "URGENT! Your bank account will be blocked. "
        "Click here http://example.invalid and enter "
        "your password immediately."
    ),

    "High Risk - OTP Request": (
        "URGENT! Your account is suspended. "
        "Click here http://example.invalid and share "
        "your OTP immediately."
    ),

    "Medium Risk - Account Verification": (
        "Please verify your account details as soon as possible."
    ),

    "Low Risk - Normal Greeting": (
        "Hello! This is a simulated reminder about "
        "tomorrow's meeting. Thank you."
    )
}

selected_demo = st.selectbox(
    "Choose an example message",
    list(demo_messages.keys()),
    key="demo_selector"
)

message = st.text_area(
    "Enter a simulated email or message",
    value=demo_messages[selected_demo],
    height=150,
    placeholder="Enter a fictional message here...",
    key="message_input"
)


# =====================================================
# RUN MULTI-AGENT ANALYSIS
# =====================================================

if st.button("🔍 Analyze Message", type="primary"):

    if not message.strip():

        st.warning("Please enter a simulated message first.")

    else:

        # Step 1: Message Analysis Agent
        analysis = message_analysis_agent(message)

        # Step 2: Security Guidance Agent
        guidance = security_guidance_agent(analysis)

        # Step 3: Coordinator Agent
        result = coordinator_agent(analysis, guidance)

        result["timestamp"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        result["location"] = selected_location

        # Store latest result
        st.session_state.analysis_result = result

        # Save history
        st.session_state.analysis_memory.insert(
            0,
            {
                "timestamp": result["timestamp"],
                "risk": result["risk"],
                "location": result["location"]
            }
        )

        # Keep latest 10 records
        st.session_state.analysis_memory = (
            st.session_state.analysis_memory[:10]
        )


# =====================================================
# DISPLAY ANALYSIS RESULTS
# =====================================================

result = st.session_state.analysis_result

if result:

    st.divider()

    st.subheader("📊 Analysis Results")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🚨 Risk Level")

        if result["risk"] == "HIGH":
            st.error("HIGH RISK")

        elif result["risk"] == "MEDIUM":
            st.warning("MEDIUM RISK")

        else:
            st.success("LOW RISK")

        st.caption(f"📍 Location: {result['location']}")

    with col2:

        st.markdown("### 🕒 Analysis Time")
        st.write(result["timestamp"])

        st.metric(
            "Warning Signs Detected",
            result["score"]
        )

    st.markdown("### 📝 Risk Explanation")

    st.write(result["explanation"])

    st.markdown("### 🛡️ Safe Recommendation")

    st.info(result["recommendation"])

    # Message Analysis Agent
    with st.expander(
        "🔎 Message Analysis Agent",
        expanded=True
    ):

        st.write(f"**Risk:** {result['risk']}")

        st.write("**🚩 Detected Indicators:**")

        if result["indicators"]:

            for indicator in result["indicators"]:
                st.write(f"- {indicator}")

        else:

            st.write("No configured warning signs detected.")

        st.write(
            f"**Explanation:** {result['explanation']}"
        )

        st.caption(
            "This is a simple rule-based demo, not a definitive "
            "phishing detection system."
        )

    # Security Guidance Agent
    with st.expander("🔐 Security Guidance Agent"):

        st.write(result["recommendation"])

        st.caption(
            "Source: Built-in defensive security guidance"
        )

    # Coordinator Agent
    with st.expander("🤖 Coordinator Agent"):

        st.write(
            "The Coordinator Agent combines the Message Analysis "
            "and Security Guidance results to produce the final "
            "risk explanation and safe recommendation."
        )

    # Agent Execution Trace
    st.markdown("### 🔄 Agent Execution Trace")

    for index, step in enumerate(
        result["trace"],
        start=1
    ):

        st.write(
            f"**Step {index}: {step['agent']}** "
            f"→ {step['action']}"
        )

    # Workflow
    st.markdown("### 🏗️ Multi-Agent Workflow")

    st.code(
        """
Simulated Message
       |
       v
Message Analysis Agent
       |
       v
Security Guidance Agent
       |
       v
Coordinator Agent
       |
       v
Risk Explanation
       |
       v
Safe Recommendation
       |
       v
Analysis Memory
        """,
        language="text"
    )


# =====================================================
# ANALYSIS MEMORY
# =====================================================

st.divider()

st.subheader("🧠 Analysis Memory")

if st.session_state.analysis_memory:

    for record in st.session_state.analysis_memory:

        st.write(
            f"🕒 {record['timestamp']} | "
            f"📍 {record['location']} | "
            f"Risk: {record['risk']}"
        )

    if st.button("🗑️ Clear Analysis Memory"):

        st.session_state.analysis_memory = []
        st.session_state.analysis_result = None

        st.rerun()

else:

    st.caption(
        "No analysis history yet. Run a demo message "
        "to create a record."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "🛡️ Phishing Awareness Multi-Agent System | "
    "Defensive cybersecurity demo using simulated messages only."
)
```
