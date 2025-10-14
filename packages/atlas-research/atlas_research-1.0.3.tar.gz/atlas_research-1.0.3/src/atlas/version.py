"""
Atlas version management module.
Automatically syncs version from pyproject.toml or package metadata.

Author: Han Jeongwoo
"""

from importlib.metadata import version as pkg_version, PackageNotFoundError
from pathlib import Path
import sys


def _load_version() -> str:
    """
    Load package version dynamically.
    1. Try to get it from installed package metadata.
    2. If not installed (local dev), read directly from pyproject.toml.
    """
    try:
        # 1️⃣ Installed package case (PyPI, production)
        return pkg_version("atlas-research")
    except PackageNotFoundError:
        # 2️⃣ Local dev case: read pyproject.toml manually
        try:
            pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
            if pyproject_path.exists():
                # Python 3.11+ tomllib 내장, 이하 버전은 tomli 사용
                if sys.version_info >= (3, 11):
                    import tomllib
                else:
                    import tomli as tomllib
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                return data.get("project", {}).get("version", "0.0.0-dev")
        except Exception:
            pass
        return "0.0.0-dev"


__version__ = _load_version()
