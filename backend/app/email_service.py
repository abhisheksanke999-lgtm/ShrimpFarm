"""SMTP email helpers (Gmail-compatible), same approach as RentYaar MailKit SMTP."""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_otp_email(to_email: str, otp_code: str, expiry_seconds: int) -> None:
    settings = get_settings()
    subject = "AquaControl - Email Verification Code"
    minutes = max(1, expiry_seconds // 60)
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2 style="color: #0d6efd;">AquaControl email verification</h2>
        <p>Your verification code is:</p>
        <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">{otp_code}</p>
        <p>This code expires in <strong>{minutes} minute(s)</strong>. Do not share it with anyone.</p>
        <p>— AquaControl Team</p>
      </body>
    </html>
    """

    if not (settings.smtp_host or "").strip():
        # Local/dev fallback when SMTP is not configured
        logger.warning(
            "SMTP not configured. OTP for %s: %s (expires in %ss)",
            to_email,
            otp_code,
            expiry_seconds,
        )
        print(f"[OTP] {to_email} => {otp_code} (expires in {expiry_seconds}s)")
        return

    from_email = (settings.email_from or settings.smtp_username).strip()
    if not from_email or not settings.smtp_username or not settings.smtp_password:
        raise RuntimeError(
            "Email is not configured. Set SMTP_USERNAME, SMTP_PASSWORD, and EMAIL_FROM in backend/.env"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.email_from_name} <{from_email}>"
    msg["To"] = to_email
    msg.attach(MIMEText(f"Your AquaControl verification code is {otp_code}", "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host.strip(), int(settings.smtp_port), timeout=30) as client:
            client.ehlo()
            client.starttls()
            client.ehlo()
            client.login(settings.smtp_username.strip(), settings.smtp_password.strip())
            client.sendmail(from_email, [to_email], msg.as_string())
        logger.info("OTP email sent to %s", to_email)
    except Exception as exc:
        logger.exception("Failed to send OTP email to %s", to_email)
        raise RuntimeError(
            "Could not send verification email. Check SMTP settings or try again."
        ) from exc
