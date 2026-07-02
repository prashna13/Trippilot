import os


def get_main_model():
    """Return the configured model for ADK agents.

    Two modes controlled by ``ADK_PROVIDER`` env var:

    ``"google"`` (default)
      Uses ``GEMINI_MODEL`` (default ``"gemini-2.5-flash"``).
      ADK uses its built-in Gemini API client.

    ``"openai-compatible"``
      Uses ``ADK_MODEL`` (default ``"gpt-4o-mini"``).
      ADK routes through ``OpenAILlm`` which reads ``OPENAI_API_KEY``
      and ``OPENAI_BASE_URL`` from the environment.

    For model names that don't match ADK's built-in patterns
    (``gpt-*``, ``o1-*``, ``o3-*``), set ``ADK_MODEL_PREFIX=openai``
    to prefix with ``openai/`` for LiteLLM routing.
    """
    provider = (os.getenv("ADK_PROVIDER") or "google").strip().lower()

    if provider == "openai-compatible":
        model = os.getenv("ADK_MODEL") or "gpt-4o-mini"
        prefix = os.getenv("ADK_MODEL_PREFIX") or ""
        return f"{prefix}/{model}" if prefix else model

    # Google Gemini provider
    return os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
