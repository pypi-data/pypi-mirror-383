try:
    from .tng_python import *
except ImportError:
    # Rust extension not available (e.g., during testing)
    pass
import tomllib
from pathlib import Path

def _get_version():
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "0.1.0"  # fallback

__version__ = _get_version()
