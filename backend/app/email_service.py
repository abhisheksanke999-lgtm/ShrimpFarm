"""SMTP email helpers (Gmail-compatible). Fails closed if mail is not actually sent."""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

from app.config import get_settings

logger = logging.getLogger(__name__)


def _smtp_password(raw: str) -> str:
    # Gmail app passwords are often copied with spaces
    return (raw or "").replace(" ", "").strip()


def send_otp_email(to_email: str, otp_code: str, expiry_seconds: int) -> None:
    """Send OTP email via Gmail SMTP. Raises RuntimeError if delivery is not accepted."""
    settings = get_settings()
    host = (settings.smtp_host or "").strip()
    username = (settings.smtp_username or "").strip()
    password = _smtp_password(settings.smtp_password)
    from_email = (settings.email_from or username).strip()
    from_name = (settings.email_from_name or "AquaControl").strip()
    port = int(settings.smtp_port or 587)
    allow_console = bool(settings.allow_console_otp)

    if not host or not username or not password or not from_email:
        if allow_console:
            logger.warning(
                "SMTP not configured (ALLOW_CONSOLE_OTP). OTP for %s: %s",
                to_email,
                otp_code,
            )
            print(f"[OTP] {to_email} => {otp_code} (expires in {expiry_seconds}s)")
            return
        raise RuntimeError(
            "Email SMTP is not configured on the server. "
            "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and EMAIL_FROM "
            "(in backend/.env locally, or Render Environment for production)."
        )

    minutes = max(1, int(expiry_seconds) // 60)
    subject = "AquaControl - Email Verification Code"
    text_body = (
        f"Your AquaControl verification code is {otp_code}.\n"
        f"This code expires in {minutes} minute(s). Do not share it with anyone.\n"
    )
    html_body = f"""\
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #222;">
    <h2 style="color: #0d6efd;">AquaControl email verification</h2>
    <p>Your verification code is:</p>
    <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">{otp_code}</p>
    <p>This code expires in <strong>{minutes} minute(s)</strong>. Do not share it with anyone.</p>
    <p>— AquaControl Team</p>
  </body>
</html>
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
    msg["Reply-To"] = from_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    errors: list[str] = []

    # Prefer STARTTLS on 587 (Gmail standard), then SSL on 465
    attempts: list[tuple[str, int]] = [("starttls", port if port else 587)]
    if port != 465:
        attempts.append(("ssl", 465))

    for mode, attempt_port in attempts:
        try:
            if mode == "ssl":
                with smtplib.SMTP_SSL(host, attempt_port, timeout=30, context=context) as client:
                    client.ehlo()
                    client.login(username, password)
                    refused = client.send_message(msg)
            else:
                with smtplib.SMTP(host, attempt_port, timeout=30) as client:
                    client.ehlo()
                    client.starttls(context=context)
                    client.ehlo()
                    client.login(username, password)
                    refused = client.send_message(msg)

            if refused:
                raise RuntimeError(f"SMTP refused recipients: {refused}")

            logger.info("OTP email accepted by SMTP for %s via %s:%s", to_email, mode, attempt_port)
            print(f"[OTP email] accepted by Gmail SMTP for {to_email} ({mode}:{attempt_port})")
            return
        except Exception as exc:
            errors.append(f"{mode}:{attempt_port} -> {exc}")
            logger.warning("SMTP attempt failed (%s:%s): %s", mode, attempt_port, exc)

    detail = " | ".join(errors) if errors else "unknown error"
    logger.error("All SMTP attempts failed for %s: %s", to_email, detail)
    raise RuntimeError(
        "Could not send verification email via Gmail SMTP. "
        "Check the App Password, enable 2FA on the sender account, "
        f"and set SMTP env vars on the API host. Details: {detail}"
    )
