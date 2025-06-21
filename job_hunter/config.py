# job_hunter/config.py
from pathlib import Path
from dotenv import load_dotenv

def load_env() -> None:
    """
    Load .env from repo root exactly once.
    Safe to call multiple times; subsequent calls are no-ops.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)