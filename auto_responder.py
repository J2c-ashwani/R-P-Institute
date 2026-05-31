import os
import smtplib
import time
import pandas as pd
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 🛑 CONFIGURATION & SECRETS
# ==========================================
# GitHub Actions feeds these securely from your repository secrets
SENDER_EMAIL = os.environ.get("GMAIL_EMAIL")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Your Premium Consultation Landing Page Link (handles CAD/USD via PayPal Personal)
CONSULTATION_LINK = "https://www.fsidigital.ca/consultation"

# Replace this placeholder with your actual published Google Sheet CSV URL
# (To get this: Google Sheets -> File -> Share -> Publish to Web -> Web Page dropdown -> select CSV -> Copy link)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWQ6ih5-XHfhi84kmvgLDFJExwthL-HomBW5agTAcUtEU7RgpZI2_j6_yIP2a1_sCtsaRws-U7R6hm/pub?output=csv"

SENT_LOG_FILE = "auto_responder_sent.txt"

def get_premium_pitch_html(first_name):
    """Returns the high-converting $199 premium funding strategy session HTML template."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>B2B Funding Eligibility Confirmation</title>
</head>
<body style="margin:0;padding:0;background-color:#070716;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#070716;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="background-color:#0d0e2c;border-radius:12px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.3);border:1px solid #1f2256;">
          
          <!-- TOP HEADER BANNER -->
          <tr>
            <td style="background:linear-gradient(135deg,#1e293b,#111827);padding:24px 40px;text-align:left;border-bottom:1px solid #1e2040;">
              <span style="color:#38bdf8;font-size:20px;font-weight:800;letter-spacing:1px;">FSI DIGITAL</span>
            </td>
          </tr>
          
          <!-- MAIN CONTENT -->
          <tr>
            <td style="padding:40px 40px 30px;color:#c8cfe8;font-size:15px;line-height:1.7;">
              <p style="margin:0 0 16px;font-size:16px;">Hi {first_name},</p>
              
              <p style="margin:0 0 16px;">
                I am reaching out regarding the government grant and corporate financing inquiry you submitted on our platform, <strong>FSI Digital</strong>.
              </p>
              
              <p style="margin:0 0 16px;">
                Our preliminary database analysis indicates that your business operates in a highly eligible sector. However, because government grant frameworks and corporate tax codes are complex, standard automated applications result in a 90% rejection rate.
              </p>
              
              <p style="margin:0 0 20px;">
                To assist you directly, I am opening up a limited number of premium, **1-on-1 Government Grant & Funding Strategy Consultations** next week.
              </p>
              
              <!-- THE DEEP RESEARCH VALUE PROPOSITION -->
              <div style="background-color:#14163c;border-left:4px solid #38bdf8;border-radius:4px;padding:18px 20px;margin-bottom:24px;border-top:1px solid #282b68;border-right:1px solid #282b68;border-bottom:1px solid #282b68;">
                <h4 style="margin:0 0 10px;color:#ffffff;font-size:14px;text-transform:uppercase;letter-spacing:0.5px;">Why this is a premium, custom assessment:</h4>
                <p style="margin:0;font-size:14px;color:#a0aec0;line-height:1.6;">
                  This is a bespoke advisory service. Before we get on our 30-minute private Google Meet, our team spends **2 hours of custom research** specifically analyzing your business domain, local tax codes, and matching them against our proprietary database of active private and government programs.
                </p>
              </div>
              
              <!-- THE 3 DELIVERABLES -->
              <p style="margin:0 0 12px;font-weight:700;color:#ffffff;">During our call, you will receive:</p>
              <ul style="margin:0 0 24px;padding-left:20px;color:#c8cfe8;">
                <li style="margin-bottom:8px;">A fully customized, pre-researched **Government Grant & Funding Roadmap** for your business.</li>
                <li style="margin-bottom:8px;">The exact top 3 grant or loan programs you qualify for with the highest probability of approval.</li>
                <li style="margin-bottom:0;">A step-by-step documentation and filing plan to avoid costly compliance rejections.</li>
              </ul>
              
              <p style="margin:0 0 24px;">
                Our fee for this deeply researched, custom strategy package is <strong style="color:#ffffff;">$199 USD</strong> (backed by our upfront research commitment).
              </p>
              
              <!-- CTA BUTTON -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:30px;">
                <tr>
                  <td align="center">
                    <a href="{CONSULTATION_LINK}" style="display:inline-block;background:linear-gradient(135deg,#38bdf8,#0284c7);color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 40px;border-radius:8px;box-shadow:0 4px 12px rgba(56,189,248,0.2);">
                      👉 Secure Your Consultation Slot
                    </a>
                    <div style="color:#5a6a9a;font-size:12px;margin-top:10px;">Secure Checkout via PayPal or Card &nbsp;|&nbsp; Only 12 Slots Available next week</div>
                  </td>
                </tr>
              </table>
              
              <!-- 1-CLICK EDTECH PLATFORMS PLUG -->
              <p style="margin:0 0 16px;font-size:14px;color:#8f9ac2;">
                In the meantime, feel free to test the core AI models built by our engineering division that power our custom data analysis models:
              </p>
              
              <div style="background-color:#14163c;border-radius:8px;padding:12px 15px;margin-bottom:24px;border:1px solid #282b68;text-align:center;">
                <a href="https://twinmind-9l6x.onrender.com" style="display:inline-block;background-color:#764ba2;color:#ffffff;font-size:12px;font-weight:700;text-decoration:none;padding:6px 12px;border-radius:4px;margin:3px;">💻 TwinGenie AI</a>
              </div>
              
              <p style="margin:0;font-size:14px;color:#8f9ac2;font-style:italic;">
                *Please note: Because each session requires 2 hours of pre-call research from our team, these slots are strictly allocated on a first-come, first-served basis.*
              </p>
            </td>
          </tr>
          
          <!-- FOOTER -->
          <tr>
            <td style="background:#050510;padding:20px 40px;border-top:1px solid #1a1c44;text-align:left;color:#4f5c87;font-size:12px;line-height:1.6;">
              <strong>Ashwani</strong><br>
              Lead Funding Strategist, FSI Digital<br>
              <a href="https://fsidigital.ca" style="color:#38bdf8;text-decoration:none;">fsidigital.ca</a> | ashwani@fsidigital.ca
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""
    return html

def send_pitch_email(server, recipient_email, first_name):
    """Sends the premium B2B consultation email."""
    msg = MIMEMultipart('alternative')
    msg['From'] = f"Ashwani <{SENDER_EMAIL}>"
    msg['To'] = recipient_email
    msg['Subject'] = "Eligibility Confirmed: Custom Business Grant & Funding Strategy Session"
    
    html_body = get_premium_pitch_html(first_name)
    msg.attach(MIMEText(html_body, 'html'))
    
    server.send_message(msg)
    print(f"📧 [AUTO-RESPONDER] Sent premium pitch to {recipient_email} (Name: {first_name})")

def main():
    print("🚀 Running Cloud B2B Auto-Responder Daemon...")
    
    # 1. Validate Secrets
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("❌ Error: Missing GMAIL_EMAIL or GMAIL_APP_PASSWORD environment variables.")
        return
        
    if "[YOUR_SPREADSHEET_ID_HERE]" in SHEET_CSV_URL:
        print("❌ Error: You must replace SPREADSHEET_ID in SHEET_CSV_URL before running.")
        return

    # 2. Load the sent emails log
    if os.path.exists(SENT_LOG_FILE):
        with open(SENT_LOG_FILE, "r") as f:
            sent_emails = set(line.strip() for line in f if line.strip())
    else:
        sent_emails = set()
        
    print(f"📂 Loaded {len(sent_emails)} already emailed leads from local log.")

    # 3. Read Google Sheet CSV directly
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df.columns = [c.strip() for c in df.columns]  # Clean whitespace from column headers
        print(f"✅ Successfully fetched Google Sheet. Found {len(df)} total rows.")
    except Exception as e:
        print(f"❌ Error fetching Google Sheet CSV from web: {e}")
        return

    # Validate essential columns
    email_col = None
    for col in ['Email', 'Email Address', 'email', 'EMAIL']:
        if col in df.columns:
            email_col = col
            break
            
    if not email_col:
        print("❌ Error: Could not find 'Email' column in Google Sheet. Available columns:", list(df.columns))
        return

    # Extract name column if it exists
    name_col = None
    for col in ['Name', 'Name/Company', 'Name ', 'First Name', 'FirstName', 'FullName', 'Full Name', 'name']:
        if col in df.columns:
            name_col = col
            break

    # Find timestamp column if it exists
    timestamp_col = None
    for col in ['Timestamp', 'timestamp', 'Created', 'Created At', 'Date', 'date', 'Submission Date', 'Submitted At']:
        if col in df.columns:
            timestamp_col = col
            break

    # 4. Filter for fresh, unsent leads
    fresh_leads = []
    
    # Define our target start date (March 1, 2026) and cutoff (2 hours ago)
    start_date = pd.to_datetime("2026-03-01 00:00:00")
    now = pd.Timestamp.now()
    cutoff_time = now - pd.Timedelta(hours=2)
    
    print(f"⏰ Filters Active:")
    print(f"   - Only leads created on or after: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Only leads created before: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} (at least 2 hours ago)")
    print(f"   - Strict exclusion of all newsletter leads.")
    
    for _, row in df.iterrows():
        email = str(row[email_col]).strip().lower()
        if not email or '@' not in email or 'nan' in email:
            continue
            
        # Robust Newsletter Filtering - scan all columns for newsletter/subscriber indicators
        is_newsletter_subscriber = False
        for col in df.columns:
            col_lower = col.lower()
            val_str = str(row[col]).strip().lower()
            if any(term in col_lower for term in ['newsletter', 'subscribe', 'subscriber', 'role', 'type', 'source', 'form']):
                if any(term in val_str for term in ['newsletter', 'subscriber', 'yes', 'true', 'sub']):
                    is_newsletter_subscriber = True
                    break
        
        if is_newsletter_subscriber:
            continue
            
        # Check if already sent
        if email in sent_emails:
            continue
            
        # Date & 2-Hour Time Delay Filtering
        if timestamp_col:
            lead_time = pd.to_datetime(row[timestamp_col], errors='coerce')
            if pd.notnull(lead_time):
                # Remove timezone info for comparison if it exists
                if lead_time.tzinfo is not None:
                    lead_time = lead_time.tz_localize(None)
                
                # Verify lead is within March 1, 2026 and at least 2 hours old
                if lead_time < start_date:
                    continue
                if lead_time > cutoff_time:
                    continue
            else:
                # If there's a timestamp column but it's blank/unparseable, skip to be safe.
                continue

        name = str(row[name_col]).strip() if name_col else "there"
        if not name or name.lower() == 'nan':
            name = "there"
            
        first_name = name.split()[0].capitalize()
        fresh_leads.append({"email": email, "first_name": first_name})

    print(f"🎯 Found {len(fresh_leads)} new fresh leads needing auto-response.")
    
    if not fresh_leads:
        print("🎉 No new leads to email. Exiting safely.")
        return

    # 5. Connect and Send Loop
    try:
        server = smtplib.SMTP('smtp.zoho.in', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        count = 0
        for lead in fresh_leads:
            try:
                send_pitch_email(server, lead["email"], lead["first_name"])
                count += 1
                
                # Append immediately to the local log file
                with open(SENT_LOG_FILE, "a") as f:
                    f.write(lead["email"] + "\n")
                    
                # Short 5-second sleep to prevent rapid-fire SMTP warnings
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ Failed to send to {lead['email']}. Error: {e}")
                
        server.quit()
        print(f"\n🎉 SUCCESS: Automated response completed! Emailed {count} new leads.")
        
    except Exception as e:
        print(f"❌ SMTP connection failure: {e}")

if __name__ == "__main__":
    main()
