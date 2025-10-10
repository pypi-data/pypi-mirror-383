#!/usr/bin/env python3
"""
General Python project cleanup script.

Removes build artifacts, cache folders, temporary files, 
and setuptools_scm version files (e.g., _version.py).

Usage:
    python clean_build_dirs.py [project_root]
If no argument is given, uses the current working directory.
"""

import os
import shutil
import sys
from pathlib import Path

# Common directories to remove
CLEAN_DIRS = [
    "build", "dist", "*.egg-info", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".nox", ".tox"
]

# Common file patterns to remove
CLEAN_FILES = [
    "*.pyc", "*.pyo", "*~", "._*", "_version.py"
]

def remove_path(path: Path):
    """Remove a file or directory safely."""
    try:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"🗑️ Removed directory: {path}")
        elif path.is_file():
            path.unlink()
            print(f"🗑️ Removed file: {path}")
    except Exception as e:
        print(f"⚠️ Could not remove {path}: {e}")

def clean(root: Path):
    """Recursively remove unwanted build artifacts."""
    for pattern in CLEAN_DIRS + CLEAN_FILES:
        for match in root.rglob(pattern):
            remove_path(match)

if __name__ == "__main__":
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(f"🚀 Cleaning Python project at: {project_root}")
    clean(project_root)
    print("✅ Cleanup complete.")
