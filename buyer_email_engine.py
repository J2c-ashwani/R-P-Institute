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
# SENDER ACCOUNTS (Supports B2B Inbox Rotation to distribute B2B outreach load)
ACCOUNTS = []
if os.environ.get("B2B_EMAIL") and os.environ.get("B2B_APP_PASSWORD"):
    ACCOUNTS.append({
        "email": os.environ.get("B2B_EMAIL"),
        "password": os.environ.get("B2B_APP_PASSWORD"),
        "display_name": "Ashwani Kumar"
    })
if os.environ.get("PARTNERS_EMAIL") and os.environ.get("PARTNERS_APP_PASSWORD"):
    ACCOUNTS.append({
        "email": os.environ.get("PARTNERS_EMAIL"),
        "password": os.environ.get("PARTNERS_APP_PASSWORD"),
        "display_name": "Partners FSI Digital"
    })

# Fallback for individual tests/scenarios
SENDER_EMAIL = ACCOUNTS[0]["email"] if ACCOUNTS else os.environ.get("B2B_EMAIL") or "fsidigital.usa@gmail.com"
APP_PASSWORD = ACCOUNTS[0]["password"] if ACCOUNTS else os.environ.get("B2B_APP_PASSWORD") or "ylfzoakplpejhptu"

CSV_FILE = "buyer_leads.csv"
SENT_LOG_FILE = "buyer_sent_emails.txt"

# Batch size per execution run (keeps triggers safe from timeouts and spam filters)
BATCH_SIZE = 3
DAILY_CAP = 20  # Safety limit for Zoho SMTP (emails/day per account)


SUBJECT_OPTIONS = [
    "Quick question about your lead pipeline",
    "3 free grant leads for your team",
    "Idea for {company_name} — inbound grant leads",
    "We generate leads you'd want to close"
]

def get_b2b_html_body(company_name, dm_name, dm_role, sender_email):
    """
    Returns a premium, visually stunning B2B HTML outreach template.
    Designed from a founder's perspective to command attention and drive replies.
    """
    # Personalize greeting using decision maker's first name if available
    if dm_name and dm_name.lower() != "team":
        first_name = dm_name.split()[0]
        greeting = f"Hi {first_name},"
        personalized_hook = f"I came across {company_name} while researching top-tier grant advisory firms in the region, and your track record stood out."
    else:
        greeting = f"Hi Team at {company_name}," if company_name and company_name != "there" else "Hi there,"
        personalized_hook = f"I came across {company_name} while researching established grant advisory firms, and your expertise stood out." if company_name and company_name != "there" else "I came across your firm while researching established grant advisory practices, and your expertise stood out."
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Partnership Opportunity - FSI Digital</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a1a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a1a;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#111827;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);border:1px solid #1e293b;">
          
          <!-- PREMIUM HEADER WITH GRADIENT -->
          <tr>
            <td style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:28px 40px;text-align:left;border-bottom:1px solid #2d3a55;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="color:#38bdf8;font-size:22px;font-weight:800;letter-spacing:1.5px;">FSI DIGITAL</span>
                    <span style="color:#475569;font-size:11px;display:block;margin-top:2px;letter-spacing:0.5px;">LEAD GENERATION DIVISION</span>
                  </td>
                  <td align="right">
                    <span style="display:inline-block;background-color:#059669;color:#ffffff;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:0.5px;">PARTNERSHIP INQUIRY</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- MAIN CONTENT -->
          <tr>
            <td style="padding:36px 40px 20px;color:#cbd5e1;font-size:15px;line-height:1.75;">
              <p style="margin:0 0 16px;color:#e2e8f0;">{greeting}</p>
              
              <p style="margin:0 0 16px;">
                {personalized_hook}
              </p>
              
              <p style="margin:0 0 20px;">
                I am the founder of <a href="https://fsidigital.ca" style="color:#38bdf8;text-decoration:none;font-weight:600;">FSI Digital</a>, a content-driven lead generation platform focused exclusively on government grants and SR&amp;ED tax credits across Canada and the USA.
              </p>
              
              <p style="margin:0 0 24px;">
                We generate warm, high-intent inbound leads organically through our SEO-ranked grant guides and eligibility tools. These are business owners who actively search for funding, read our content, and submit detailed inquiry forms. We do not offer consulting or grant writing services, which is exactly why I am reaching out to you.
              </p>
            </td>
          </tr>
          
          <!-- LIVE STATS DASHBOARD -->
          <tr>
            <td style="padding:0 40px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;border:1px solid #1e3a5f;">
                <tr>
                  <td colspan="3" style="background:linear-gradient(135deg,#0c1f3d,#162d50);padding:14px 20px;border-bottom:1px solid #1e3a5f;">
                    <span style="color:#38bdf8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Live Pipeline Stats</span>
                  </td>
                </tr>
                <tr>
                  <td width="33%" style="background-color:#0f1d36;padding:18px 16px;text-align:center;border-right:1px solid #1e3a5f;">
                    <div style="color:#38bdf8;font-size:28px;font-weight:800;line-height:1;">500+</div>
                    <div style="color:#64748b;font-size:10px;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Active Leads</div>
                  </td>
                  <td width="33%" style="background-color:#0f1d36;padding:18px 16px;text-align:center;border-right:1px solid #1e3a5f;">
                    <div style="color:#10b981;font-size:28px;font-weight:800;line-height:1;">5/day</div>
                    <div style="color:#64748b;font-size:10px;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">New Inbound</div>
                  </td>
                  <td width="33%" style="background-color:#0f1d36;padding:18px 16px;text-align:center;">
                    <div style="color:#f59e0b;font-size:28px;font-weight:800;line-height:1;">100%</div>
                    <div style="color:#64748b;font-size:10px;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Organic SEO</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 3-STEP PARTNERSHIP MODEL -->
          <tr>
            <td style="padding:0 40px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0d1b2a;border-radius:12px;border:1px solid #1e3a5f;overflow:hidden;">
                <tr>
                  <td style="padding:18px 20px 8px;">
                    <span style="color:#e2e8f0;font-size:14px;font-weight:700;">How it works (3 simple steps):</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:8px 20px 18px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#38bdf8,#0284c7);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">1</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">We send you <strong style="color:#e2e8f0;">3 free sample leads</strong> so you can verify the quality firsthand.</td>
                          </tr></table>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#10b981,#059669);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">2</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">You contact the leads and see how high-intent they are (these prospects already want funding help).</td>
                          </tr></table>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0;">
                          <table cellpadding="0" cellspacing="0"><tr>
                            <td style="width:28px;height:28px;background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:50%;text-align:center;color:#fff;font-size:12px;font-weight:800;line-height:28px;vertical-align:middle;">3</td>
                            <td style="padding-left:12px;color:#94a3b8;font-size:13px;line-height:1.5;">If you like the quality, we set up a <strong style="color:#e2e8f0;">weekly or monthly exclusive lead supply</strong> for your firm.</td>
                          </tr></table>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- TRUST INDICATORS -->
          <tr>
            <td style="padding:0 40px 24px;">
              <table width="100%" cellpadding="0" cellspacing="8">
                <tr>
                  <td width="50%" style="background-color:#0d1b2a;border-radius:8px;padding:14px 16px;border:1px solid #1e3a5f;">
                    <div style="color:#38bdf8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Exclusive Access</div>
                    <div style="color:#94a3b8;font-size:12px;line-height:1.4;">Each lead is sold to only one firm. No bidding wars or shared lists.</div>
                  </td>
                  <td width="50%" style="background-color:#0d1b2a;border-radius:8px;padding:14px 16px;border:1px solid #1e3a5f;">
                    <div style="color:#10b981;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Zero Risk Trial</div>
                    <div style="color:#94a3b8;font-size:12px;line-height:1.4;">Start with 3 complimentary leads. No contracts or commitments required.</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CLOSING + CTA -->
          <tr>
            <td style="padding:0 40px 32px;color:#cbd5e1;font-size:15px;line-height:1.75;">
              <p style="margin:0 0 24px;">
                Would it make sense for me to send over the 3 free sample leads so your team can evaluate the fit?
              </p>
              
              <!-- CTA BUTTON -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left">
                    <a href="mailto:{sender_email}?subject=Yes%20-%20Send%20Me%20the%203%20Free%20Sample%20Leads" style="display:inline-block;background:linear-gradient(135deg,#0284c7,#0369a1);color:#ffffff;font-size:14px;font-weight:700;text-decoration:none;padding:14px 32px;border-radius:8px;box-shadow:0 4px 14px rgba(2,132,199,0.3);letter-spacing:0.3px;">
                      Yes, Send Me the 3 Free Leads &rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- PREMIUM FOOTER -->
          <tr>
            <td style="background:linear-gradient(135deg,#060d1b,#0a1628);padding:24px 40px;border-top:1px solid #1e293b;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="color:#64748b;font-size:12px;line-height:1.6;">
                    <strong style="color:#94a3b8;">Ashwani Kumar</strong><br>
                    Founder &amp; CEO, FSI Digital<br>
                    <a href="https://fsidigital.ca" style="color:#38bdf8;text-decoration:none;">fsidigital.ca</a> &nbsp;|&nbsp; <a href="mailto:{sender_email}" style="color:#38bdf8;text-decoration:none;">{sender_email}</a>
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

def send_b2b_email(server, recipient_email, company_name, dm_name, dm_role, sender_email, sender_display_name):
    """Constructs and sends a premium B2B cold email."""
    subject = random.choice(SUBJECT_OPTIONS).replace("{company_name}", company_name or "your firm")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_display_name} <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    html_body = get_b2b_html_body(company_name, dm_name, dm_role, sender_email)
    msg.attach(MIMEText(html_body, 'html'))
    
    server.send_message(msg)
    print(f"📧 [B2B] Sent B2B pitch to {recipient_email} (Target: {dm_name} at {company_name}) | Subject: {subject} | From: {sender_display_name} <{sender_email}>")

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
        
    # 2. Load Sent Log (handles backward compatibility with plain emails)
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

    # 3. Connect and Send loop (Connection-Per-Email with Inbox Rotation for robustness)
    if not ACCOUNTS:
        print("❌ Error: No B2B sender accounts loaded from environment secrets.")
        return
        
    # Check daily sending cap before sending and filter active accounts
    active_accounts = []
    for acc in ACCOUNTS:
        sent_today = check_daily_sending_limit(SENT_LOG_FILE, acc["email"])
        print(f"📊 Daily sending audit: B2B Account ({acc['email']}) has sent {sent_today}/{DAILY_CAP} emails in the last 24 hours.")
        if sent_today < DAILY_CAP:
            active_accounts.append({
                "email": acc["email"],
                "password": acc["password"],
                "display_name": acc["display_name"],
                "remaining": DAILY_CAP - sent_today
            })
            
    if not active_accounts:
        print("🛑 All loaded B2B accounts have reached their daily caps. Skipping this outreach batch.")
        return
        
    count = 0
    rotation_idx = 0
    for lead in fresh_leads:
        available_accounts = [acc for acc in active_accounts if acc["remaining"] > 0]
        if not available_accounts:
            print("🛑 All B2B accounts have exhausted their limits during this run.")
            break
            
        if count >= BATCH_SIZE:
            print(f"🛑 Batch size limit of {BATCH_SIZE} reached for this execution cycle.")
            break
            
        # Rotate B2B accounts to distribute sending load
        account = available_accounts[rotation_idx % len(available_accounts)]
        sender_email = account["email"]
        app_password = account["password"]
        sender_display_name = account["display_name"]
        
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
 
        # Determine SMTP Host based on custom domain vs gmail
        smtp_host = "smtppro.zoho.in" if "fsidigital.ca" in sender_email.lower() else "smtp.gmail.com"
        
        print(f"⚡ Connecting to {smtp_host} as {sender_display_name} ({sender_email}) to send B2B email to {email}...")
        try:
            server = smtplib.SMTP(smtp_host, 587, timeout=15)
            server.starttls()
            server.login(sender_email, app_password)
            
            send_b2b_email(server, email, company, dm_name, dm_role, sender_email, sender_display_name)
            server.quit()
            
            count += 1
            account["remaining"] -= 1
            rotation_idx += 1
            
            # Append immediately to local logs in format: email,timestamp,sender
            timestamp_str = pd.Timestamp.now(tz='UTC').isoformat()
            with open(SENT_LOG_FILE, "a") as f:
                f.write(f"{email},{timestamp_str},{sender_email}\n")
                
            # 15-second spam-protection delay between sends
            if count < BATCH_SIZE and any(acc["remaining"] > 0 for acc in active_accounts):
                time.sleep(15)
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Critical Authentication Failure for B2B sender {sender_email}: {e}. Aborting batch.")
            break
        except Exception as e:
            print(f"⚠️ Failed to send B2B email to {email}. Error: {e}")
            time.sleep(5)
            
    print(f"\n🎉 SUCCESS: Automated B2B batch completed! Sent {count} emails.")

if __name__ == "__main__":
    main()
