"""
Email service — Send emails via Gmail SMTP.

Uses Gmail App Password (not OAuth) for simplicity.
Requires: GMAIL_USER and GMAIL_APP_PASSWORD env vars.

If not configured, emails are logged instead of sent.
"""

from __future__ import annotations

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _send_email(to: str, subject: str, html_body: str) -> bool:
    """Send an email via Gmail SMTP. Returns True on success."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.info("Email not configured. Would send to %s: %s", to, subject)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"AI Marketing Hub <{GMAIL_USER}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to, msg.as_string())

        logger.info("Email sent to %s: %s", to, subject)
        return True

    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def send_welcome_email(to: str, name: str) -> bool:
    """Send a welcome email after registration."""
    subject = "🎉 Chào mừng bạn đến với AI Marketing Hub!"
    html = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 40px 20px;">
      <div style="background: #ffffff; border-radius: 16px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);">
        <div style="text-align: center; margin-bottom: 30px;">
          <div style="display: inline-block; width: 60px; height: 60px; background: linear-gradient(135deg, #8b5cf6, #06b6d4); border-radius: 16px; line-height: 60px; font-size: 28px; color: white;">✓</div>
        </div>
        <h1 style="color: #1a1a2e; font-size: 24px; text-align: center; margin: 0 0 16px;">Chào mừng, {name}! 🚀</h1>
        <p style="color: #6b7280; font-size: 15px; line-height: 1.6; text-align: center;">
          Tài khoản của bạn đã được tạo thành công trên <strong>AI Marketing Hub</strong> — nền tảng SEO & Marketing thông minh.
        </p>
        <div style="text-align: center; margin: 30px 0;">
          <a href="https://trannhuy.online" style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #06b6d4); color: #fff; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 15px;">
            Bắt đầu sử dụng →
          </a>
        </div>
        <div style="background: #f0f4ff; border-radius: 10px; padding: 16px; margin-top: 20px;">
          <p style="color: #4b5563; font-size: 13px; margin: 0; line-height: 1.5;">
            <strong>Bạn có thể:</strong><br>
            ✅ Kiểm tra SEO cho website<br>
            ✅ Phân tích từ khóa bằng AI<br>
            ✅ Viết bài tự động với Groq LLaMA 3.3<br>
            ✅ Theo dõi thứ hạng keyword
          </p>
        </div>
      </div>
      <p style="color: #9ca3af; font-size: 11px; text-align: center; margin-top: 20px;">
        AI Marketing Hub · Nền tảng SEO & Marketing thông minh
      </p>
    </div>
    """
    return _send_email(to, subject, html)


def send_alert_email(to: str, subject: str, message: str) -> bool:
    """Send a generic alert email."""
    html = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 40px 20px;">
      <div style="background: #ffffff; border-radius: 16px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);">
        <h2 style="color: #1a1a2e; font-size: 20px; margin: 0 0 16px;">⚠️ {subject}</h2>
        <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">{message}</p>
        <div style="text-align: center; margin-top: 24px;">
          <a href="https://trannhuy.online" style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #06b6d4); color: #fff; text-decoration: none; padding: 12px 28px; border-radius: 10px; font-weight: 600; font-size: 14px;">
            Xem chi tiết →
          </a>
        </div>
      </div>
    </div>
    """
    return _send_email(to, subject, html)
