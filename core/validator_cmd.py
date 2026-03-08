"""Validate command handler"""
import asyncio
import json
import os
import re
import smtplib
import socket
from datetime import datetime
import dns.resolver


class EmailValidator:
    def validate_syntax(self, email):
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.lower()))

    def verify_smtp(self, email):
        try:
            domain = email.split('@')[1]
            records = dns.resolver.resolve(domain, 'MX')
            mx = str(records[0].exchange)

            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            server.connect(mx)
            server.helo('verify.com')
            server.mail('verify@verify.com')
            code, _ = server.rcpt(email)
            server.quit()

            if code == 250:   return 'valid'
            elif code == 550: return 'invalid'
            else:             return 'unknown'
        except Exception:
            return 'unknown'

    async def check(self, email, delay=2.0):
        if not self.validate_syntax(email):
            return {'email': email, 'status': 'invalid', 'reason': 'Bad syntax'}
        await asyncio.sleep(delay)
        status = self.verify_smtp(email)
        reasons = {
            'valid':   'Mailbox exists',
            'invalid': 'Mailbox not found',
            'unknown': 'Could not verify (rate limit or temp error)'
        }
        return {'email': email, 'status': status, 'reason': reasons[status]}


async def _validate(leads, delay, output_file):
    validator = EmailValidator()
    emails    = list({l['email'] for l in leads if l.get('email')})

    print(f"📧 Unique emails to check: {len(emails)}")
    print(f"⏱️  Estimated time: {len(emails)*delay/60:.1f} minutes\n")

    results = {}
    for i, email in enumerate(emails, 1):
        r = await validator.check(email, delay)
        results[email] = r['status']
        icon = {'valid':'✅','invalid':'❌','unknown':'❓'}[r['status']]
        print(f"  [{i}/{len(emails)}] {icon} {email}  ({r['reason']})")

    # annotate leads
    for lead in leads:
        lead['email_status'] = results.get(lead.get('email',''), 'unknown')

    valid_leads = [l for l in leads if l.get('email_status') == 'valid']

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_leads, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*55}")
    print(f"✅ Valid:   {sum(1 for v in results.values() if v=='valid')}")
    print(f"❌ Invalid: {sum(1 for v in results.values() if v=='invalid')}")
    print(f"❓ Unknown: {sum(1 for v in results.values() if v=='unknown')}")
    print(f"💾 Valid leads saved → {output_file}")


def run_validate(args):
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return

    with open(args.file, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    output = args.output if args.output else args.file.replace('.json', '_valid.json')

    print(f"📂 Loaded {len(leads)} leads from {args.file}")
    asyncio.run(_validate(leads, args.delay, output))