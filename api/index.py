"""
Vercel entrypoint (root-level, per the includeFiles: "backend/**" pattern).

This file lives at the TRUE repo root (api/index.py), not inside backend/.
Vercel's `functions` config in vercel.json bundles the entire backend/
directory alongside this file at deploy time, so we add backend/ to
sys.path here and import the real FastAPI app from backend/app/main.py.
Nothing inside app/main.py or anything it imports needs to know about
any of this -- it still just does `from app.config import settings` etc,
which resolves correctly once backend/ is on the path.
"""
import os
import sys

_API_DIR = os.path.dirname(os.path.abspath(__file__))       # .../api
_REPO_ROOT = os.path.dirname(_API_DIR)                       # repo root
_BACKEND_DIR = os.path.join(_REPO_ROOT, "backend")            # repo root/backend

sys.path.insert(0, _BACKEND_DIR)

from app.main import app  # noqa: E402  (import after sys.path fix, intentional)