# ---------- Security Guidance Search Tool ----------

def search_security_guidance(query):
    """
    Search for defensive cybersecurity and phishing awareness guidance.
    """

    security_query = (
        "phishing awareness cybersecurity guidance "
        + query
    )

    try:
        result = web_search(security_query)

        return result

    except Exception:
        return (
            "General phishing safety guidance: "
            "Do not click suspicious links. "
            "Do not provide passwords, OTPs, or financial information. "
            "Verify unexpected requests through an official website "
            "or trusted contact."
        )# ---------- Security Guidance Search Tool ----------

def search_security_guidance(query):
    """
    Search for defensive cybersecurity and phishing awareness guidance.
    """

    security_query = (
        "phishing awareness cybersecurity guidance "
        + query
    )

    try:
        result = web_search(security_query)

        return result

    except Exception:
        return (
            "General phishing safety guidance: "
            "Do not click suspicious links. "
            "Do not provide passwords, OTPs, or financial information. "
            "Verify unexpected requests through an official website "
            "or trusted contact."
        )