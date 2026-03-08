"""
WhatsApp Cold Outreach via Chrome Debug Port (port 9222)
─────────────────────────────────────────────────────────
How it works:
  1. Opens a real Chrome window at debug port 9222
  2. Navigates to web.whatsapp.com
  3. Shows QR code — user scans once
  4. Sends messages to phone numbers from leads file
  5. Random long delays (10–20 msgs per 2–3 hours) to avoid ban
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright


# ── Message template ──────────────────────────────────────────
DEFAULT_WA_MESSAGE = """Hi! 👋

I came across {business_name} on Google Maps while looking for {niche} services in {city}.

I noticed you don't have a website yet — I'd love to build you a FREE preview to show what it could look like. No commitment needed.

Interested? Just reply and I'll have something ready for you within 24 hours! 😊

— {your_name}"""


def load_template(filepath):
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return DEFAULT_WA_MESSAGE


def clean_phone(phone):
    """Strip everything except digits and leading +"""
    if not phone:
        return None
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    # Must be at least 7 digits
    digits = ''.join(c for c in cleaned if c.isdigit())
    if len(digits) < 7:
        return None
    return cleaned


async def wait_for_wa_login(page):
    """Wait until WhatsApp Web is fully loaded (QR scanned)"""
    print("\n📱 Waiting for you to scan the WhatsApp QR code...")
    print("   Open WhatsApp on your phone → Linked Devices → Link a Device")
    print("   Scan the QR code in the Chrome window\n")

    # Wait up to 3 minutes for login
    for _ in range(180):
        try:
            # Check if the main chat list is visible (means logged in)
            chat_list = await page.query_selector('div[data-testid="chat-list"]')
            if not chat_list:
                chat_list = await page.query_selector('div[aria-label="Chat list"]')
            if not chat_list:
                # fallback: search box visible
                chat_list = await page.query_selector('div[data-testid="search"]')
            if chat_list:
                print("✅ WhatsApp logged in!\n")
                return True
        except Exception:
            pass
        await asyncio.sleep(1)

    print("❌ Login timeout (3 min). Re-run and scan faster.")
    return False


async def send_whatsapp_message(page, phone, message):
    """Open a chat and send a message via WhatsApp Web URL"""
    try:
        # Encode message for URL
        import urllib.parse
        encoded = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded}"

        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(4000)

        # Check for invalid number popup
        invalid = await page.query_selector('div[data-animate-modal-popup="true"]')
        if invalid:
            text = await invalid.inner_text()
            if 'invalid' in text.lower() or 'not registered' in text.lower():
                return False, "Phone not on WhatsApp"

        # Find and click the send button
        send_selectors = [
            'button[data-testid="compose-btn-send"]',
            'span[data-testid="send"]',
            'button[aria-label="Send"]',
        ]
        sent = False
        for sel in send_selectors:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                await page.wait_for_timeout(2000)
                sent = True
                break

        if not sent:
            # Try pressing Enter
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(2000)
            sent = True

        return sent, "OK" if sent else "Send button not found"

    except Exception as e:
        return False, str(e)[:80]


async def _run_whatsapp(args):
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return

    with open(args.file, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    message_tpl = load_template(getattr(args, 'template', None))

    # Filter leads with phone numbers not yet messaged via WA
    to_message = [
        l for l in leads
        if l.get('phone') and not l.get('wa_sent', False)
    ]

    print(f"\n{'='*60}")
    print(f"📲 WHATSAPP COLD OUTREACH")
    print(f"{'='*60}")
    print(f"📂 File:          {args.file}")
    print(f"📊 Total leads:   {len(leads)}")
    print(f"📱 With phones:   {len(to_message)}")
    print(f"📮 Sending:       {min(args.limit, len(to_message))} messages")
    print(f"⏱️  Delay range:   {args.delay_min}–{args.delay_max} minutes between messages")
    print(f"{'='*60}\n")

    if not to_message:
        print("✅ All leads with phone numbers already messaged!")
        return

    to_send = to_message[:args.limit]

    async with async_playwright() as p:
        print("🌐 Launching Chrome on debug port 9222...")
        print("   (A real Chrome window will open — do NOT close it)\n")

        browser = await p.chromium.launch(
            headless=False,   # MUST be visible for QR scan
            args=[
                '--remote-debugging-port=9222',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
            ]
        )

        context = await browser.new_context(
            viewport=None,  # use actual window size
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        # ── Load WhatsApp Web ──────────────────────────────────
        print("📱 Opening WhatsApp Web...")
        await page.goto("https://web.whatsapp.com", timeout=30000)
        await page.wait_for_timeout(3000)

        # ── Wait for QR scan / existing session ───────────────
        logged_in = await wait_for_wa_login(page)
        if not logged_in:
            await browser.close()
            return

        # ── Send messages ──────────────────────────────────────
        sent = failed = skipped = 0
        batch_count = 0
        msgs_per_batch = random.randint(args.batch_min, args.batch_max)

        print(f"{'='*60}")
        print(f"🚀 SENDING MESSAGES")
        print(f"{'='*60}\n")

        for i, lead in enumerate(to_send, 1):
            phone = clean_phone(lead.get('phone', ''))
            if not phone:
                print(f"[{i}/{len(to_send)}] ⏭️  {lead.get('business_name','?')} — no valid phone, skipping")
                skipped += 1
                continue

            name  = lead.get('business_name', 'there')
            niche = lead.get('niche', 'local')
            city  = lead.get('city', 'your area')

            message = message_tpl.format(
                business_name=name,
                niche=niche,
                city=city,
                your_name=args.name
            )

            print(f"[{i}/{len(to_send)}] 📲 {name} ({phone})...", end=" ", flush=True)

            success, reason = await send_whatsapp_message(page, phone, message)

            if success:
                print("✅ SENT")
                lead['wa_sent']      = True
                lead['wa_sent_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sent += 1
                batch_count += 1

                # Save progress
                with open(args.file, 'w', encoding='utf-8') as f:
                    json.dump(leads, f, indent=2, ensure_ascii=False)

            else:
                print(f"❌ FAILED ({reason})")
                failed += 1

            # ── Delay logic ────────────────────────────────────
            if i < len(to_send):
                # After a batch, take a longer break
                if batch_count >= msgs_per_batch:
                    batch_pause = random.randint(
                        args.batch_pause_min * 60,
                        args.batch_pause_max * 60
                    )
                    print(f"\n   ⏸️  Batch of {batch_count} done.")
                    print(f"   😴 Long break: {batch_pause//60:.1f} minutes (anti-ban)...\n")
                    time.sleep(batch_pause)
                    batch_count   = 0
                    msgs_per_batch = random.randint(args.batch_min, args.batch_max)
                else:
                    # Normal delay between messages
                    delay_secs = random.randint(
                        args.delay_min * 60,
                        args.delay_max * 60
                    )
                    print(f"   ⏳ Next message in {delay_secs//60:.1f} min {delay_secs%60}s...")
                    time.sleep(delay_secs)

        await browser.close()

    print(f"\n{'='*60}")
    print(f"✅ Sent:    {sent}")
    print(f"❌ Failed:  {failed}")
    print(f"⏭️  Skipped: {skipped} (no phone number)")
    print(f"💾 Progress saved → {args.file}")
    print(f"{'='*60}\n")


def run_whatsapp(args):
    asyncio.run(_run_whatsapp(args))