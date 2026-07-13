"""Pytest path setup so tests can import both `backend.*` package paths
and the flat module imports used inside backend/api and backend/model."""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")

for path in (
    REPO_ROOT,
    BACKEND_DIR,
    os.path.join(BACKEND_DIR, "api"),
    os.path.join(BACKEND_DIR, "model"),
):
    if path not in sys.path:
        sys.path.insert(0, path)
