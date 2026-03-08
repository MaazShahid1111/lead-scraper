import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random

# ==============================================================================
# EMAIL TEMPLATES
# ==============================================================================

EMAIL_SUBJECT = "Quick question about {business_name}"

EMAIL_BODY = """Hi there,

I was browsing Google Maps looking for {niche} services in {city} and came across {business_name}.

I noticed you don't have a website yet. As a web developer, I'd love to offer you a FREE preview of what a professional site could look like for your business - no strings attached.

If you're interested, just reply with:
• Your business name
• What services you offer  
• Any specific features you'd like

I'll have a custom preview ready for you within 24 hours.

Best regards,
{your_name}"""

# ==============================================================================
# GMAIL SENDER
# ==============================================================================

class GmailSender:
    def __init__(self, gmail_address, app_password, your_name):
        """
        Initialize Gmail sender
        
        IMPORTANT: You need an APP PASSWORD, not your regular Gmail password!
        
        How to get App Password:
        1. Go to myaccount.google.com/security
        2. Enable 2-Step Verification
        3. Search "App Passwords"
        4. Create password for "Mail"
        5. Copy the 16-character code
        """
        self.gmail_address = gmail_address
        self.app_password = app_password
        self.your_name = your_name
    
    def send_email(self, to_email, business_name, niche, city):
        """Send single email"""
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = to_email
            msg['Subject'] = EMAIL_SUBJECT.format(business_name=business_name)
            
            # Format body
            body = EMAIL_BODY.format(
                niche=niche,
                city=city,
                business_name=business_name,
                your_name=self.your_name
            )
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_address, self.app_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ AUTHENTICATION FAILED!")
            print("   Make sure you're using an App Password, not regular password")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

# ==============================================================================
# LEAD MANAGER
# ==============================================================================

class LeadManager:
    def __init__(self, country_file):
        self.country_file = country_file
        self.leads = self.load_leads()
    
    def load_leads(self):
        """Load leads from file"""
        if not os.path.exists(self.country_file):
            print(f"❌ File not found: {self.country_file}")
            return []
        
        with open(self.country_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        # Add tracking fields if missing
        for lead in leads:
            if 'contacted' not in lead:
                lead['contacted'] = False
            if 'contacted_date' not in lead:
                lead['contacted_date'] = None
        
        return leads
    
    def save_leads(self):
        """Save leads back to file"""
        with open(self.country_file, 'w', encoding='utf-8') as f:
            json.dump(self.leads, f, indent=2, ensure_ascii=False)
    
    def get_uncontacted(self):
        """Get leads that haven't been contacted"""
        return [l for l in self.leads if not l.get('contacted', False)]
    
    def mark_contacted(self, lead):
        """Mark lead as contacted"""
        for l in self.leads:
            if l['gmail'] == lead['gmail']:
                l['contacted'] = True
                l['contacted_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
        self.save_leads()

# ==============================================================================
# MAIN CAMPAIGN
# ==============================================================================

def run_campaign():
    """Run the outreach campaign"""
    
    print("\n" + "="*70)
    print("📧 GMAIL COLD OUTREACH - INITIAL CONTACT")
    print("="*70)
    
    # Step 1: Select country file
    print("\n📁 Select country file:")
    files = [f for f in os.listdir('.') if f.endswith('_valid.json')]
    
    if not files:
        print("❌ No _valid.json files found!")
        print("Run the Gmail validator first.")
        return
    
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    try:
        choice = int(input("\nEnter number: ")) - 1
        country_file = files[choice]
    except:
        print("❌ Invalid choice")
        return
    
    # Step 2: Load leads
    manager = LeadManager(country_file)
    uncontacted = manager.get_uncontacted()
    
    print(f"\n📊 Statistics:")
    print(f"   • Total leads: {len(manager.leads)}")
    print(f"   • Already contacted: {len(manager.leads) - len(uncontacted)}")
    print(f"   • Available to contact: {len(uncontacted)}")
    
    if not uncontacted:
        print("\n✅ All leads have been contacted!")
        return
    
    # Step 3: Get Gmail credentials
    print("\n" + "="*70)
    print("🔑 GMAIL SETUP")
    print("="*70)
    print("\n⚠️  CRITICAL: You need an APP PASSWORD (not regular password)!")
    print("\nHow to get App Password:")
    print("  1. Go to: myaccount.google.com/security")
    print("  2. Enable '2-Step Verification' (if not enabled)")
    print("  3. Search for 'App Passwords'")
    print("  4. Click 'App Passwords'")
    print("  5. Select 'Mail' and 'Other device'")
    print("  6. Copy the 16-character password (looks like: xxxx xxxx xxxx xxxx)")
    print("\n⚠️  Use a NEW/BURNER Gmail account, not your main one!\n")
    
    gmail_address = input("Enter Gmail address: ").strip()
    app_password = input("Enter App Password (16 chars): ").replace(" ", "").strip()
    your_name = input("Enter your name: ").strip()
    
    # Step 4: How many to send?
    print("\n" + "="*70)
    print("📮 HOW MANY EMAILS TO SEND?")
    print("="*70)
    print("\n⚠️  Gmail Limits to avoid ban:")
    print("   • Day 1: Send 10-20 emails MAX")
    print("   • Day 2: Send 20-30 emails MAX")
    print("   • Day 3+: Can increase to 30-50 per day")
    print(f"\n📊 You have {len(uncontacted)} uncontacted leads")
    
    try:
        num_to_send = int(input("\nHow many emails to send TODAY? "))
        if num_to_send > len(uncontacted):
            num_to_send = len(uncontacted)
            print(f"⚠️  Adjusted to {num_to_send} (all available)")
    except:
        print("❌ Invalid number")
        return
    
    # Step 5: Confirm
    print(f"\n📋 SUMMARY:")
    print(f"   • Sending from: {gmail_address}")
    print(f"   • Emails to send: {num_to_send}")
    print(f"   • File: {country_file}")
    
    confirm = input("\n✅ Start sending? (yes/no): ").lower()
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Step 6: Send emails
    sender = GmailSender(gmail_address, app_password, your_name)
    
    print("\n" + "="*70)
    print("🚀 SENDING EMAILS...")
    print("="*70 + "\n")
    
    sent_count = 0
    failed_count = 0
    
    for i, lead in enumerate(uncontacted[:num_to_send], 1):
        business_name = lead['business_name']
        email = lead['gmail']
        niche = lead['niche']
        city = lead['city']
        
        print(f"[{i}/{num_to_send}] Sending to: {business_name} ({email})...", end=" ")
        
        # Send email
        success = sender.send_email(email, business_name, niche, city)
        
        if success:
            print("✅ SENT")
            manager.mark_contacted(lead)
            sent_count += 1
            
            # Random delay between 3-8 seconds (looks more human)
            if i < num_to_send:
                delay = random.randint(3, 8)
                print(f"   ⏳ Waiting {delay} seconds...\n")
                time.sleep(delay)
        else:
            print("❌ FAILED")
            failed_count += 1
            
            # If authentication fails, stop immediately
            if "AUTHENTICATION" in str(success):
                print("\n❌ STOPPING: Fix your App Password and try again")
                break
    
    # Step 7: Summary
    print("\n" + "="*70)
    print("📊 CAMPAIGN COMPLETE")
    print("="*70)
    print(f"✅ Successfully sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Updated file: {country_file}")
    print(f"\n💡 Wait 24 hours before running again to avoid Gmail limits")
    print("="*70 + "\n")

# ==============================================================================
# RUN
# ==============================================================================

if __name__ == "__main__":
    run_campaign()