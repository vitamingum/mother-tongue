import os
from pathlib import Path

def load_env():
    """Load .env file from current directory."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Load API keys (required based on model selection)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Backward compatibility
API_KEY = GOOGLE_API_KEY

# Validate at least one key is present
if not GOOGLE_API_KEY and not ANTHROPIC_API_KEY:
    raise ValueError("Set GOOGLE_API_KEY or ANTHROPIC_API_KEY in .env")
