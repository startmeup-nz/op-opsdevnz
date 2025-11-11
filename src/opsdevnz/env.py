"""
Environment helpers for loading secret reference files.
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_refs(env: str = "staging", path: Optional[str] = None) -> None:
    """
    Explicitly load a refs file like `.env.refs.staging` (safe to commit).
    Does nothing when the file is absent.
    """

    filename = path or f".env.refs.{env}"
    p = Path(filename)
    if p.exists():
        load_dotenv(p)
