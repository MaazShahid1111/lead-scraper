import asyncio
import json
import os
from playwright.async_api import async_playwright
from datetime import datetime
import re

USA_CITIES = [
    'Portland OR', 'San Francisco CA', 'Los Angeles CA', 
    'San Diego CA', 'Sacramento CA', 'Oakland CA', 'San Jose CA',
    
    'Denver CO', 'Boulder CO', 'Phoenix AZ', 'Tucson AZ', 
    'Salt Lake City UT', 'Albuquerque NM', 'Las Vegas NV',
    
    'Austin TX', 'Houston TX', 'Dallas TX', 'San Antonio TX',
    'Nashville TN', 'Memphis TN', 'Atlanta GA', 'Charlotte NC',
    'Raleigh NC', 'Charleston SC', 'New Orleans LA', 'Miami FL',
    'Tampa FL', 'Orlando FL',
    
    'Chicago IL', 'Minneapolis MN', 'Milwaukee WI', 'Kansas City MO',
    'St Louis MO', 'Indianapolis IN', 'Columbus OH', 'Detroit MI',
    
    'Boston MA', 'New York NY', 'Philadelphia PA', 'Pittsburgh PA',
    'Portland ME', 'Burlington VT', 'Providence RI', 'Baltimore MD',
    'Washington DC'
]

NICHES = [
    "Coffee Shop", "Cafe", "Espresso Bar",
    "Restaurant", "Bakery", "Food Truck",
    "Gym", "Fitness Studio", "Yoga Studio",
    "Hair Salon", "Barber Shop", "Nail Salon", "Spa",
    "Roofing Contractor", "Landscaping Service", "Tree Service",
    "Cleaning Service", "Plumber", "Electrician",
    "Handyman", "Painter", "Carpenter", "HVAC",
    "Auto Repair", "Mobile Mechanic", "Car Wash",
    "Pet Grooming", "Dog Trainer", "Veterinarian",
    "Tattoo Shop", "Photography Studio", "Florist"
]

def is_valid_email(email):
    """Check if email is valid (any domain, not just Gmail)"""
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_email_from_text(text):
    """Extract any email from text using regex"""
    if not text:
        return None
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def clean_business_name(name):
    """Remove common business suffixes and clean name"""
    if not name:
        return "Unknown"
    
    suffixes = ['Ltd', 'Limited', 'LTD', 'LLC', 'Inc', 'Incorporated', 
                'Corp', 'Corporation', 'Co', 'Company', 'Pty', 'PTY',
                'L.L.C.', 'L.L.C', 'INC', 'CORP']
    
    clean = name
    for suffix in suffixes:
        clean = re.sub(rf'\b{suffix}\.?\b', '', clean, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    clean = ' '.join(clean.split())
    return clean.strip()

def load_leads():
    """Load existing leads"""
    filename = "usa_leads.json"
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_leads(leads):
    """Save leads to JSON file"""
    filename = "usa_leads.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(leads)} leads to {filename}")

# ==============================================================================
# OPTIMIZED LEAD SCRAPER
# ==============================================================================
async def scrape_google_maps():
    async with async_playwright() as p:
        # Faster browser launch
        browser = await p.chromium.launch(
            headless=True,  # Headless = faster
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        leads = load_leads()
        initial_count = len(leads)
        
        print(f"🎯 Goal: Find {TARGET_COUNT} USA businesses with emails")
        print(f"📊 Current leads: {initial_count}")
        print(f"🌍 Searching {len(USA_CITIES)} cities\n")

        try:
            for city_idx, city in enumerate(USA_CITIES, 1):
                print(f"\n{'='*60}")
                print(f"🏙️ City {city_idx}/{len(USA_CITIES)}: {city}")
                print(f"{'='*60}")
                
                for niche_idx, niche in enumerate(NICHES, 1):
                    # Stop if we hit target
                    if len(leads) >= TARGET_COUNT:
                        print(f"\n🎉 TARGET REACHED: {len(leads)} leads!")
                        break
                    
                    query = f"{niche} in {city}"
                    print(f"  🔍 [{niche_idx}/{len(NICHES)}] {niche}...", end=" ")
                    
                    try:
                        # Navigate to search
                        await page.goto(
                            f"https://www.google.com/maps/search/{query.replace(' ', '+')}",
                            timeout=15000
                        )
                        await page.wait_for_timeout(3000)  # Reduced wait time

                        # Quick scroll to load results (reduced scrolls)
                        for _ in range(2):  # Reduced from 4 to 2
                            await page.mouse.wheel(0, 2000)
                            await page.wait_for_timeout(1000)  # Reduced from 2000

                        # Get all listings
                        listings = await page.query_selector_all('div[role="article"]')
                        found_in_search = 0
                        
                        for listing in listings[:15]:  # Limit to first 15 per search
                            try:
                                # Click listing
                                await listing.click()
                                await page.wait_for_timeout(2000)  # Reduced from 3000
                                
                                # === CRITICAL FILTERS ===
                                
                                # 1. Must NOT have a website
                                website = await page.query_selector('a[data-item-id="authority"]')
                                if website:
                                    continue
                                
                                # 2. Extract business name
                                name = None
                                name_selectors = [
                                    'h1.DUwDid',
                                    'h1.DUO9ee', 
                                    'div.TIH60c h1',
                                    'h1'
                                ]
                                
                                for selector in name_selectors:
                                    el = await page.query_selector(selector)
                                    if el:
                                        text = await el.inner_text()
                                        if text and len(text) > 2 and text.lower() not in ['results', 'result']:
                                            name = clean_business_name(text)
                                            break
                                
                                if not name:
                                    continue
                                
                                # 3. Extract EMAIL (REQUIRED)
                                email = None
                                
                                # Method 1: Check email button/link
                                email_selectors = [
                                    'button[data-item-id^="email"]',
                                    'a[data-item-id^="email"]',
                                    'a[href^="mailto:"]',
                                    'button[aria-label*="email" i]'
                                ]
                                
                                for selector in email_selectors:
                                    try:
                                        el = await page.query_selector(selector)
                                        if el:
                                            # Try data-item-id
                                            attr = await el.get_attribute("data-item-id")
                                            if attr and 'email:' in attr:
                                                potential = attr.replace("email:", "").strip()
                                                if is_valid_email(potential):
                                                    email = potential.lower()
                                                    break
                                            
                                            # Try href
                                            href = await el.get_attribute("href")
                                            if href and 'mailto:' in href:
                                                potential = href.replace("mailto:", "").strip()
                                                if is_valid_email(potential):
                                                    email = potential.lower()
                                                    break
                                            
                                            # Try text content
                                            text = await el.inner_text()
                                            potential = extract_email_from_text(text)
                                            if potential and is_valid_email(potential):
                                                email = potential.lower()
                                                break
                                    except:
                                        continue
                                
                                # Method 2: Scan details panel
                                if not email:
                                    try:
                                        panel = await page.query_selector('div.m6QErb')
                                        if panel:
                                            panel_text = await panel.inner_text()
                                            potential = extract_email_from_text(panel_text)
                                            if potential and is_valid_email(potential):
                                                email = potential.lower()
                                    except:
                                        pass
                                
                                # SKIP if no email found
                                if not email:
                                    continue
                                
                                # 4. Extract phone (optional)
                                phone = None
                                try:
                                    phone_el = await page.query_selector('button[data-item-id^="phone:tel:"]')
                                    if phone_el:
                                        phone_attr = await phone_el.get_attribute("data-item-id")
                                        if phone_attr:
                                            phone = phone_attr.replace("phone:tel:", "").strip()
                                except:
                                    pass
                                
                                # 5. Create lead object
                                new_lead = {
                                    "business_name": name,
                                    "email": email,
                                    "phone": phone,
                                    "city": city,
                                    "niche": niche,
                                    "country": "USA",
                                    "status": "pending",
                                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                                # 6. Check duplicates
                                if not any(l['email'] == email for l in leads):
                                    leads.append(new_lead)
                                    found_in_search += 1
                                    print(f"\n    ✅ {name} | {email}")
                                    
                                    # Save every 5 leads
                                    if len(leads) % 5 == 0:
                                        save_leads(leads)
                                
                            except Exception:
                                continue
                        
                        print(f"({found_in_search} found)")
                                
                    except Exception as e:
                        print(f"⚠️ Error: {str(e)[:50]}")
                        continue
                
                # Check if target reached
                if len(leads) >= TARGET_COUNT:
                    break
                    
        finally:
            # Final save
            save_leads(leads)
            await browser.close()
            
            print(f"\n{'='*60}")
            print(f"🎉 SCRAPING COMPLETE!")
            print(f"📊 Total leads: {len(leads)}")
            print(f"📈 New leads: {len(leads) - initial_count}")
            print(f"💾 Saved to: usa_leads.json")
            print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(scrape_google_maps())