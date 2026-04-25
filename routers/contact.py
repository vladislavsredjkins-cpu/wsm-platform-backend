from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import resend
import os

router = APIRouter(prefix="/api/contact", tags=["contact"])

resend.api_key = os.getenv("RESEND_API_KEY")

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    source: str = "ranking.worldstrongman.org"

@router.post("")
async def send_contact(form: ContactForm):
    try:
        # Email to WSM team
        resend.Emails.send({
            "from": "WSM Platform <noreply@ranking.worldstrongman.org>",
            "to": ["gensec@worldstrongman.org"],
            "reply_to": form.email,
            "subject": f"[{form.source}] {form.subject}",
            "html": f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 20px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;">

  <tr><td style="background:#111;border-radius:16px 16px 0 0;padding:24px 32px;border-bottom:2px solid #c9a84c;">
    <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" width="60" alt="WSM" style="margin-bottom:12px;display:block;"/>
    <div style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">New Contact Message</div>
    <div style="color:#fff;font-size:20px;font-weight:700;margin-top:4px;">{form.subject}</div>
  </td></tr>

  <tr><td style="background:#161616;padding:32px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid #222;">
          <div style="color:#888;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">From</div>
          <div style="color:#fff;font-size:14px;font-weight:600;">{form.name}</div>
        </td>
      </tr>
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid #222;">
          <div style="color:#888;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Email</div>
          <div style="color:#c9a84c;font-size:14px;">{form.email}</div>
        </td>
      </tr>
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid #222;">
          <div style="color:#888;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Source</div>
          <div style="color:#fff;font-size:14px;">{form.source}</div>
        </td>
      </tr>
      <tr>
        <td style="padding:16px 0;">
          <div style="color:#888;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Message</div>
          <div style="color:#ddd;font-size:14px;line-height:1.7;background:#1e1e1e;padding:16px;border-radius:8px;border-left:3px solid #c9a84c;">{form.message}</div>
        </td>
      </tr>
    </table>

    <div style="margin-top:20px;text-align:center;">
      <a href="mailto:{form.email}" style="display:inline-block;background:#c9a84c;color:#000;font-size:14px;font-weight:700;padding:12px 28px;border-radius:8px;text-decoration:none;">
        Reply to {form.name} →
      </a>
    </div>
  </td></tr>

  <tr><td style="background:#0d0d0d;padding:16px 32px;border-radius:0 0 16px 16px;text-align:center;border-top:1px solid #1a1a1a;">
    <div style="color:#444;font-size:11px;">© 2026 World Strongman International Union</div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>
            """
        })

        # Auto-reply to sender
        resend.Emails.send({
            "from": "WSM Platform <noreply@ranking.worldstrongman.org>",
            "to": [form.email],
            "subject": "We received your message — World Strongman",
            "html": f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 20px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;">

  <tr><td style="background:#111;border-radius:16px 16px 0 0;padding:24px 32px;text-align:center;border-bottom:2px solid #c9a84c;">
    <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" width="60" alt="WSM" style="margin-bottom:12px;"/>
    <div style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">World Strongman International Union</div>
  </td></tr>

  <tr><td style="background:#161616;padding:36px;text-align:center;">
    <div style="font-size:40px;margin-bottom:16px;">✅</div>
    <div style="color:#fff;font-size:22px;font-weight:700;margin-bottom:10px;">Message Received!</div>
    <div style="color:#aaa;font-size:15px;line-height:1.7;margin-bottom:24px;">
      Dear {form.name},<br/><br/>
      Thank you for contacting World Strongman International Union.<br/>
      We have received your message and will respond within <strong style="color:#fff;">24–48 hours</strong>.
    </div>

    <div style="background:#1e1e1e;border-radius:10px;padding:16px 20px;text-align:left;margin-bottom:24px;border-left:3px solid #c9a84c;">
      <div style="color:#888;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Your message</div>
      <div style="color:#ddd;font-size:13px;line-height:1.6;">{form.message[:200]}{"..." if len(form.message) > 200 else ""}</div>
    </div>

    <div style="color:#aaa;font-size:13px;margin-bottom:20px;">
      📍 Riga, Latvia | Dubai, UAE<br/>
      ✉️ gensec@worldstrongman.org &nbsp;·&nbsp; <a href="https://wa.me/971542301001" style="display:inline-block;background:#25D366;color:#fff;font-size:12px;font-weight:700;padding:4px 12px;border-radius:6px;text-decoration:none;">💬 WhatsApp</a>
    </div>

    <a href="https://worldstrongman.org" style="display:inline-block;background:#c9a84c;color:#000;font-size:14px;font-weight:700;padding:12px 28px;border-radius:8px;text-decoration:none;">
      Visit WSM Website →
    </a>
  </td></tr>

  <tr><td style="background:#0d0d0d;padding:16px 32px;border-radius:0 0 16px 16px;text-align:center;border-top:1px solid #1a1a1a;">
    <div style="color:#444;font-size:11px;">© 2026 World Strongman International Union · All Rights Reserved</div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>
            """
        })

        return {"status": "ok", "message": "Message sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
