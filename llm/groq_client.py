"""Reusable Groq client (Groq Python SDK). Model is configurable via GROQ_MODEL env var / sidebar."""
import os
from guardrails.guardrails import parse_json

DEFAULT_MODEL = "openai/gpt-oss-20b"


def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name and name not in os.environ:
                os.environ[name] = value


_load_dotenv()


class LLMError(Exception):
    pass


def model_name():
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL)


def _api_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key

    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        return st.secrets.get("GROQ_API_KEY")
    except StreamlitSecretNotFoundError:
        return None


def api_key_present():
    return bool(_api_key())


_client = None


def get_client():
    global _client
    key = _api_key()
    if not key:
        raise LLMError("Set GROQ_API_KEY in the environment or Streamlit secrets.")
    if _client is None or getattr(_client, "api_key", None) != key:
        try:
            from groq import Groq
            _client = Groq(api_key=key)
        except Exception as e:
            raise LLMError(f"Could not create Groq client: {e}")
    return _client


def chat(messages, temperature=0.2, json_mode=False):
    client = get_client()
    kwargs = dict(model=model_name(), messages=messages, temperature=temperature)
    try:
        if json_mode:
            try:
                r = client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
            except Exception:  # model may not support json_object -> retry plain
                r = client.chat.completions.create(**kwargs)
        else:
            r = client.chat.completions.create(**kwargs)
        return r.choices[0].message.content or ""
    except Exception as e:
        raise LLMError(f"Groq API error: {e}")


def chat_json(system, user):
    """Ask for JSON; raises LLMError on API failure or invalid JSON."""
    text = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], json_mode=True)
    try:
        return parse_json(text)
    except ValueError as e:
        raise LLMError(f"Invalid LLM output: {e}")


def chat_stream(messages, temperature=0.3):
    client = get_client()
    try:
        stream = client.chat.completions.create(model=model_name(), messages=messages,
                                                temperature=temperature, stream=True)
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta
    except Exception as e:
        raise LLMError(f"Groq streaming error: {e}")
