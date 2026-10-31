"""Run from backend folder: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Or use backend\\run.bat. Running from backend/app with main:app also works (path fix below)."""
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

import time

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.auth import get_current_user, hash_password, verify_password
from app.database import Base, SessionLocal, engine, get_db, test_connection
from app.models import User

from app.routers import (
    auth,
    daily,
    dashboard,
    expense,
    feed,
    harvest,
    ponds,
    reports_settings,
    seed_stocking,
    ml_api,
)


# =========================================================
# FRONTEND PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FRONTEND = ROOT / "frontend"
PAGES = FRONTEND / "pages"
CSS = FRONTEND / "css"
JS = FRONTEND / "js"


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AquaControl API",
    version="2.0.0",
)

# Alias for running with `uvicorn app.main:main`
main = app


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aquafarmcontrol.vercel.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth.router)
app.include_router(ponds.router)
app.include_router(daily.router)
app.include_router(feed.router)
app.include_router(expense.router)
app.include_router(harvest.router)
app.include_router(seed_stocking.router)
app.include_router(dashboard.router)
app.include_router(reports_settings.router)

# AI prediction routes
app.include_router(ml_api.router)


@app.post("/api/predict-all")
@app.post("/api/predict-all/")
@app.post("/api/predict")
@app.post("/api/predict/")
def predict_all_alias(
    payload: ml_api.PredictAllRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ml_api.predict_all(payload=payload, db=db, user=user)


# =========================================================
# STATIC FRONTEND FILES
# =========================================================

app.mount(
    "/css",
    StaticFiles(directory=str(CSS)),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=str(JS)),
    name="js",
)


# =========================================================
# ADMIN SEED
# =========================================================

def seed_admin(db: Session) -> None:

    email = "admin@shrimpfarm.com"
    password = "admin123"

    existing = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing:

        # Repair sample admin if password hash
        # is invalid or outdated
        if not verify_password(
            password,
            existing.password,
        ):
            existing.password = hash_password(password)
            db.commit()

        return

    db.add(
        User(
            full_name="Farm Admin",
            email=email,
            password=hash_password(password),
            role="Farm Owner",
        )
    )

    db.commit()


# =========================================================
# DATABASE STARTUP
# =========================================================

@app.on_event("startup")
def on_startup() -> None:

    """
    Connect to Neon, create tables,
    seed admin and retry temporary
    connection failures.
    """

    last_error: Exception | None = None

    for attempt in range(1, 4):

        try:

            # Test Neon/PostgreSQL connection
            info = test_connection()

            Base.metadata.create_all(bind=engine)
            print(f"Database tables ready ({len(Base.metadata.tables)} tables).")

            # Seed admin account
            db = SessionLocal()

            try:
                seed_admin(db)

            finally:
                db.close()

            print(
                f"Database connected OK "
                f"(attempt {attempt})."
            )

            if info.get("version"):

                print(
                    f"Postgres: "
                    f"{str(info['version'])[:80]}..."
                )

            return

        except Exception as exc:

            last_error = exc

            print(
                f"Database connect attempt "
                f"{attempt}/3 failed: {exc}"
            )

            if attempt < 3:
                time.sleep(2)

    # Keep FastAPI running even if Neon
    # is temporarily unavailable.

    print(
        "WARNING: Could not reach Neon Postgres. "
        "Check internet/DNS, VPN/firewall, "
        "and DATABASE_URL in backend/.env. "
        "The API is running but DB routes "
        "will fail until connectivity returns.\n"
        f"Last error: {last_error}"
    )


# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.get("/")
def root():

    return FileResponse(
        FRONTEND / "index.html"
    )


@app.get("/index.html")
def login_page():

    return FileResponse(
        FRONTEND / "index.html"
    )


@app.get("/pages/{page_name}")
def serve_page(page_name: str):

    # Allow .html pages only
    # from frontend/pages/

    if not page_name.endswith(".html"):
        page_name = f"{page_name}.html"

    target = PAGES / page_name

    if not target.exists() or not target.is_file():
        return RedirectResponse(
            url="/"
        )

    return FileResponse(target)


@app.get("/{page_name}.html")
def serve_page_direct(page_name: str):
    target = PAGES / f"{page_name}.html"
    if target.exists() and target.is_file():
        return FileResponse(target)
    root_target = FRONTEND / f"{page_name}.html"
    if root_target.exists() and root_target.is_file():
        return FileResponse(root_target)
    return RedirectResponse(url="/")


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    try:

        info = test_connection()

        return {
            "status": "ok",
            "database": "connected",
            "postgres": info.get("version"),
        }

    except Exception as exc:

        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }