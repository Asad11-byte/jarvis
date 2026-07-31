"""
Vercel entrypoint (monorepo deployment).

Vercel's Python runtime looks for a variable named `app` in this file.
Our real FastAPI app lives in app/main.py, mounted under an /api prefix
(see main.py) so it never collides with the frontend's own routes on the
same domain. app/main.py uses absolute imports like `from app.config
import settings` -- those only resolve if the backend/ directory (the
parent of this api/ folder) is on sys.path. We add it explicitly before
importing, so nothing in app/main.py or anything it imports needs to
change for deployment. This works whether backend/ is deployed on its
own or, as here, as one of two builds in a monorepo -- the path logic is
relative to this file, not to the repo root.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402  (import after sys.path fix, intentional)