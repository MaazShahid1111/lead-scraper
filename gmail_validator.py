import json
import os
import asyncio
import re
from datetime import datetime
import socket
import smtplib
import dns.resolver

class GmailValidator:
    """
    Validates Gmail addresses using FREE methods:
    1. Syntax validation (regex)
    2. DNS/MX record check (Gmail servers exist)
    3. SMTP verification (checks if mailbox exists)
    """
    
    def __init__(self):
        self.results = {
            'valid': [],
            'invalid': [],
            'unknown': []
        }
    
    def validate_syntax(self, email):
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        return re.match(pattern, email.lower()) is not None
    
    def check_mx_records(self, domain='gmail.com'):
        """Check if Gmail MX records exist (they always should)"""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return len(records) > 0
        except:
            return False
    
    def verify_smtp(self, email):
        """
        SMTP verification - The FREE way to check if Gmail exists
        This connects to Gmail's SMTP server and asks if the mailbox exists
        """
        try:
            # Get MX record for gmail.com
            records = dns.resolver.resolve('gmail.com', 'MX')
            mx_record = str(records[0].exchange)
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            server.connect(mx_record)
            server.helo('gmail.com')
            server.mail('verify@gmail.com')
            
            # This is the key check - RCPT TO command
            code, message = server.rcpt(email)
            server.quit()
            
            # Gmail response codes:
            # 250 = Email exists (VALID)
            # 550 = User not found (INVALID)
            # 451/452 = Temporary issue (UNKNOWN)
            
            if code == 250:
                return 'valid'
            elif code == 550:
                return 'invalid'
            else:
                return 'unknown'
                
        except smtplib.SMTPServerDisconnected:
            return 'unknown'
        except smtplib.SMTPConnectError:
            return 'unknown'
        except Exception as e:
            return 'unknown'
    
    async def validate_email_async(self, email, delay=2):
        """Validate single email with delay to avoid rate limiting"""
        
        # Step 1: Syntax check
        if not self.validate_syntax(email):
            return {
                'email': email,
                'status': 'invalid',
                'reason': 'Invalid syntax'
            }
        
        # Step 2: Wait to avoid Gmail rate limits
        await asyncio.sleep(delay)
        
        # Step 3: SMTP verification
        status = self.verify_smtp(email)
        
        reasons = {
            'valid': 'Email exists and can receive mail',
            'invalid': 'Mailbox does not exist',
            'unknown': 'Could not verify (rate limited or temp error)'
        }
        
        return {
            'email': email,
            'status': status,
            'reason': reasons[status]
        }
    
    async def validate_batch(self, emails, delay=2):
        """Validate multiple emails with delays"""
        tasks = []
        for email in emails:
            task = self.validate_email_async(email, delay)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)

# ==============================================================================
# COUNTRY FILE PROCESSOR
# ==============================================================================

async def process_country_file(filename, delay=2):
    """Process a single country JSON file"""
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return
    
    print(f"\n{'='*60}")
    print(f"📧 Processing: {filename}")
    print(f"{'='*60}\n")
    
    # Load leads
    with open(filename, 'r', encoding='utf-8') as f:
        leads = json.load(f)
    
    if not leads:
        print(f"⚠️ No leads found in {filename}")
        return
    
    # Extract unique emails
    emails = list(set([lead['gmail'] for lead in leads if lead.get('gmail')]))
    print(f"📊 Found {len(emails)} unique Gmail addresses")
    print(f"⏱️ Estimated time: {len(emails) * delay / 60:.1f} minutes\n")
    
    # Validate emails
    validator = GmailValidator()
    results = await validator.validate_batch(emails, delay)
    
    # Categorize results
    valid_emails = []
    invalid_emails = []
    unknown_emails = []
    
    for result in results:
        if result['status'] == 'valid':
            valid_emails.append(result['email'])
            print(f"✅ VALID: {result['email']}")
        elif result['status'] == 'invalid':
            invalid_emails.append(result['email'])
            print(f"❌ DEAD: {result['email']}")
        else:
            unknown_emails.append(result['email'])
            print(f"❓ UNKNOWN: {result['email']}")
    
    # Update leads with validation status
    for lead in leads:
        email = lead.get('gmail')
        if email in valid_emails:
            lead['email_status'] = 'valid'
        elif email in invalid_emails:
            lead['email_status'] = 'invalid'
        else:
            lead['email_status'] = 'unknown'
    
    # Save results
    base_name = filename.replace('.json', '')
    
    # Save validated leads (valid only)
    valid_leads = [l for l in leads if l.get('email_status') == 'valid']
    with open(f"{base_name}_valid.json", 'w', encoding='utf-8') as f:
        json.dump(valid_leads, f, indent=2, ensure_ascii=False)
    
    # Save all leads with status
    with open(f"{base_name}_validated.json", 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    
    # Save summary report
    report = {
        'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_leads': len(leads),
        'total_emails': len(emails),
        'valid': len(valid_emails),
        'invalid': len(invalid_emails),
        'unknown': len(unknown_emails),
        'valid_emails': valid_emails,
        'invalid_emails': invalid_emails,
        'unknown_emails': unknown_emails
    }
    
    with open(f"{base_name}_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY - {filename}")
    print(f"{'='*60}")
    print(f"✅ Valid emails: {len(valid_emails)}")
    print(f"❌ Dead emails: {len(invalid_emails)}")
    print(f"❓ Unknown: {len(unknown_emails)}")
    print(f"\n💾 Files created:")
    print(f"   • {base_name}_valid.json (LIVE leads only)")
    print(f"   • {base_name}_validated.json (All leads with status)")
    print(f"   • {base_name}_report.json (Detailed report)")
    print(f"{'='*60}\n")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

async def main():
    """Process all country files"""
    
    print("🚀 FREE GMAIL VALIDATOR")
    print("=" * 60)
    print("This tool validates Gmail addresses using:")
    print("  ✓ Syntax validation")
    print("  ✓ SMTP verification (checks if mailbox exists)")
    print("  ✓ 100% FREE - No API keys needed")
    print("=" * 60)
    
    # Files to process
    country_files = ['ireland.json', 'australia.json', 'new_zealand.json']
    
    # Check which files exist
    existing_files = [f for f in country_files if os.path.exists(f)]
    
    if not existing_files:
        print("\n❌ No country files found!")
        print("Expected files: ireland.json, australia.json, new_zealand.json")
        return
    
    print(f"\n📁 Found {len(existing_files)} file(s) to process")
    
    # Process each country file
    for filename in existing_files:
        await process_country_file(filename, delay=3)  # 3 sec delay to avoid rate limits
    
    print("\n🎉 ALL DONE!")
    print("Check the _valid.json files for LIVE emails only")

if __name__ == "__main__":
    # Check dependencies
    try:
        import dns.resolver
    except ImportError:
        print("❌ Missing dependency!")
        print("Run: pip install dnspython")
        exit(1)
    
    # Run validator
    asyncio.run(main())