import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables manually from local .env file
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

SENDER_EMAIL = os.environ.get("GMAIL_EMAIL")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Import the HTML template and variables from the main auto_responder script
from auto_responder import get_premium_pitch_html, CONSULTATION_LINK

recipient = "sukashwanikumar@gmail.com"

msg = MIMEMultipart('alternative')
msg['From'] = f"Ashwani <{SENDER_EMAIL}>"
msg['To'] = recipient
msg['Subject'] = "Your grant eligibility results are ready"

# Replace placeholder with Consultation link
html_body = get_premium_pitch_html("Ashwani").replace("{CONSULTATION_LINK}", CONSULTATION_LINK)
msg.attach(MIMEText(html_body, 'html'))

print("⚡ Connecting to smtppro.zoho.in to send preview email...")
try:
    server = smtplib.SMTP('smtppro.zoho.in', 587)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"✅ SUCCESS: Preview email has been successfully sent to {recipient}!")
except Exception as e:
    print(f"❌ ERROR: Failed to send test email: {e}")
