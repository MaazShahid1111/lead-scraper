"""Email command handler"""
import json
import os
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

DEFAULT_SUBJECT = "Quick question about {business_name}"

DEFAULT_BODY = """Hi there,

I was browsing Google Maps looking for {niche} services in {city} and came across {business_name}.

I noticed you don't have a website yet. As a web developer, I'd love to offer you a FREE preview of what a professional site could look like for your business — no strings attached.

If you're interested, just reply with:
  • Your business name
  • What services you offer
  • Any specific features you'd like

I'll have a custom preview ready within 24 hours.

Best regards,
{your_name}"""


def load_template(filepath):
    """Load custom email template from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Expect SUBJECT: on first line, then blank line, then body
    lines = content.split('\n')
    if lines[0].startswith('SUBJECT:'):
        subject = lines[0].replace('SUBJECT:', '').strip()
        body    = '\n'.join(lines[2:]).strip()
        return subject, body
    return DEFAULT_SUBJECT, content


def send_email(gmail, app_password, to_email, subject, body):
    msg             = MIMEMultipart()
    msg['From']     = gmail
    msg['To']       = to_email
    msg['Subject']  = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail, app_password)
    server.send_message(msg)
    server.quit()


def run_email(args):
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return

    with open(args.file, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    # load template
    if args.template and os.path.exists(args.template):
        subject_tpl, body_tpl = load_template(args.template)
        print(f"📄 Using custom template: {args.template}")
    else:
        subject_tpl = DEFAULT_SUBJECT
        body_tpl    = DEFAULT_BODY

    app_password = args.app_password.replace(' ', '')

    # filter uncontacted
    uncontacted = [l for l in leads if not l.get('contacted', False)]

    print(f"\n{'='*55}")
    print(f"📧 COLD EMAIL CAMPAIGN")
    print(f"{'='*55}")
    print(f"📂 File:       {args.file}")
    print(f"📊 Total:      {len(leads)}  |  Uncontacted: {len(uncontacted)}")
    print(f"📮 Sending:    {min(args.limit, len(uncontacted))} emails")
    print(f"📤 From:       {args.gmail}")
    print(f"{'='*55}\n")

    if not uncontacted:
        print("✅ All leads already contacted!")
        return

    sent = failed = 0
    to_send = uncontacted[:args.limit]

    for i, lead in enumerate(to_send, 1):
        name   = lead.get('business_name', 'there')
        email  = lead.get('email', '')
        niche  = lead.get('niche', 'local')
        city   = lead.get('city', 'your area')

        subject = subject_tpl.format(business_name=name)
        body    = body_tpl.format(
            business_name=name,
            niche=niche,
            city=city,
            your_name=args.name
        )

        print(f"[{i}/{len(to_send)}] → {name} ({email})...", end=" ", flush=True)

        try:
            send_email(args.gmail, app_password, email, subject, body)
            print("✅ SENT")
            lead['contacted']      = True
            lead['contacted_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sent += 1

            # save progress after every send
            with open(args.file, 'w', encoding='utf-8') as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)

            if i < len(to_send):
                delay = random.randint(args.delay_min, args.delay_max)
                print(f"   ⏳ Waiting {delay}s...")
                time.sleep(delay)

        except smtplib.SMTPAuthenticationError:
            print("❌ AUTH FAILED — check your App Password")
            print("\n❌ Stopping: Fix your App Password and retry")
            break
        except Exception as e:
            print(f"❌ FAILED ({str(e)[:60]})")
            failed += 1

    print(f"\n{'='*55}")
    print(f"✅ Sent:   {sent}")
    print(f"❌ Failed: {failed}")
    print(f"💡 Wait 24h before running again to stay under Gmail limits")
    print(f"{'='*55}\n")