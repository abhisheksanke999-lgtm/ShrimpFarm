from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.database import Base, SessionLocal, engine, test_connection
from app.models import User
from app.routers import auth, daily, dashboard, expense, feed, harvest, ponds, reports_settings

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "pages"
CSS = ROOT / "css"
JS = ROOT / "js"

app = FastAPI(title="AquaControl API", version="2.0.0")

# Allow Live Server (and similar static hosts) to call the API with cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ponds.router)
app.include_router(daily.router)
app.include_router(feed.router)
app.include_router(expense.router)
app.include_router(harvest.router)
app.include_router(dashboard.router)
app.include_router(reports_settings.router)

app.mount("/css", StaticFiles(directory=str(CSS)), name="css")
app.mount("/js", StaticFiles(directory=str(JS)), name="js")


def seed_admin(db: Session) -> None:
    email = "admin@shrimpfarm.com"
    password = "admin123"
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        # Repair sample admin if password hash is invalid/outdated
        if not verify_password(password, existing.password):
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


@app.on_event("startup")
def on_startup() -> None:
    # Verify Neon/Postgres connection, then create tables
    test_connection()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/pages/login.html")


@app.get("/pages/{page_name}")
def serve_page(page_name: str):
    # Allow .html pages only from pages/
    if not page_name.endswith(".html"):
        page_name = f"{page_name}.html"
    target = PAGES / page_name
    if not target.exists() or not target.is_file():
        return RedirectResponse(url="/pages/login.html")
    return FileResponse(target)


@app.get("/health")
def health():
    try:
        info = test_connection()
        return {"status": "ok", "database": "connected", "postgres": info.get("version")}
    except Exception as exc:
        return {"status": "error", "database": "disconnected", "detail": str(exc)}
