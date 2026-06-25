import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str) -> str:
    """Return env var value or raise if not set. Fails fast on misconfiguration."""
    value = os.getenv(key)
    if value is None or value == "":
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            f"Set it in .env or the deployment environment."
        )
    return value


def _get_env(key: str, default: str) -> str:
    """Return env var value or default. For non-secret operational configs only."""
    return os.getenv(key, default)


# Required — will crash at startup if not set
GCP_PROJECT_ID = _require_env("GCP_PROJECT_ID")

# Optional operational configs with safe defaults
GCP_REGION = _get_env("GCP_REGION", "us-central1")
VERTEX_AI_LOCATION = _get_env("VERTEX_AI_LOCATION", "us-central1")
GEMINI_MODEL = _get_env("GEMINI_MODEL", "gemini-2.5-flash")
