import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import get_settings
from app.database import get_db
from app.email_service import send_otp_email
from app.models import PendingRegistration, User
from app.schemas import (
    LoginIn,
    MessageOut,
    RegisterIn,
    RegisterPendingOut,
    ResendOtpIn,
    UserOut,
    VerifyOtpIn,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _cookie_flags(request: Request) -> tuple[bool, str]:
    # Cross-site frontends (Vercel → Render) need SameSite=None; Secure.
    # Local HTTP same-origin uses Lax when COOKIE_SECURE is false.
    secure = settings.cookie_secure or request.url.scheme == "https"
    samesite = "none" if secure else "lax"
    return secure, samesite


def set_auth_cookie(response: Response, user_id: int, request: Request) -> None:
    token = create_access_token(user_id)
    secure, samesite = _cookie_flags(request)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        samesite=samesite,
        secure=secure,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _generate_otp() -> str:
    length = max(4, min(settings.otp_length, 12))
    upper = 10**length
    return str(secrets.randbelow(upper)).zfill(length)


def _otp_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=settings.otp_expiry_seconds)


def _reload_settings() -> None:
    global settings
    get_settings.cache_clear()
    settings = get_settings()


def _issue_pending_otp(pending: PendingRegistration) -> None:
    """Generate OTP and email it. Does not commit — caller commits only after success."""
    pending.otp_code = _generate_otp()
    pending.otp_expiry = _otp_expiry()
    try:
        send_otp_email(pending.email, pending.otp_code, settings.otp_expiry_seconds)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register", response_model=RegisterPendingOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """Start signup: store pending registration and email a 6-digit OTP (RentYaar-style)."""
    _reload_settings()

    full_name = payload.full_name.strip()
    email = str(payload.email).strip().lower()
    password = payload.password.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="Please enter your full name.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please sign in instead.",
        )

    pending = db.query(PendingRegistration).filter(PendingRegistration.email == email).first()
    if pending:
        pending.full_name = full_name
        pending.password = hash_password(password)
    else:
        pending = PendingRegistration(
            full_name=full_name,
            email=email,
            password=hash_password(password),
            otp_code="000000",
            otp_expiry=_otp_expiry(),
        )
        db.add(pending)

    # Email first; only persist OTP after SMTP accepts the message
    _issue_pending_otp(pending)
    db.commit()

    return {
        "message": "Verification code sent to your email. Check inbox and spam.",
        "email": email,
        "expires_in": settings.otp_expiry_seconds,
    }


@router.post("/verify-otp", response_model=UserOut)
def verify_otp(
    payload: VerifyOtpIn,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()
    otp_code = payload.otp_code.strip()

    pending = db.query(PendingRegistration).filter(PendingRegistration.email == email).first()
    if not pending:
        raise HTTPException(
            status_code=400,
            detail="No pending registration found. Please register again.",
        )

    if pending.otp_code != otp_code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    expiry = pending.otp_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(status_code=400, detail="Verification code expired. Please resend.")

    if db.query(User).filter(User.email == email).first():
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please sign in instead.",
        )

    user = User(
        full_name=pending.full_name,
        email=pending.email,
        password=pending.password,
        role="Farmer",
    )
    db.add(user)
    db.delete(pending)
    db.commit()
    db.refresh(user)
    set_auth_cookie(response, user.id, request)
    return user


@router.post("/resend-otp", response_model=RegisterPendingOut)
def resend_otp(payload: ResendOtpIn, db: Session = Depends(get_db)):
    _reload_settings()

    email = str(payload.email).strip().lower()
    pending = db.query(PendingRegistration).filter(PendingRegistration.email == email).first()
    if not pending:
        raise HTTPException(
            status_code=400,
            detail="No pending registration found. Please register again.",
        )

    _issue_pending_otp(pending)
    db.commit()

    return {
        "message": "A new verification code has been sent. Check inbox and spam.",
        "email": email,
        "expires_in": settings.otp_expiry_seconds,
    }


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, request: Request, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    password = payload.password.strip()
    if not password:
        raise HTTPException(status_code=400, detail="Please enter your password.")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Wrong email or password. Please try again.")

    set_auth_cookie(response, user.id, request)
    return user


@router.post("/logout", response_model=MessageOut)
def logout(response: Response, request: Request):
    secure, samesite = _cookie_flags(request)
    response.delete_cookie(
        settings.cookie_name,
        path="/",
        samesite=samesite,
        secure=secure,
    )
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
