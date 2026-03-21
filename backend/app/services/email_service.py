import smtplib
import imaplib
import email
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from app.core.config import settings
from app.models.email_message import EmailMessage
from app.models.user import User
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.imap_server = "imap.gmail.com"
        self.port = 587
        self.imap_port = 993
        self.sender_email = settings.SMTP_USER
        self.password = settings.SMTP_PASS
    
    def send_otp(self, recipient_email: str, otp: str) -> bool:
        # Code remains same but using self.sender_email and self.password
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "DHQ - Your Verification Code"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            html = f"""
            <html>
              <body>
                <h2>Digital Headquarters - Verification Code</h2>
                <p>Your 6-digit verification code is:</p>
                <h1 style="font-size: 32px; color: #007bff; letter-spacing: 8px;">{otp}</h1>
                <p>This code will expire in 5 minutes.</p>
                <p><strong>Do not share this code with anyone.</strong></p>
                <hr>
                <p><small>If you didn't request this code, please ignore this email.</small></p>
              </body>
            </html>
            """
            message.attach(MIMEText(html, "html"))
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP to {recipient_email}: {str(e)}")
            return False

    def fetch_emails(self, user: User, limit: int = 20):
        """Fetch unread emails using IMAP PEEK to avoid marking as seen"""
        if not user.email_creds or not user.email_creds.get('email') or not user.email_creds.get('password'):
            logger.warning(f"No email credentials for user {user.username}")
            return []

        email_user = user.email_creds['email']
        email_pass = user.email_creds['password']
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(email_user, email_pass)
            mail.select("inbox")

            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                return []

            email_ids = messages[0].split()
            # Get latest 20
            latest_ids = email_ids[-limit:]
            latest_ids.reverse() # Process newest first

            fetched_messages = []

            for e_id in latest_ids:
                # Use BODY.PEEK[] to keep it unread
                status, msg_data = mail.fetch(e_id, '(BODY.PEEK[])')
                if status != 'OK':
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Extract Headers
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        sender_raw = msg.get("From")
                        sender_name, sender_email = self._parse_sender(sender_raw)
                        message_id = msg.get("Message-ID")

                        # Check if already processed
                        if EmailMessage.objects(user=user, message_id=message_id).first():
                            continue

                        # Extract Body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        # Detect Urgency
                        urgency = "Normal"
                        if re.search(r'\b(ASAP|deadline|urgent|this week|important|now)\b', (subject + " " + body), re.I):
                            urgency = "High"

                        email_doc = EmailMessage(
                            user=user,
                            message_id=message_id,
                            uid=e_id.decode(),
                            sender_name=sender_name,
                            sender_email=sender_email,
                            subject=subject,
                            body=body,
                            urgency=urgency,
                            status='Unprocessed'
                        )
                        email_doc.save()
                        fetched_messages.append(email_doc)

            mail.close()
            mail.logout()
            return fetched_messages

        except Exception as e:
            logger.error(f"IMAP Error for {user.username}: {str(e)}")
            return []

    def _parse_sender(self, sender_raw):
        if not sender_raw:
            return "Unknown", "Unknown"
        
        match = re.match(r'(?P<name>.*)<(?P<email>.*)>', sender_raw)
        if match:
            return match.group("name").strip().strip('"'), match.group("email").strip()
        return "Unknown", sender_raw.strip()

email_service = EmailService()

