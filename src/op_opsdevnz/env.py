"""
Environment helpers for loading secret reference files.
"""

from pathlib import Path
from typing import Optional

from dotenv import find_dotenv, load_dotenv


def load_refs(env: str = "staging", path: Optional[str] = None) -> None:
    """
    Load a refs file into the environment.

    By default, auto-discovers ``.env.{env}`` (e.g. ``.env.staging``)
    by walking up the directory tree — the same convention used by
    ``python-dotenv``.  Pass ``path`` explicitly for files with a
    different naming convention or location.
    """

    filename = path or f".env.{env}"
    p = Path(filename)
    if not p.exists():
        p = Path(find_dotenv(filename))
    if p.exists():
        load_dotenv(p)
