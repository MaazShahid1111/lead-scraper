# 🎯 Lead Generation Bot — Automated Cold Outreach

> Scrape → Validate → Email / WhatsApp. Find local businesses with no website on Google Maps, verify their contacts for free, and send personalised cold outreach — all from one CLI.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> ⚠️ **Disclaimer:** This tool is for educational and legitimate business outreach only. Always comply with local spam/marketing laws (CAN-SPAM, GDPR). Use a burner account for outreach. The author is not responsible for any bans or misuse.

---

## ✨ Features

- **Google Maps Scraper** — finds businesses with email/phone but *no* website
- **Email Validator** — free SMTP verification, zero API keys needed
- **Cold Email Sender** — personalised Gmail outreach with rate-limit protection
- **WhatsApp Sender** — scan QR once, auto-sends with long human-like delays
- **6 Countries** — USA, UK, Canada, Australia, Ireland, New Zealand
- **30+ Niches** — coffee shops, gyms, salons, contractors, and more
- **Full Pipeline** — one command runs everything end-to-end
- **Cross-platform** — Linux, Windows, macOS

---

## ⚡ Quick Start

### Linux / macOS
```bash
git clone https://github.com/MaazShahid1111/lead-generation-bot.git
cd lead-generation-bot
bash install.sh
```

### Windows
```batch
git clone https://github.com/MaazShahid1111/lead-generation-bot.git
cd lead-generation-bot
install.bat
```

---

## 🚀 Usage

```
python lead_scrapper.py [COMMAND] [OPTIONS]
```

### Commands

| Command | Description |
|---------|-------------|
| `scrape` | Scrape Google Maps for businesses without websites |
| `validate` | Verify collected emails via free SMTP |
| `email` | Send personalised cold emails via Gmail |
| `whatsapp` | Send WhatsApp messages (scan QR once) |
| `all` | Full pipeline: scrape → validate → email |

---

### `scrape` — Find leads

```bash
# Scrape 500 USA businesses
python lead_scrapper.py scrape --country usa --target 500

# Specific cities and niches
python lead_scrapper.py scrape --country uk \
  --cities "London" "Manchester" \
  --niches "Coffee Shop" "Gym" --target 200

# Show browser window while scraping
python lead_scrapper.py scrape --country australia --target 100 --no-headless
```

| Flag | Default | Description |
|------|---------|-------------|
| `--country` | required | `usa` `uk` `canada` `australia` `ireland` `new_zealand` |
| `--target` | 500 | Stop after N leads |
| `--cities` | built-in | Override city list |
| `--niches` | built-in | Override niche list |
| `--output` | `<country>_leads.json` | Output file |
| `--no-headless` | — | Show browser window |

---

### `validate` — Verify emails

```bash
python lead_scrapper.py validate --file usa_leads.json
python lead_scrapper.py validate --file usa_leads.json --delay 3
```

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | required | Input JSON leads file |
| `--delay` | 2.0 | Seconds between checks |
| `--output` | `<file>_valid.json` | Output file for valid leads |

---

### `email` — Send cold emails

```bash
python lead_scrapper.py email \
  --file usa_leads_valid.json \
  --from you@gmail.com \
  --app-password "xxxx xxxx xxxx xxxx" \
  --name "Your Name" \
  --limit 20
```

> ⚠️ Use a **burner Gmail** + **App Password** (not your real password).
> Get one: myaccount.google.com → Security → App Passwords

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | required | Valid leads JSON |
| `--from` | required | Your Gmail address |
| `--app-password` | required | 16-char Gmail App Password |
| `--name` | required | Your name for signature |
| `--limit` | 20 | Max emails today |
| `--delay-min` | 3 | Min seconds between sends |
| `--delay-max` | 8 | Max seconds between sends |
| `--template` | built-in | Custom template file |

**Gmail daily limits:**

| Account Age | Safe Daily Limit |
|-------------|-----------------|
| < 1 week | 10–20 |
| 1–4 weeks | 20–30 |
| 1+ month | 30–50 |

---

### `whatsapp` — Send WhatsApp messages

```bash
python lead_scrapper.py whatsapp \
  --file usa_leads.json \
  --name "Your Name" \
  --limit 30
```

> ⚠️ **Use a burner number.** WhatsApp bans accounts for bulk messaging. Keep limits low and delays high.

How it works:
1. Opens a real Chrome window
2. Navigates to WhatsApp Web — scan the QR code once with your phone
3. Automatically sends messages to leads that have phone numbers
4. Uses long random delays (8–18 min between messages) to avoid bans
5. Takes 45–90 min breaks every 3–6 messages

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | required | Leads JSON with phone numbers |
| `--name` | required | Your name for message signature |
| `--limit` | 30 | Max messages this session |
| `--delay-min` | 8 | Min minutes between messages |
| `--delay-max` | 18 | Max minutes between messages |
| `--batch-min` | 3 | Min messages before long break |
| `--batch-max` | 6 | Max messages before long break |
| `--batch-pause-min` | 45 | Min minutes for batch break |
| `--batch-pause-max` | 90 | Max minutes for batch break |
| `--template` | built-in | Custom message template |

---

### `all` — Full pipeline

```bash
python lead_scrapper.py all \
  --country usa \
  --target 100 \
  --from you@gmail.com \
  --app-password "xxxx xxxx xxxx xxxx" \
  --name "Your Name" \
  --limit 20
```

---

## 📁 Output Files

```
usa_leads.json          ← all scraped leads (email + phone)
usa_leads_valid.json    ← verified email addresses only
```

Each lead:
```json
{
  "business_name": "Joe's Barbershop",
  "email": "joe@gmail.com",
  "phone": "+1 555-123-4567",
  "city": "Austin TX",
  "niche": "Barber Shop",
  "contacted": false,
  "wa_sent": false,
  "scraped_at": "2025-01-15 14:32:10"
}
```

---

## 📧 Custom Templates

**Email** — edit `config/email_template.txt`:
```
SUBJECT: Quick question about {business_name}

Hi there, ...
```

**WhatsApp** — edit `config/whatsapp_template.txt`

Variables: `{business_name}` `{niche}` `{city}` `{your_name}`

```bash
python lead_scrapper.py email --file leads_valid.json \
  --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" \
  --name "Maaz" --template config/email_template.txt
```

---

## ⚙️ Project Structure

```
lead-generation-bot/
├── lead_scrapper.py           ← CLI entry point
├── core/
│   ├── scraper_cmd.py         ← Google Maps scraper
│   ├── validator_cmd.py       ← SMTP email validator
│   ├── emailer_cmd.py         ← Gmail sender
│   ├── whatsapp_cmd.py        ← WhatsApp sender
│   └── pipeline.py            ← full pipeline
├── config/
│   ├── email_template.txt
│   └── whatsapp_template.txt
├── requirements.txt
├── install.sh                 ← Linux/macOS
└── install.bat                ← Windows
```

---

## 🛠️ Requirements

- Python 3.8+
- Chromium (installed automatically by `install.sh` / `install.bat`)

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built by [MaazShahid1111](https://github.com/MaazShahid1111)*
