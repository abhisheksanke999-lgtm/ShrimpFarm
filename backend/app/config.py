from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str = "postgresql://neondb_owner:npg_ifFDhpaU70Xy@ep-summer-lake-azw67k8n-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    cookie_name: str = "aquacontrol_token"
    # True required for cross-origin auth (Vercel → Render). Set false for local HTTP same-origin.
    cookie_secure: bool = True
    algorithm: str = "HS256"

    # HTTPS email APIs (required on Render — SMTP ports are blocked there)
    brevo_api_key: str = ""
    resend_api_key: str = ""

    # Gmail SMTP (works on local PC; blocked on Render free tier)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_from_name: str = "AquaControl"
    # If true and no email provider works, print OTP to server logs (local only).
    allow_console_otp: bool = False
    otp_expiry_seconds: int = 300
    otp_length: int = 6

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
