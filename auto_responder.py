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
# GitHub Actions feeds these securely from your repository secrets
SENDER_EMAIL = os.environ.get("GMAIL_EMAIL")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Your Premium Consultation Landing Page Link (handles CAD/USD via PayPal Personal)
CONSULTATION_LINK = "https://www.fsidigital.ca/consultation"

# Replace this placeholder with your actual published Google Sheet CSV URL
# (To get this: Google Sheets -> File -> Share -> Publish to Web -> Web Page dropdown -> select CSV -> Copy link)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWQ6ih5-XHfhi84kmvgLDFJExwthL-HomBW5agTAcUtEU7RgpZI2_j6_yIP2a1_sCtsaRws-U7R6hm/pub?output=csv"

SENT_LOG_FILE = "auto_responder_sent.txt"
BATCH_SIZE = 10

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

def send_pitch_email(server, recipient_email, first_name):
    """Sends the premium consultation pitch email with A/B subject line testing."""
    # FIX #1: Rotate subject lines dynamically with personalization
    subject = random.choice(B2C_SUBJECT_OPTIONS).replace("{first_name}", first_name or "there")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"Ashwani <{SENDER_EMAIL}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    html_body = get_premium_pitch_html(first_name).replace("{CONSULTATION_LINK}", CONSULTATION_LINK)
    msg.attach(MIMEText(html_body, 'html'))
    
    server.send_message(msg)
    print(f"📧 [AUTO-RESPONDER] Sent premium pitch to {recipient_email} (Name: {first_name}) | Subject: {subject}")

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
    
    # Define our target cutoff time (2 hours ago)
    now = pd.Timestamp.now()
    cutoff_time = now - pd.Timedelta(hours=2)
    
    print(f"⏰ Filters Active:")
    print(f"   - Processing ALL historical leads in sheet (no start date limit).")
    print(f"   - For fresh leads, only those created before: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} (at least 2 hours ago)")
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
                
                # Verify lead is at least 2 hours old
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
        server = smtplib.SMTP('smtppro.zoho.in', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        count = 0
        for lead in fresh_leads:
            if count >= BATCH_SIZE:
                print(f"🛑 Batch size limit of {BATCH_SIZE} reached for this execution cycle. Exiting cleanly.")
                break
            try:
                send_pitch_email(server, lead["email"], lead["first_name"])
                count += 1
                
                # Append immediately to the local log file
                with open(SENT_LOG_FILE, "a") as f:
                    f.write(lead["email"] + "\n")
                    
                # 15-second delay between emails to mimic human behavior and protect domain reputation
                if count < BATCH_SIZE:
                    time.sleep(15)
            except Exception as e:
                print(f"⚠️ Failed to send to {lead['email']}. Error: {e}")
                
        server.quit()
        print(f"\n🎉 SUCCESS: Automated response completed! Emailed {count} new leads.")
        
    except Exception as e:
        print(f"❌ SMTP connection failure: {e}")

if __name__ == "__main__":
    main()
