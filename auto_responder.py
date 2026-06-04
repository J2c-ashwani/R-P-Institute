import os
import smtplib
import time
import random
import pandas as pd
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 🛑 CONFIGURATION & SECRETS
# ==========================================
# SENDER ACCOUNTS (Supports Inbox Rotation to distribute B2C load)
ACCOUNTS = []
if os.environ.get("GMAIL_EMAIL") and os.environ.get("GMAIL_APP_PASSWORD"):
    ACCOUNTS.append({
        "email": os.environ.get("GMAIL_EMAIL"),
        "password": os.environ.get("GMAIL_APP_PASSWORD"),
        "display_name": "Ashwani"
    })
if os.environ.get("ADVISORS_EMAIL") and os.environ.get("ADVISORS_APP_PASSWORD"):
    ACCOUNTS.append({
        "email": os.environ.get("ADVISORS_EMAIL"),
        "password": os.environ.get("ADVISORS_APP_PASSWORD"),
        "display_name": "Advisors"
    })

# Fallback for individual tests/scenarios
SENDER_EMAIL = ACCOUNTS[0]["email"] if ACCOUNTS else os.environ.get("GMAIL_EMAIL")
APP_PASSWORD = ACCOUNTS[0]["password"] if ACCOUNTS else os.environ.get("GMAIL_APP_PASSWORD")

# Your Premium Consultation Landing Page Link (handles CAD/USD via PayPal Personal)
CONSULTATION_LINK = "https://www.fsidigital.ca/consultation"

# Replace this placeholder with your actual published Google Sheet CSV URL
# (To get this: Google Sheets -> File -> Share -> Publish to Web -> Web Page dropdown -> select CSV -> Copy link)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWQ6ih5-XHfhi84kmvgLDFJExwthL-HomBW5agTAcUtEU7RgpZI2_j6_yIP2a1_sCtsaRws-U7R6hm/pub?output=csv"

SENT_LOG_FILE = "auto_responder_sent.txt"
BATCH_SIZE = 3
DAILY_CAP = 30  # Safety limit for Zoho SMTP (emails/day per account)


# FIX #1: A/B Subject Lines — short, human, curiosity-driven (avoids spam triggers)
B2C_SUBJECT_OPTIONS = [
    "Your grant eligibility results are ready",
    "{first_name}, quick update on your funding inquiry",
    "We found 3 programs your business qualifies for",
    "Following up on your grant inquiry",
]

def get_premium_pitch_html(first_name):
    """Returns the high-converting $199 premium funding strategy session HTML template.
    Redesigned with all 7 conversion fixes: social proof, price anchoring, 
    3-step process, outcome-focused CTA, no distractions."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Funding Eligibility Results</title>
</head>
<body style="margin:0;padding:0;background-color:#070716;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#070716;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="background-color:#0d0e2c;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.4);border:1px solid #1f2256;">
          
          <!-- PREMIUM HEADER -->
          <tr>
            <td style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:24px 40px;text-align:left;border-bottom:1px solid #2d3a55;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="color:#38bdf8;font-size:22px;font-weight:800;letter-spacing:1.5px;">FSI DIGITAL</span>
                    <span style="color:#475569;font-size:11px;display:block;margin-top:2px;letter-spacing:0.5px;">FUNDING STRATEGY DIVISION</span>
                  </td>
                  <td align="right">
                    <span style="display:inline-block;background-color:#059669;color:#ffffff;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px;">ELIGIBLE</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FIX #2: SOCIAL PROOF STATS BAR -->
          <tr>
            <td style="padding:24px 40px 0;">
              <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:10px;overflow:hidden;border:1px solid #1e3a5f;">
                <tr>
                  <td width="33%" style="background-color:#0f1d36;padding:14px 12px;text-align:center;border-right:1px solid #1e3a5f;">
                    <div style="color:#38bdf8;font-size:22px;font-weight:800;line-height:1;">350+</div>
                    <div style="color:#64748b;font-size:9px;font-weight:600;margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;">Businesses Helped</div>
                  </td>
                  <td width="33%" style="background-color:#0f1d36;padding:14px 12px;text-align:center;border-right:1px solid #1e3a5f;">
                    <div style="color:#10b981;font-size:22px;font-weight:800;line-height:1;">$2.8M+</div>
                    <div style="color:#64748b;font-size:9px;font-weight:600;margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;">Funding Identified</div>
                  </td>
                  <td width="33%" style="background-color:#0f1d36;padding:14px 12px;text-align:center;">
                    <div style="color:#f59e0b;font-size:22px;font-weight:800;line-height:1;">94%</div>
                    <div style="color:#64748b;font-size:9px;font-weight:600;margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;">Satisfaction Rate</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- MAIN CONTENT -->
          <tr>
            <td style="padding:28px 40px 20px;color:#c8cfe8;font-size:15px;line-height:1.75;">
              <p style="margin:0 0 16px;font-size:16px;color:#e2e8f0;">Hi {first_name},</p>
              
              <p style="margin:0 0 16px;">
                Thank you for submitting your funding inquiry on <a href="https://fsidigital.ca" style="color:#38bdf8;text-decoration:none;font-weight:600;">FSI Digital</a>. I personally reviewed your submission.
              </p>
              
              <p style="margin:0 0 16px;">
                Our initial screening shows your business falls into a <strong style="color:#10b981;">high-eligibility category</strong>. However, because government grant programs and SR&amp;ED tax credits have complex qualification rules, 90% of businesses that apply without expert guidance get rejected on technicalities alone.
              </p>
              
              <p style="margin:0 0 24px;">
                To help you avoid that, I am offering a limited number of <strong style="color:#e2e8f0;">1-on-1 Custom Funding Strategy Sessions</strong> this week.
              </p>
            </td>
          </tr>

          <!-- WHAT YOU GET — 3 DELIVERABLES -->
          <tr>
            <td style="padding:0 40px 24px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0d1b2a;border-radius:12px;border:1px solid #1e3a5f;overflow:hidden;">
                <tr>
                  <td style="padding:18px 20px 8px;">
                    <span style="color:#e2e8f0;font-size:14px;font-weight:700;">What you will receive:</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:4px 20px 18px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#38bdf8,#0284c7);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">1</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">A <strong style="color:#e2e8f0;">Custom Funding Roadmap</strong> — 2 hours of pre-research on your industry, region, and tax profile before our call.</td>
                          </tr></table>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#10b981,#059669);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">2</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">Your <strong style="color:#e2e8f0;">Top 3 Grant Programs</strong> ranked by approval probability, with exact deadlines and funding amounts.</td>
                          </tr></table>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">3</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">A <strong style="color:#e2e8f0;">Step-by-Step Filing Plan</strong> to avoid the documentation errors that cause 90% of rejections.</td>
                          </tr></table>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FIX #6: PRICE ANCHORING CARD -->
          <tr>
            <td style="padding:0 40px 24px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;border:1px solid #1e3a5f;">
                <tr>
                  <td style="background:linear-gradient(135deg,#0c1f3d,#162d50);padding:18px 24px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td>
                          <div style="color:#64748b;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Your Investment</div>
                          <div style="color:#ffffff;font-size:28px;font-weight:800;line-height:1;">$199 <span style="color:#64748b;font-size:14px;font-weight:400;">USD</span></div>
                          <div style="color:#94a3b8;font-size:12px;margin-top:4px;">Includes 2 hrs research + 30-min private strategy call</div>
                        </td>
                        <td align="right" style="vertical-align:top;">
                          <div style="text-decoration:line-through;color:#ef4444;font-size:14px;font-weight:600;opacity:0.7;">$500+</div>
                          <div style="color:#64748b;font-size:10px;">Typical industry rate</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FIX #5: CTA BUTTON — OUTCOME-FOCUSED -->
          <tr>
            <td style="padding:0 40px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="{{CONSULTATION_LINK}}" style="display:inline-block;background:linear-gradient(135deg,#38bdf8,#0284c7);color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;padding:16px 48px;border-radius:10px;box-shadow:0 6px 20px rgba(56,189,248,0.25);letter-spacing:0.3px;">
                      Get My Custom Funding Roadmap &rarr;
                    </a>
                    <div style="color:#5a6a9a;font-size:11px;margin-top:10px;">Secure Checkout via PayPal or Card &nbsp;&bull;&nbsp; Only 8 spots remaining this week</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FIX #4: WHAT HAPPENS AFTER YOU PAY — 3-STEP PROCESS -->
          <tr>
            <td style="padding:0 40px 28px;">
              <table width="100%" cellpadding="0" cellspacing="8">
                <tr>
                  <td width="33%" style="background-color:#0d1b2a;border-radius:8px;padding:14px 12px;border:1px solid #1e3a5f;text-align:center;">
                    <div style="color:#38bdf8;font-size:18px;font-weight:800;margin-bottom:4px;">Step 1</div>
                    <div style="color:#94a3b8;font-size:11px;line-height:1.4;">You pay $199 &amp; share your business details</div>
                  </td>
                  <td width="33%" style="background-color:#0d1b2a;border-radius:8px;padding:14px 12px;border:1px solid #1e3a5f;text-align:center;">
                    <div style="color:#10b981;font-size:18px;font-weight:800;margin-bottom:4px;">Step 2</div>
                    <div style="color:#94a3b8;font-size:11px;line-height:1.4;">We spend 2 hours researching your eligibility</div>
                  </td>
                  <td width="33%" style="background-color:#0d1b2a;border-radius:8px;padding:14px 12px;border:1px solid #1e3a5f;text-align:center;">
                    <div style="color:#f59e0b;font-size:18px;font-weight:800;margin-bottom:4px;">Step 3</div>
                    <div style="color:#94a3b8;font-size:11px;line-height:1.4;">Private 30-min call with your full roadmap</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- URGENCY CLOSE -->
          <tr>
            <td style="padding:0 40px 28px;">
              <p style="margin:0;font-size:13px;color:#8f9ac2;line-height:1.6;font-style:italic;">
                Because each session requires 2 hours of dedicated pre-call research from our advisory team, spots are strictly limited and filled on a first-come, first-served basis.
              </p>
            </td>
          </tr>
          
          <!-- PREMIUM FOOTER -->
          <tr>
            <td style="background:linear-gradient(135deg,#060d1b,#0a1628);padding:24px 40px;border-top:1px solid #1e293b;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="color:#64748b;font-size:12px;line-height:1.6;">
                    <strong style="color:#94a3b8;">Ashwani Kumar</strong><br>
                    Lead Funding Strategist, FSI Digital<br>
                    <a href="https://fsidigital.ca" style="color:#38bdf8;text-decoration:none;">fsidigital.ca</a> &nbsp;|&nbsp; ashwani@fsidigital.ca
                  </td>
                  <td align="right" style="vertical-align:top;">
                    <span style="display:inline-block;background-color:#1e293b;color:#64748b;font-size:9px;font-weight:600;padding:4px 10px;border-radius:4px;letter-spacing:0.5px;">CANADA &amp; USA</span>
                  </td>
                </tr>
              </table>
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

def check_daily_sending_limit(log_file, sender_email):
    """
    Checks how many emails were sent by a specific sender_email in the last 24 hours.
    Returns the count of sent emails.
    """
    if not os.path.exists(log_file):
        return 0
        
    count = 0
    now = pd.Timestamp.now(tz='UTC')
    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    logged_sender = parts[2].strip().lower()
                    if logged_sender == sender_email.lower():
                        timestamp = pd.to_datetime(parts[1].strip())
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.tz_localize('UTC')
                        else:
                            timestamp = timestamp.tz_convert('UTC')
                        if (now - timestamp).total_seconds() < 86400:
                            count += 1
                except Exception:
                    pass
    return count

def send_pitch_email(server, recipient_email, first_name, sender_email, sender_display_name):
    """Sends the premium consultation pitch email with A/B subject line testing."""
    # FIX #1: Rotate subject lines dynamically with personalization
    subject = random.choice(B2C_SUBJECT_OPTIONS).replace("{first_name}", first_name or "there")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_display_name} <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    html_body = get_premium_pitch_html(first_name).replace("{CONSULTATION_LINK}", CONSULTATION_LINK)
    msg.attach(MIMEText(html_body, 'html'))
    
    server.send_message(msg)
    print(f"📧 [AUTO-RESPONDER] Sent premium pitch to {recipient_email} (Name: {first_name}) | Subject: {subject} | From: {sender_display_name} <{sender_email}>")

def main():
    print("🚀 Running Cloud B2B Auto-Responder Daemon...")
    
    # Check if current time is within US/Eastern Business Hours (Mon-Fri, 9am - 6pm EST)
    try:
        now_est = pd.Timestamp.now(tz='America/New_York')
        day_of_week = now_est.dayofweek  # 0 is Monday, 6 is Sunday
        hour = now_est.hour
        
        is_business_day = 0 <= day_of_week <= 4
        is_business_hour = 9 <= hour <= 17
        
        if not (is_business_day and is_business_hour):
            print(f"😴 Outside Business Hours in Target Market (US/Eastern):")
            print(f"   - Current EST Time: {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"   - Allowed: Monday to Friday, 9:00 AM - 6:00 PM EST.")
            print(f"   - Leads will remain safely queued in your Google Sheet. Exiting cleanly.")
            return
    except Exception as e:
        print(f"⚠️ Warning: Timezone check skipped due to error: {e}. Running anyway.")
    
    # 1. Validate Secrets
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("❌ Error: Missing GMAIL_EMAIL or GMAIL_APP_PASSWORD environment variables.")
        return
        
    if "[YOUR_SPREADSHEET_ID_HERE]" in SHEET_CSV_URL:
        print("❌ Error: You must replace SPREADSHEET_ID in SHEET_CSV_URL before running.")
        return

    # 2. Load the sent emails log (handles backward compatibility with plain emails)
    sent_emails = set()
    if os.path.exists(SENT_LOG_FILE):
        with open(SENT_LOG_FILE, "r") as f:
            for line in f:
                line = line.strip().lower()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                email = parts[0].strip()
                sent_emails.add(email)
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
    fresh_new_leads = []  # >= May 1, 2026
    fresh_old_leads = []  # < May 1, 2026
    
    # Define our target cutoff time (2 hours ago)
    now = pd.Timestamp.now()
    cutoff_time = now - pd.Timedelta(hours=2)
    cutoff_date = pd.to_datetime("2026-05-01")
    
    print(f"⏰ Filters Active:")
    print(f"   - Split processing: New leads (>= May 1, 2026) send from advisors@, Historical leads (< May 1, 2026) send from ashwani@.")
    print(f"   - For fresh leads, only those created before: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} (at least 2 hours ago)")
    print(f"   - Strict exclusion of all newsletter leads.")
    seen_emails_this_run = set()
    for _, row in df.iterrows():
        email = str(row[email_col]).strip().lower()
        if not email or '@' not in email or 'nan' in email:
            continue
            
        # Exclude fake/test domains to protect sender reputation and prevent bounces
        if any(domain in email for domain in ['mailinator.com', 'test.com', 'example.com', 'tempmail.com']):
            continue
            
        # Avoid duplicate processing of the same email in the same execution run
        if email in seen_emails_this_run:
            continue
        seen_emails_this_run.add(email)
            
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
        lead_is_new = False
        if timestamp_col:
            lead_time = pd.to_datetime(row[timestamp_col], errors='coerce')
            if pd.notnull(lead_time):
                # Remove timezone info for comparison if it exists
                if lead_time.tzinfo is not None:
                    lead_time = lead_time.tz_localize(None)
                
                # Verify lead is at least 2 hours old
                if lead_time > cutoff_time:
                    continue
                    
                if lead_time >= cutoff_date:
                    lead_is_new = True
            else:
                # If there's a timestamp column but it's blank/unparseable, skip to be safe.
                continue

        name = str(row[name_col]).strip() if name_col else "there"
        if not name or name.lower() == 'nan':
            name = "there"
            
        first_name = name.split()[0].capitalize()
        lead_info = {"email": email, "first_name": first_name}
        
        if lead_is_new:
            fresh_new_leads.append(lead_info)
        else:
            fresh_old_leads.append(lead_info)

    print(f"🎯 Lead Segmentation Results:")
    print(f"   - NEW Leads (>= May 1, 2026): {len(fresh_new_leads)} pending.")
    print(f"   - HISTORICAL Leads (< May 1, 2026): {len(fresh_old_leads)} pending.")
    
    if not fresh_new_leads and not fresh_old_leads:
        print("🎉 No new or historical leads to email. Exiting safely.")
        return

    # 5. Connect and Send Loop for NEW Leads (using Advisors account to keep fresh leads instant!)
    new_count = 0
    advisors_email = os.environ.get("ADVISORS_EMAIL")
    advisors_password = os.environ.get("ADVISORS_APP_PASSWORD")
    
    if fresh_new_leads and advisors_email and advisors_password:
        sent_today = check_daily_sending_limit(SENT_LOG_FILE, advisors_email)
        print(f"📊 Daily sending audit: Advisors ({advisors_email}) has sent {sent_today}/{DAILY_CAP} emails in the last 24 hours.")
        if sent_today >= DAILY_CAP:
            print(f"🛑 Safe cap reached: Advisors ({advisors_email}) reached daily limit of {DAILY_CAP} emails. Skipping new leads batch.")
        else:
            allowed_to_send = min(BATCH_SIZE, DAILY_CAP - sent_today)
            print(f"\n🔥 Processing up to {allowed_to_send} NEW leads using advisors@fsidigital.ca (within daily cap of {DAILY_CAP})...")
            for lead in fresh_new_leads:
                if new_count >= allowed_to_send:
                    print(f"🛑 New lead batch size limit of {allowed_to_send} reached.")
                    break
                    
                # Determine SMTP Host based on custom domain vs gmail
                smtp_host = "smtppro.zoho.in" if "fsidigital.ca" in advisors_email.lower() else "smtp.gmail.com"
                print(f"⚡ Connecting to {smtp_host} as Advisors ({advisors_email}) to send response to NEW lead {lead['email']}...")
                try:
                    server = smtplib.SMTP(smtp_host, 587, timeout=15)
                    server.starttls()
                    server.login(advisors_email, advisors_password)
                    
                    send_pitch_email(server, lead["email"], lead["first_name"], advisors_email, "Advisors")
                    server.quit()
                    
                    new_count += 1
                    
                    # Append immediately to the local log file in format: email,timestamp,sender
                    timestamp_str = pd.Timestamp.now(tz='UTC').isoformat()
                    with open(SENT_LOG_FILE, "a") as f:
                        f.write(f"{lead['email']},{timestamp_str},{advisors_email}\n")
                        
                    # 15-second delay between emails to mimic human behavior and protect domain reputation
                    if new_count < allowed_to_send:
                        time.sleep(15)
                except smtplib.SMTPAuthenticationError as e:
                    print(f"❌ Critical Authentication Failure for NEW leads sender {advisors_email}: {e}. Aborting batch.")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to send to NEW lead {lead['email']}. Error: {e}")
                    time.sleep(5)
    else:
        if not fresh_new_leads:
            print("ℹ️ No new leads (>= May 1, 2026) to process.")
        else:
            print("⚠️ Skipping NEW leads because ADVISORS_EMAIL or ADVISORS_APP_PASSWORD secrets are not configured on GitHub yet.")
 
    # 6. Connect and Send Loop for HISTORICAL Leads (using Ashwani account to steadily clear the backlog!)
    old_count = 0
    ashwani_email = os.environ.get("GMAIL_EMAIL")
    ashwani_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if fresh_old_leads and ashwani_email and ashwani_password:
        sent_today = check_daily_sending_limit(SENT_LOG_FILE, ashwani_email)
        print(f"📊 Daily sending audit: Ashwani ({ashwani_email}) has sent {sent_today}/{DAILY_CAP} emails in the last 24 hours.")
        if sent_today >= DAILY_CAP:
            print(f"🛑 Safe cap reached: Ashwani ({ashwani_email}) reached daily limit of {DAILY_CAP} emails. Skipping historical leads batch.")
        else:
            allowed_to_send = min(BATCH_SIZE, DAILY_CAP - sent_today)
            print(f"\n🕰️ Processing up to {allowed_to_send} HISTORICAL leads using ashwani@fsidigital.ca (within daily cap of {DAILY_CAP})...")
            for lead in fresh_old_leads:
                if old_count >= allowed_to_send:
                    print(f"🛑 Historical lead batch size limit of {allowed_to_send} reached.")
                    break
                    
                # Determine SMTP Host based on custom domain vs gmail
                smtp_host = "smtppro.zoho.in" if "fsidigital.ca" in ashwani_email.lower() else "smtp.gmail.com"
                print(f"⚡ Connecting to {smtp_host} as Ashwani ({ashwani_email}) to send response to HISTORICAL lead {lead['email']}...")
                try:
                    server = smtplib.SMTP(smtp_host, 587, timeout=15)
                    server.starttls()
                    server.login(ashwani_email, ashwani_password)
                    
                    send_pitch_email(server, lead["email"], lead["first_name"], ashwani_email, "Ashwani")
                    server.quit()
                    
                    old_count += 1
                    
                    # Append immediately to the local log file in format: email,timestamp,sender
                    timestamp_str = pd.Timestamp.now(tz='UTC').isoformat()
                    with open(SENT_LOG_FILE, "a") as f:
                        f.write(f"{lead['email']},{timestamp_str},{ashwani_email}\n")
                        
                    # 15-second delay between emails to mimic human behavior and protect domain reputation
                    if old_count < allowed_to_send:
                        time.sleep(15)
                except smtplib.SMTPAuthenticationError as e:
                    print(f"❌ Critical Authentication Failure for HISTORICAL leads sender {ashwani_email}: {e}. Aborting batch.")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to send to HISTORICAL lead {lead['email']}. Error: {e}")
                    time.sleep(5)
    else:
        if not fresh_old_leads:
            print("ℹ️ No historical leads (< May 1, 2026) to process.")
        else:
            print("⚠️ Skipping HISTORICAL leads because GMAIL_EMAIL or GMAIL_APP_PASSWORD secrets are not configured on GitHub.")
            
    print(f"\n🎉 SUCCESS: Automated response run completed! Emailed {new_count} new leads and {old_count} historical leads.")

if __name__ == "__main__":
    main()
