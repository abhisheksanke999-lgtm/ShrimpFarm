from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import LoginIn, MessageOut, RegisterIn, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def set_auth_cookie(response: Response, user_id: int) -> None:
    token = create_access_token(user_id)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/register", response_model=UserOut)
def register(payload: RegisterIn, response: Response, db: Session = Depends(get_db)):
    full_name = payload.full_name.strip()
    email = str(payload.email).strip().lower()
    password = payload.password.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="Please enter your full name.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="This email is already registered. Please sign in instead.")

    user = User(
        full_name=full_name,
        email=email,
        password=hash_password(password),
        role="Farmer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    password = payload.password.strip()
    if not password:
        raise HTTPException(status_code=400, detail="Please enter your password.")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Wrong email or password. Please try again.")

    set_auth_cookie(response, user.id)
    return user


@router.post("/logout", response_model=MessageOut)
def logout(response: Response):
    response.delete_cookie(settings.cookie_name, path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
