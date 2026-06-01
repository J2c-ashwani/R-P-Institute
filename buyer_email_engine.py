import smtplib
import time
import random
import os
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 🛑 CONFIGURATION & SECRETS
# ==========================================
# Look for custom B2B outreach credentials first, fallback to standard GMAIL or defaults
SENDER_EMAIL = os.environ.get("B2B_EMAIL") or os.environ.get("GMAIL_EMAIL") or "fsidigital.usa@gmail.com"
APP_PASSWORD = os.environ.get("B2B_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD") or "ylfzoakplpejhptu"

CSV_FILE = "buyer_leads.csv"
SENT_LOG_FILE = "buyer_sent_emails.txt"

# Batch size per execution run (keeps triggers safe from timeouts and spam filters)
BATCH_SIZE = 10

# A/B Testing Subject Lines: Pick one dynamically
SUBJECT_OPTIONS = [
    "Exclusive Grant Leads in Canada & US (Daily Inbound)",
    "Do you need more Government Grant / SR&ED Clients?",
    "Partnering: Hot Government Grant Inbound Leads"
]

def get_b2b_html_body(company_name, dm_name, dm_role, sender_email):
    """
    Returns a clean, executive B2B HTML outreach template.
    Uses professional blue/slate styling for maximum B2B corporate appeal.
    """
    # Personalize greeting using decision maker's first name if available
    if dm_name and dm_name.lower() != "team":
        first_name = dm_name.split()[0]
        greeting = f"Hi {first_name},"
        role_mention = f"your role as {dm_role} at {company_name}"
    else:
        greeting = f"Hi Team at {company_name}," if company_name else "Hi there,"
        role_mention = f"your team's expertise at {company_name}"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>B2B Partnership - FSI Digital</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f7f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f7f6;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05);border:1px solid #e1e8ed;">
          
          <!-- TOP HEADER STRIP -->
          <tr>
            <td style="background-color:#1e293b;padding:24px 40px;text-align:left;">
              <span style="color:#38bdf8;font-size:20px;font-weight:800;letter-spacing:1px;">FSI DIGITAL</span>
            </td>
          </tr>
          
          <!-- CONTENT -->
          <tr>
            <td style="padding:40px 40px 30px;color:#334155;font-size:15px;line-height:1.7;">
              <p style="margin:0 0 16px;">{greeting}</p>
              
              <p style="margin:0 0 16px;">
                I am reaching out because of {role_mention} in assisting businesses to secure government funding and grants.
              </p>
              
              <p style="margin:0 0 20px;">
                My agency, <strong>FSI Digital</strong> (based in Canada at <a href="https://fsidigital.ca" style="color:#0284c7;text-decoration:none;font-weight:600;">fsidigital.ca</a>), generates <strong>5 highly targeted, hot inbound leads daily</strong> of Canadian and US business owners actively seeking government grants and SR&ED credits. We currently have a fresh database of <strong>~500 grant-seeking business leads</strong>.
              </p>
              
              <!-- KEY HIGHLIGHTS BOX -->
              <div style="background-color:#f8fafc;border-left:4px solid #0284c7;border-radius:4px;padding:18px 20px;margin-bottom:24px;">
                <h4 style="margin:0 0 10px;color:#1e293b;font-size:14px;text-transform:uppercase;letter-spacing:0.5px;">Why partner with us:</h4>
                <ul style="margin:0;padding-left:18px;color:#475569;font-size:14px;">
                  <li style="margin-bottom:6px;"><strong>Exclusive Leads:</strong> We do not oversell leads. Once you buy a lead, it is yours exclusively.</li>
                  <li style="margin-bottom:6px;"><strong>High-Intent Inbound:</strong> Leads are generated 100% organically through our high-traffic grant guides and SEO blogs on fsidigital.ca (highly qualified prospects who actively search and read our content before filling the inquiry form).</li>
                  <li style="margin-bottom:0;"><strong>Free Trial:</strong> We want to prove our quality. We will give you 3 fresh leads completely free.</li>
                </ul>
              </div>
              
              <p style="margin:0 0 24px;">
                Since we do not offer grant writing or consulting services ourselves, we are looking for a reliable partner firm to buy these high-intent leads on a consistent basis. 
              </p>
              
              <p style="margin:0 0 30px;">
                Would you be open to a brief 5-minute call this week to see if we can fuel your sales pipeline, or should I send you the <strong>3 free sample leads</strong> to test out first?
              </p>
              
              <!-- CTA BUTTON -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
                <tr>
                  <td align="left">
                    <a href="mailto:{sender_email}?subject=Re:%20Exclusive%20Grant%20Leads%20Partnership" style="display:inline-block;background-color:#0284c7;color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 28px;border-radius:6px;box-shadow:0 2px 4px rgba(2,132,199,0.2);">
                      📩 Get 3 Free Sample Leads
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- FOOTER -->
          <tr>
            <td style="background-color:#f1f5f9;padding:24px 40px;border-top:1px solid #e2e8f0;text-align:left;color:#64748b;font-size:12px;line-height:1.6;">
              <strong>Ashwani Kumar</strong><br>
              Founder, FSI Digital<br>
              <a href="https://fsidigital.ca" style="color:#475569;text-decoration:none;">fsidigital.ca</a> | <a href="mailto:{sender_email}" style="color:#475569;text-decoration:none;">{sender_email}</a>
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

def send_b2b_email(server, recipient_email, company_name, dm_name, dm_role, sender_email):
    """Constructs and sends a premium B2B cold email."""
    subject = random.choice(SUBJECT_OPTIONS)
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"Ashwani Kumar <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    html_body = get_b2b_html_body(company_name, dm_name, dm_role, sender_email)
    msg.attach(MIMEText(html_body, 'html'))
    
    server.send_message(msg)
    print(f"📧 [B2B] Sent B2B pitch to {recipient_email} (Target: {dm_name} at {company_name}) | Subject: {subject}")

def main():
    print("🚀 Starting the FSI Digital B2B Sales Engine...")
    
    # Validate Secrets
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("❌ Error: Missing credentials. Please set B2B_EMAIL and B2B_APP_PASSWORD.")
        return

    # 1. Load Leads
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: Could not find {CSV_FILE}. Make sure the B2B scraper output is loaded.")
        return
        
    try:
        df = pd.read_csv(CSV_FILE)
        # Handle dropna case insensitively
        email_col = None
        for col in ['Email', 'Email Address', 'email', 'EMAIL']:
            if col in df.columns:
                email_col = col
                break
                
        if not email_col:
            print("❌ Error: Could not find 'Email' column in B2B leads file.")
            return

        df = df.dropna(subset=[email_col])
        df = df.drop_duplicates(subset=[email_col])
        leads = df.to_dict('records')
        print(f"📂 Loaded {len(leads)} unique B2B buyer leads from {CSV_FILE}.")
    except Exception as e:
        print(f"❌ Error reading B2B leads CSV: {e}")
        return
        
    # 2. Load Sent Log
    if os.path.exists(SENT_LOG_FILE):
        with open(SENT_LOG_FILE, "r") as f:
            sent_emails = set(line.strip().lower() for line in f if line.strip())
    else:
        sent_emails = set()
        
    print(f"📂 Loaded {len(sent_emails)} already contacted B2B buyers.")

    # Filter for fresh leads
    fresh_leads = []
    for lead in leads:
        email = str(lead[email_col]).strip().lower()
        if '@' not in email or 'nan' in email:
            continue
        if email in sent_emails:
            continue
        fresh_leads.append(lead)

    print(f"🎯 Found {len(fresh_leads)} B2B buyers waiting for outreach.")

    if not fresh_leads:
        print("🎉 No new B2B leads to contact. Exiting cleanly.")
        return

    # Determine SMTP Host based on custom domain vs gmail
    smtp_host = "smtppro.zoho.in" if "fsidigital.ca" in SENDER_EMAIL.lower() else "smtp.gmail.com"

    # 3. Connect and Send loop
    try:
        print(f"⚡ Connecting to {smtp_host} as {SENDER_EMAIL}...")
        server = smtplib.SMTP(smtp_host, 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        count = 0
        for lead in fresh_leads:
            email = str(lead[email_col]).strip().lower()
            company = lead.get('Company', 'there')
            if not company or str(company).lower() == 'nan':
                company = "there"
                
            dm_name = lead.get('DecisionMakerName', 'Team')
            if not dm_name or str(dm_name).lower() == 'nan':
                dm_name = "Team"
                
            dm_role = lead.get('DecisionMakerRole', 'Grant Consulting Partner')
            if not dm_role or str(dm_role).lower() == 'nan':
                dm_role = "Grant Consulting Partner"

            if count >= BATCH_SIZE:
                print(f"🛑 Batch size limit of {BATCH_SIZE} reached for this execution cycle.")
                break
                
            try:
                send_b2b_email(server, email, company, dm_name, dm_role, SENDER_EMAIL)
                count += 1
                
                # Append immediately to local logs to protect against sudden failures
                with open(SENT_LOG_FILE, "a") as f:
                    f.write(email + "\n")
                    
                # 15-second spam-protection delay between sends
                if count < BATCH_SIZE:
                    time.sleep(15)
            except Exception as e:
                print(f"⚠️ Failed to send B2B email to {email}. Error: {e}")
                
        server.quit()
        print(f"\n🎉 SUCCESS: Automated B2B batch completed! Sent {count} emails.")
        
    except Exception as e:
        print(f"❌ SMTP connection failure: {e}")

if __name__ == "__main__":
    main()
