import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
ALERT_EMAIL_TO = os.getenv('ALERT_EMAIL_TO')
ALERT_EMAIL_FROM = os.getenv('ALERT_EMAIL_FROM', SMTP_USER)

async def send_alert_email(subject, body, attachment=None, filename=None):
    if attachment and filename:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
    else:
        msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = ALERT_EMAIL_FROM
    msg['To'] = ALERT_EMAIL_TO
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(ALERT_EMAIL_FROM, [ALERT_EMAIL_TO], msg.as_string())
    except Exception as e:
        import logging
        logging.error(f'Failed to send alert email: {e}')
