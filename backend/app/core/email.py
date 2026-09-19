import resend

from app.core.config import settings


def _template(title: str, otp: str, note: str) -> str:
    return f"""
    ```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>

<body style="
  margin:0;
  padding:0;
  background:#050505;
  font-family:Inter,Arial,Helvetica,sans-serif;
  color:#ffffff;
">

  <div style="
    width:100%;
    background:
      radial-gradient(circle at 50% -20%, #222 0%, #0b0b0b 35%, #050505 70%);
    padding:48px 20px;
    box-sizing:border-box;
  ">

    <div style="
      max-width:520px;
      margin:0 auto;
    ">

      <!-- Logo -->
      <div style="
        text-align:center;
        margin-bottom:28px;
      ">
        <div style="
          display:inline-block;
          font-size:25px;
          font-weight:800;
          letter-spacing:-1px;
          color:#ffffff;
        ">
          Campus<span style="color:#8b8b8b;">GPT</span>
        </div>
      </div>


      <!-- Main Card -->
      <div style="
        background:#0d0d0d;
        border:1px solid #242424;
        border-radius:20px;
        padding:38px 32px;
        box-shadow:
          0 20px 60px rgba(0,0,0,0.45),
          inset 0 1px 0 rgba(255,255,255,0.03);
        text-align:center;
      ">

        <!-- Small Badge -->
        <div style="
          display:inline-block;
          padding:6px 12px;
          border-radius:999px;
          background:#171717;
          border:1px solid #292929;
          color:#a3a3a3;
          font-size:11px;
          font-weight:600;
          letter-spacing:0.8px;
          text-transform:uppercase;
          margin-bottom:20px;
        ">
          Security Verification
        </div>


        <!-- Title -->
        <h1 style="
          margin:0 0 12px;
          font-size:26px;
          line-height:1.3;
          font-weight:750;
          letter-spacing:-0.5px;
          color:#ffffff;
        ">
          {title}
        </h1>


        <!-- Description -->
        <p style="
          margin:0 auto;
          max-width:390px;
          color:#a1a1a1;
          font-size:14px;
          line-height:1.7;
        ">
          {note}
        </p>


        <!-- OTP Container -->
        <div style="
          margin:28px 0 18px;
          padding:20px 16px;
          background:#111111;
          border:1px solid #2b2b2b;
          border-radius:14px;
        ">

          <div style="
            color:#666666;
            font-size:10px;
            font-weight:700;
            letter-spacing:2px;
            text-transform:uppercase;
            margin-bottom:10px;
          ">
            Verification Code
          </div>

          <div style="
            font-size:36px;
            line-height:1.2;
            letter-spacing:10px;
            font-weight:800;
            color:#ffffff;
            padding-left:10px;
            white-space:nowrap;
          ">
            {otp}
          </div>

        </div>


        <!-- Expiry -->
        <div style="
          display:inline-block;
          padding:8px 12px;
          border-radius:8px;
          background:#161616;
          color:#888888;
          font-size:12px;
        ">
          ⏱ Expires in <strong style="color:#cfcfcf;">10 minutes</strong>
        </div>


        <!-- Security Notice -->
        <div style="
          margin-top:28px;
          padding-top:22px;
          border-top:1px solid #202020;
          text-align:left;
        ">

          <p style="
            margin:0;
            color:#707070;
            font-size:12px;
            line-height:1.7;
          ">
            <strong style="color:#999999;">Didn't request this?</strong><br>
            You can safely ignore this email. Your account remains secure.
          </p>

        </div>

      </div>


      <!-- Footer -->
      <div style="
        text-align:center;
        padding:26px 10px 0;
      ">

        <p style="
          margin:0 0 8px;
          color:#555555;
          font-size:11px;
        ">
          © CampusGPT · Built for students
        </p>

        <p style="
          margin:0;
          color:#3f3f3f;
          font-size:10px;
        ">
          This is an automated email. Please do not reply.
        </p>

      </div>

    </div>

  </div>

</body>
</html>
```

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
