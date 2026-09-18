import resend

from app.core.config import settings


def _template(title: str, otp: str, note: str) -> str:
    return f"""
    <div style="background:#000;color:#fff;font-family:Inter,Arial,sans-serif;padding:40px 24px">
      <div style="max-width:520px;margin:auto;border:1px solid #292929;border-radius:18px;padding:32px">
        <div style="font-size:22px;font-weight:700;margin-bottom:28px">Campus<span style="color:#999">GPT</span></div>
        <h1 style="font-size:24px;margin:0 0 12px">{title}</h1>
        <p style="color:#b3b3b3;line-height:1.6">{note}</p>
        <div style="font-size:40px;letter-spacing:12px;font-weight:700;padding:22px 0;color:#fff">{otp}</div>
        <p style="color:#777;font-size:13px">This code expires in 10 minutes.</p>
      </div>
    </div>
    """


def send_email(to: str, subject: str, html_body: str) -> None:
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is not configured")
    resend.api_key = settings.RESEND_API_KEY
    try:
        resend.Emails.send(
            {"from": settings.EMAIL_FROM, "to": [to], "subject": subject, "html": html_body}
        )
    except Exception as exc:
        raise RuntimeError("Unable to send email right now") from exc


def verification_email(otp: str) -> str:
    return _template("Verify your email", otp, "Use this code to verify your CampusGPT account.")


def reset_email(otp: str) -> str:
    return _template(
        "Reset your password",
        otp,
        "Use this code to choose a new password. If you did not request this, you can safely ignore this email.",
    )
