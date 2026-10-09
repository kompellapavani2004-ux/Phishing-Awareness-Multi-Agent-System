\# 🛡️ Phishing Awareness Multi-Agent System



\## 📌 Project Overview



The Phishing Awareness Multi-Agent System is a defensive cybersecurity application that analyzes simulated emails and messages to identify possible phishing indicators.



The system uses multiple specialized agents that work together to provide a risk explanation and safe recommendation.



\## 🤖 Agents



\### 1. Message Analysis Agent



Analyzes the message for phishing characteristics such as:



\- Urgent language

\- Suspicious links

\- Password requests

\- Requests for sensitive information

\- Suspicious account verification requests



\### 2. Security Guidance Agent



Retrieves defensive cybersecurity guidance using the security guidance search tool.



It provides recommendations such as:



\- Do not click suspicious links

\- Do not provide passwords or OTPs

\- Verify requests through official channels

\- Avoid sharing financial information



\### 3. Coordinator Agent



Combines the outputs from the Message Analysis Agent and Security Guidance Agent.



It produces:



\- Risk level

\- Risk explanation

\- Safe recommendation



\## 🧠 Memory



The system stores previous phishing analysis results in SQLite memory.



Stored information includes:



\- Message

\- Risk level

\- Recommendation

\- Analysis timestamp



\## 🔄 Multi-Agent Workflow



```text

Simulated Message

&#x20;      ↓

Message Analysis Agent

&#x20;      ↓

Security Guidance Agent

&#x20;      ↓

Coordinator Agent

&#x20;      ↓

Risk Explanation

&#x20;      ↓

Safe Recommendation

&#x20;      ↓

Memory

