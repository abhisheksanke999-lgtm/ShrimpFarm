"""Send OTP email.

Render (and many hosts) block outbound SMTP ports 587/465 → Errno 101 Network unreachable.
Prefer HTTPS providers (Brevo / Resend) on production; fall back to Gmail SMTP locally.
"""

from __future__ import annotations

import json
import logging
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

from app.config import get_settings

logger = logging.getLogger(__name__)


def _smtp_password(raw: str) -> str:
    return (raw or "").replace(" ", "").strip()


def _build_bodies(otp_code: str, expiry_seconds: int) -> tuple[str, str, str]:
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
    return subject, text_body, html_body


def _http_json(url: str, payload: dict, headers: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status}: {body}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def _send_via_brevo(
    api_key: str,
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> None:
    _http_json(
        "https://api.brevo.com/v3/smtp/email",
        {
            "sender": {"name": from_name, "email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body,
        },
        {
            "api-key": api_key,
            "accept": "application/json",
            "content-type": "application/json",
        },
    )


def _send_via_resend(
    api_key: str,
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> None:
    _http_json(
        "https://api.resend.com/emails",
        {
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        },
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )


def _send_via_smtp(
    host: str,
    port: int,
    username: str,
    password: str,
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> None:
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
            return
        except Exception as exc:
            errors.append(f"{mode}:{attempt_port} -> {exc}")
            logger.warning("SMTP attempt failed (%s:%s): %s", mode, attempt_port, exc)

    raise RuntimeError(" | ".join(errors) if errors else "SMTP failed")


def send_otp_email(to_email: str, otp_code: str, expiry_seconds: int) -> None:
    """Send OTP. Uses Brevo/Resend HTTPS first (works on Render), then Gmail SMTP."""
    settings = get_settings()
    from_email = (settings.email_from or settings.smtp_username or "").strip()
    from_name = (settings.email_from_name or "AquaControl").strip()
    subject, text_body, html_body = _build_bodies(otp_code, expiry_seconds)

    brevo_key = (settings.brevo_api_key or "").strip()
    resend_key = (settings.resend_api_key or "").strip()
    errors: list[str] = []

    # 1) HTTPS APIs (Render-safe — port 443)
    if brevo_key:
        if not from_email:
            raise RuntimeError("EMAIL_FROM is required when using BREVO_API_KEY.")
        try:
            _send_via_brevo(brevo_key, from_email, from_name, to_email, subject, text_body, html_body)
            logger.info("OTP email sent via Brevo to %s", to_email)
            print(f"[OTP email] sent via Brevo to {to_email}")
            return
        except Exception as exc:
            errors.append(f"brevo -> {exc}")
            logger.warning("Brevo send failed: %s", exc)

    if resend_key:
        sender = from_email or "AquaControl <onboarding@resend.dev>"
        if "@" not in sender:
            sender = f"{from_name} <{sender}>"
        try:
            # Resend expects from as "Name <email>"
            if "<" not in sender:
                sender = f"{from_name} <{from_email}>"
            _send_via_resend(
                resend_key,
                from_email or "onboarding@resend.dev",
                from_name,
                to_email,
                subject,
                text_body,
                html_body,
            )
            logger.info("OTP email sent via Resend to %s", to_email)
            print(f"[OTP email] sent via Resend to {to_email}")
            return
        except Exception as exc:
            errors.append(f"resend -> {exc}")
            logger.warning("Resend send failed: %s", exc)

    # 2) Gmail SMTP (works locally; blocked on Render free tier)
    host = (settings.smtp_host or "").strip()
    username = (settings.smtp_username or "").strip()
    password = _smtp_password(settings.smtp_password)
    port = int(settings.smtp_port or 587)

    if host and username and password and from_email:
        try:
            _send_via_smtp(
                host,
                port,
                username,
                password,
                from_email,
                from_name,
                to_email,
                subject,
                text_body,
                html_body,
            )
            print(f"[OTP email] sent via SMTP to {to_email}")
            return
        except Exception as exc:
            errors.append(f"smtp -> {exc}")
            detail = str(exc)
            if "Network is unreachable" in detail or "Errno 101" in detail:
                raise RuntimeError(
                    "Gmail SMTP is blocked on this server (Render blocks ports 587/465). "
                    "Add a free BREVO_API_KEY or RESEND_API_KEY in Render Environment, "
                    "verify sender email, redeploy, then try again."
                ) from exc

    if settings.allow_console_otp:
        logger.warning("ALLOW_CONSOLE_OTP: OTP for %s: %s", to_email, otp_code)
        print(f"[OTP] {to_email} => {otp_code} (expires in {expiry_seconds}s)")
        return

    if errors:
        raise RuntimeError(
            "Could not send verification email. "
            "On Render use BREVO_API_KEY (HTTPS). Details: " + " | ".join(errors)
        )

    raise RuntimeError(
        "Email is not configured. Set BREVO_API_KEY (recommended for Render) "
        "or SMTP_* vars for local Gmail SMTP, plus EMAIL_FROM."
    )
