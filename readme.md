> Scrape → Validate → Email. Find local businesses with no website on Google Maps, verify their emails for free, and send personalised cold outreach — all from one CLI.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- **Google Maps Scraper** — finds businesses with an email but *no* website
- **Email Validator** — free SMTP verification, no API key needed
- **Cold Email Sender** — personalised Gmail outreach with rate-limit protection
- **6 Countries** — USA, UK, Canada, Australia, Ireland, New Zealand
- **30+ Niches** — coffee shops, gyms, salons, contractors, and more
- **Full Pipeline** — one command runs everything end-to-end
- **Cross-platform** — works on Linux, Windows, and macOS

---

## ⚡ Quick Start

### Linux / macOS

```bash
git clone https://github.com/MaazShahid1111/lead-scraper.git
cd lead-scraper
bash install.sh
```

### Windows

```batch
git clone https://github.com/MaazShahid1111/lead-scraper.git
cd lead-scraper
install.bat
```

---

## 🚀 Usage

```
python lead_scraper.py [COMMAND] [OPTIONS]
```

### Commands

| Command    | Description                                      |
|------------|--------------------------------------------------|
| `scrape`   | Scrape Google Maps for businesses without websites |
| `validate` | Verify collected emails via free SMTP             |
| `email`    | Send personalised cold emails                    |
| `all`      | Run full pipeline in one command                 |

---

### `scrape` — Find leads

```bash
# Scrape 500 USA businesses
python lead_scraper.py scrape --country usa --target 500

# Target specific cities and niches
python lead_scraper.py scrape --country uk --cities "London" "Manchester" --niches "Coffee Shop" "Gym" --target 200

# Show browser while scraping
python lead_scraper.py scrape --country australia --target 100 --no-headless
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--country` | required | `usa` `uk` `canada` `australia` `ireland` `new_zealand` |
| `--target` | 500 | Stop after N leads |
| `--cities` | built-in list | Override city list |
| `--niches` | built-in list | Override niche list |
| `--output` | `<country>_leads.json` | Output file |
| `--no-headless` | — | Show browser window |

---

### `validate` — Verify emails

```bash
python lead_scraper.py validate --file usa_leads.json
python lead_scraper.py validate --file usa_leads.json --delay 3
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | required | Input JSON leads file |
| `--delay` | 2.0 | Seconds between checks (avoid rate limits) |
| `--output` | `<file>_valid.json` | Output file for valid leads |

---

### `email` — Send cold emails

```bash
python lead_scraper.py email \
  --file usa_leads_valid.json \
  --from you@gmail.com \
  --app-password "xxxx xxxx xxxx xxxx" \
  --name "Your Name" \
  --limit 20
```

> ⚠️ Use a **burner Gmail** + **App Password** (not your real password).  
> Get one at: myaccount.google.com → Security → App Passwords

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | required | Valid leads JSON file |
| `--from` | required | Your Gmail address |
| `--app-password` | required | 16-char Gmail App Password |
| `--name` | required | Your name for email signature |
| `--limit` | 20 | Max emails to send today |
| `--delay-min` | 3 | Min delay between sends (seconds) |
| `--delay-max` | 8 | Max delay between sends (seconds) |
| `--template` | built-in | Custom template file (see `config/email_template.txt`) |

**Gmail daily limits to avoid bans:**

| Account Age | Safe Daily Limit |
|-------------|-----------------|
| New (< 1 week) | 10–20 |
| 1–4 weeks | 20–30 |
| 1+ month | 30–50 |

---

### `all` — Full pipeline

```bash
python lead_scraper.py all \
  --country usa \
  --target 100 \
  --from you@gmail.com \
  --app-password "xxxx xxxx xxxx xxxx" \
  --name "Your Name" \
  --limit 20
```

---

## 📁 Output Files

After scraping and validating you'll have:

```
usa_leads.json          ← all scraped leads
usa_leads_valid.json    ← only verified email addresses
```

Each lead looks like:

```json
{
  "business_name": "Joe's Barbershop",
  "email": "joe@gmail.com",
  "phone": "+1 555-123-4567",
  "city": "Austin TX",
  "niche": "Barber Shop",
  "status": "pending",
  "contacted": false,
  "scraped_at": "2025-01-15 14:32:10"
}
```

---

## 📧 Custom Email Template

Copy `config/email_template.txt`, edit it, and pass it with `--template`:

```bash
python lead_scraper.py email --file leads_valid.json \
  --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" \
  --name "Maaz" --template config/my_template.txt
```

Available variables: `{business_name}` `{niche}` `{city}` `{your_name}`

---

## 🛠️ Requirements

- Python 3.8+
- Google Chrome / Chromium (installed automatically by `install.sh`)

---

## ⚙️ Project Structure

```
lead-scraper/
├── lead_scraper.py          ← main CLI entry point
├── core/
│   ├── scraper_cmd.py       ← Google Maps scraper
│   ├── validator_cmd.py     ← SMTP email validator
│   ├── emailer_cmd.py       ← Gmail sender
│   └── pipeline.py          ← full pipeline runner
├── config/
│   └── email_template.txt   ← default email template
├── requirements.txt
├── install.sh               ← Linux/macOS installer
└── install.bat              ← Windows installer
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built by [MaazShahid1111](https://github.com/MaazShahid1111)*