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

# Use the partnership@ Gmail credentials for B2B sending
SENDER_EMAIL = "partnership@fsidigital.ca"
APP_PASSWORD = "Krr7R25Yg31D"

# Import the new premium B2B plain-text template
from buyer_email_engine import get_b2b_plain_text

# Test with realistic sample data
recipient = "sukashwanikumar@gmail.com"
test_company = "Grant Solutions Inc."
test_dm_name = "Sarah Mitchell"
test_dm_role = "Managing Director"

msg = MIMEMultipart('alternative')
msg['From'] = f"Ashwani Kumar <{SENDER_EMAIL}>"
msg['To'] = recipient
msg['Subject'] = "3 free grant leads for your team"

text_body = get_b2b_plain_text(test_company, test_dm_name, test_dm_role, SENDER_EMAIL)
msg.attach(MIMEText(text_body, 'plain'))

print("⚡ Connecting to Zoho SMTP to send B2B preview email...")
try:
    server = smtplib.SMTP('smtppro.zoho.in', 587)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"✅ SUCCESS: B2B preview email sent to {recipient}!")
    print(f"   Company: {test_company}")
    print(f"   DM Name: {test_dm_name}")
    print(f"   Subject: 3 free grant leads for your team")
except Exception as e:
    print(f"❌ ERROR: Failed to send B2B test email: {e}")
