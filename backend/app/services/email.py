import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from backend.app.core.config import settings

logger = logging.getLogger("exampilot.email")

class BaseEmailService:
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
        raise NotImplementedError

class ConsoleEmailService(BaseEmailService):
    """
    Development and test email service.
    Captures sent emails in memory for unit/integration testing while logging sanitized info.
    Never logs the plain token in production logs.
    """
    def __init__(self):
        self.sent_emails: List[Dict[str, Any]] = []

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
        name = user_name or "Student"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        email_record = {
            "to": to_email,
            "subject": "ExamPilot 2.0 — Password Reset Request",
            "reset_url": reset_url,
            "reset_token": reset_token, # Stored in memory only for test verification
            "user_name": name
        }
        self.sent_emails.append(email_record)
        logger.info(f"Password reset email dispatched to {to_email} (Console adapter)")
        return True

    def get_last_reset_token(self, email: str) -> Optional[str]:
        for e in reversed(self.sent_emails):
            if e["to"].lower() == email.lower():
                return e["reset_token"]
        return None

    def clear(self):
        self.sent_emails.clear()

class SMTPEmailService(BaseEmailService):
    """
    Production SMTP email delivery service.
    Dispatches HTML and plaintext password reset emails via TLS SMTP.
    """
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.error("SMTP configuration missing. Cannot send password reset email.")
            return False

        name = user_name or "Student"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "ExamPilot 2.0 — Password Reset Instructions"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        text_content = (
            f"Hello {name},\n\n"
            f"A password reset request was received for your ExamPilot 2.0 account.\n\n"
            f"Please visit the following secure link to reset your password within {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes:\n"
            f"{reset_url}\n\n"
            f"If you did not request this password reset, you can safely ignore this email.\n\n"
            f"— The ExamPilot 2.0 Security Team (GT InnoX LLP)"
        )

        html_content = f"""
        <html>
          <body style="font-family: sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #0f172a; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
              <h1 style="color: #38bdf8; margin: 0;">ExamPilot 2.0</h1>
              <p style="color: #94a3b8; margin: 5px 0 0 0;">Understand Questions. Learn the Answers.</p>
            </div>
            <div style="border: 1px solid #e2e8f0; border-top: none; padding: 30px; border-radius: 0 0 8px 8px;">
              <h2>Password Reset Request</h2>
              <p>Hello {name},</p>
              <p>A request was received to reset the password for your ExamPilot account (<strong>{to_email}</strong>).</p>
              <p style="margin: 30px 0; text-align: center;">
                <a href="{reset_url}" style="background-color: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                  Reset Your Password
                </a>
              </p>
              <p style="font-size: 0.9em; color: #64748b;">
                This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes. If you did not make this request, no changes will be made to your account.
              </p>
              <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
              <p style="font-size: 0.8em; color: #94a3b8;">GT InnoX LLP • ExamPilot Security Team</p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10.0) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                if settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Password reset email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch password reset email: {str(e)}")
            return False

def get_email_service() -> BaseEmailService:
    provider = getattr(settings, "EMAIL_PROVIDER", "console").lower()
    if provider == "smtp":
        return SMTPEmailService()
    return ConsoleEmailService()

email_service = get_email_service()

