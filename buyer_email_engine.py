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

def get_b2b_plain_text(company_name, dm_name, dm_role, sender_email):
    """
    Returns a high-converting B2B plain text outreach template.
    Designed to look personal and bypass aggressive spam filters.
    """
    # Personalize greeting using decision maker's first name if available
    if dm_name and dm_name.lower() != "team":
        first_name = dm_name.split()[0]
        greeting = f"Hi {first_name},"
        personalized_hook = f"I came across {company_name} while researching top-tier grant advisory firms in the region, and your track record stood out."
    else:
        greeting = f"Hi Team at {company_name}," if company_name and company_name != "there" else "Hi there,"
        personalized_hook = f"I came across {company_name} while researching established grant advisory firms, and your expertise stood out." if company_name and company_name != "there" else "I came across your firm while researching established grant advisory practices, and your expertise stood out."
    
    text = f"""{greeting}

{personalized_hook}

I am the founder of FSI Digital (https://fsidigital.ca), a content-driven lead generation platform focused exclusively on government grants and SR&ED tax credits across Canada and the USA.

We generate warm, high-intent inbound leads organically through our SEO-ranked grant guides and eligibility tools. These are business owners who actively search for funding, read our content, and submit detailed inquiry forms. We do not offer consulting or grant writing services, which is exactly why I am reaching out to you.

We currently have a pipeline of 500+ active leads and get about 5 new inbound leads per day, all generated via organic SEO.

Here is how we usually set up a partnership:
1. We send you 3 free sample leads so you can verify the quality firsthand.
2. You contact the leads to see how high-intent they are (these prospects already want funding help).
3. If you like the quality, we set up a weekly or monthly exclusive lead supply for your firm (we strictly sell each lead to only one partner firm).

Would it make sense for me to send over the 3 free sample leads so your team can evaluate the fit?

Best regards,

Ashwani Kumar
Founder & CEO, FSI Digital
{sender_email}
https://fsidigital.ca"""
    return text

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
    """Constructs and sends a clean, high-deliverability plain-text B2B cold email."""
    subject = random.choice(SUBJECT_OPTIONS).replace("{company_name}", company_name or "your firm")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_display_name} <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    text_body = get_b2b_plain_text(company_name, dm_name, dm_role, sender_email)
    msg.attach(MIMEText(text_body, 'plain'))
    
    server.send_message(msg)
    print(f"📧 [B2B] Sent B2B plain-text pitch to {recipient_email} (Target: {dm_name} at {company_name}) | Subject: {subject} | From: {sender_display_name} <{sender_email}>")

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
        smtp_host = "smtp.gmail.com" if sender_email.lower().endswith("@gmail.com") else "smtppro.zoho.in"
        
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
