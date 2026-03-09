#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║              LEAD SCRAPER  —  Cold Outreach Automation               ║
║         Scrape → Validate → Email / WhatsApp | Google Maps           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║              LEAD SCRAPER  —  Cold Outreach Automation               ║
║         Scrape → Validate → Email / WhatsApp | Google Maps           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

COUNTRIES_HELP = """
SUPPORTED COUNTRIES (120+):
  Americas : usa, canada, mexico, brazil, argentina, colombia, chile,
             peru, venezuela, ecuador, panama, costa_rica, guatemala,
             cuba, dominican_republic, jamaica, puerto_rico
  Europe   : uk, germany, france, italy, spain, netherlands, belgium,
             portugal, poland, sweden, norway, denmark, finland,
             switzerland, austria, czech_republic, hungary, romania,
             greece, ukraine, russia, turkey, croatia, serbia, and more
  Middle E : uae, saudi_arabia, israel, jordan, kuwait, qatar,
             bahrain, oman, iraq, iran, pakistan
  Asia     : india, bangladesh, indonesia, philippines, vietnam,
             thailand, malaysia, singapore, china, japan, south_korea,
             taiwan, hong_kong, myanmar, cambodia, laos
  Africa   : nigeria, south_africa, kenya, ethiopia, ghana, egypt,
             morocco, algeria, tanzania, and more
  Oceania  : australia, new_zealand, papua_new_guinea, fiji

  Aliases: us=usa, england=uk, america=usa, emirates=uae, korea=south_korea
"""

EPILOG = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🚀  ONE COMMAND — FULL PIPELINE (scrape + validate + email):

      python lead_scrapper.py all \\
          --country usa \\
          --target 100 \\
          --from you@gmail.com \\
          --app-password "xxxx xxxx xxxx xxxx" \\
          --name "John Smith"

      → Scrapes 100 leads from Google Maps
      → Validates all emails automatically
      → Sends cold emails to valid ones
      → Done. No extra steps needed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📋  STEP BY STEP (run each separately):

  STEP 1 — Scrape leads:
      python lead_scrapper.py scrape --country usa --target 200
      python lead_scrapper.py scrape --country uae --target 100 --no-headless
      python lead_scrapper.py scrape --country india --niches "Restaurant" "Cafe" --target 50

  STEP 2 — Validate emails (removes dead/fake emails):
      python lead_scrapper.py validate --file usa_leads.json

  STEP 3a — Send cold emails:
      python lead_scrapper.py email \\
          --file usa_leads_valid.json \\
          --from you@gmail.com \\
          --app-password "xxxx xxxx xxxx xxxx" \\
          --name "John Smith" \\
          --limit 20

  STEP 3b — Send WhatsApp messages:
      python lead_scrapper.py whatsapp \\
          --file usa_leads.json \\
          --name "John Smith" \\
          --limit 30

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  💡  TIPS:
      • Use --no-headless to watch the browser scrape live
      • Gmail app password: myaccount.google.com → Security → App Passwords
      • Keep email --limit to 20/day to avoid Gmail bans
      • WhatsApp uses real delays (8-18 min) between messages to stay safe
      • Output files: {country}_leads.json and {country}_leads_valid.json

""" + COUNTRIES_HELP + """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog='lead_scrapper',
        description='Automated lead generation & cold outreach — Google Maps → Email/WhatsApp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )

    sub = parser.add_subparsers(dest='command', metavar='COMMAND')
    sub.required = True

    # ── SCRAPE ────────────────────────────────────────────────────────────────
    p = sub.add_parser(
        'scrape',
        help='Scrape Google Maps for business leads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Scrape business leads from Google Maps.
Finds businesses with emails, phone numbers, and websites.

EXAMPLES:
  python lead_scrapper.py scrape --country usa --target 200
  python lead_scrapper.py scrape --country uae --target 100 --no-headless
  python lead_scrapper.py scrape --country india --niches "Restaurant" "Cafe" --target 50
  python lead_scrapper.py scrape --country uk --cities "London" "Manchester" --target 100
""",
    )
    p.add_argument('--country',     required=True, metavar='COUNTRY',
                   help='Country to scrape (usa, uk, uae, india, pakistan, etc.)')
    p.add_argument('--target',      type=int, default=100, metavar='N',
                   help='Stop after N leads collected (default: 100)')
    p.add_argument('--cities',      nargs='+', metavar='CITY',
                   help='Override city list e.g. --cities "New York NY" "Los Angeles CA"')
    p.add_argument('--niches',      nargs='+', metavar='NICHE',
                   help='Business types e.g. --niches "Restaurant" "Gym" "Hair Salon"')
    p.add_argument('--output',      default=None, metavar='FILE',
                   help='Output JSON file (default: {country}_leads.json)')
    p.add_argument('--no-headless', dest='headless', action='store_false', default=True,
                   help='Show browser window so you can watch it scrape live')

    # ── VALIDATE ──────────────────────────────────────────────────────────────
    p = sub.add_parser(
        'validate',
        help='Verify collected emails via free SMTP (no API needed)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Validate emails from your scraped leads file.
Uses free SMTP checks — no paid API required.
Removes fake/dead emails. Saves valid ones to {country}_leads_valid.json

EXAMPLE:
  python lead_scrapper.py validate --file usa_leads.json
""",
    )
    p.add_argument('--file',   required=True, metavar='FILE',
                   help='JSON leads file from scrape step')
    p.add_argument('--delay',  type=float, default=2.0, metavar='SECS',
                   help='Delay between checks in seconds (default: 2.0)')
    p.add_argument('--output', default=None, metavar='FILE',
                   help='Output file (default: {original}_valid.json)')

    # ── EMAIL ─────────────────────────────────────────────────────────────────
    p = sub.add_parser(
        'email',
        help='Send cold emails via your Gmail account',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Send cold outreach emails to validated leads via Gmail SMTP.

HOW TO GET APP PASSWORD:
  1. Go to myaccount.google.com
  2. Security → 2-Step Verification (must be ON)
  3. App Passwords → Generate → copy the 16-char password

EXAMPLE:
  python lead_scrapper.py email \\
      --file usa_leads_valid.json \\
      --from you@gmail.com \\
      --app-password "xxxx xxxx xxxx xxxx" \\
      --name "John Smith" \\
      --limit 20
""",
    )
    p.add_argument('--file',         required=True, metavar='FILE',
                   help='JSON leads file (use validated file for best results)')
    p.add_argument('--from',         required=True, dest='gmail', metavar='EMAIL',
                   help='Your Gmail address')
    p.add_argument('--app-password', required=True, metavar='PASSWORD',
                   help='Gmail App Password (16 chars, spaces ok)')
    p.add_argument('--name',         required=True, metavar='NAME',
                   help='Your name for email signature')
    p.add_argument('--limit',        type=int, default=20, metavar='N',
                   help='Max emails to send (default: 20 — stay safe with Gmail)')
    p.add_argument('--delay-min',    type=int, default=3, metavar='SECS',
                   help='Min delay between emails in seconds (default: 3)')
    p.add_argument('--delay-max',    type=int, default=8, metavar='SECS',
                   help='Max delay between emails in seconds (default: 8)')
    p.add_argument('--template',     default=None, metavar='FILE',
                   help='Custom email template file (default: config/email_template.txt)')

    # ── WHATSAPP ──────────────────────────────────────────────────────────────
    p = sub.add_parser(
        'whatsapp',
        help='Send WhatsApp messages (opens browser, scan QR once)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Send WhatsApp messages to leads that have phone numbers.

HOW IT WORKS:
  1. Opens a real Chrome browser window
  2. Go to web.whatsapp.com and scan the QR code with your phone (once)
  3. Script sends messages automatically with human-like delays

EXAMPLE:
  python lead_scrapper.py whatsapp \\
      --file usa_leads.json \\
      --name "John Smith" \\
      --limit 30
""",
    )
    p.add_argument('--file',            required=True, metavar='FILE',
                   help='JSON leads file with phone numbers')
    p.add_argument('--name',            required=True, metavar='NAME',
                   help='Your name for message signature')
    p.add_argument('--limit',           type=int, default=30, metavar='N',
                   help='Max messages to send this session (default: 30)')
    p.add_argument('--template',        default=None, metavar='FILE',
                   help='Custom message template (default: config/whatsapp_template.txt)')
    p.add_argument('--delay-min',       type=int, default=8,  metavar='MINS',
                   help='Min minutes between messages (default: 8)')
    p.add_argument('--delay-max',       type=int, default=18, metavar='MINS',
                   help='Max minutes between messages (default: 18)')
    p.add_argument('--batch-min',       type=int, default=3, metavar='N',
                   help='Messages per batch before long break (default: 3)')
    p.add_argument('--batch-max',       type=int, default=6, metavar='N',
                   help='Max messages per batch (default: 6)')
    p.add_argument('--batch-pause-min', type=int, default=45, metavar='MINS',
                   help='Min minutes for long break between batches (default: 45)')
    p.add_argument('--batch-pause-max', type=int, default=90, metavar='MINS',
                   help='Max minutes for long break between batches (default: 90)')

    # ── ALL (one command full pipeline) ───────────────────────────────────────
    p = sub.add_parser(
        'all',
        help='🚀 Full pipeline: scrape → validate → email in ONE command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Run the FULL pipeline in one command:
  1. Scrapes leads from Google Maps
  2. Validates all emails automatically
  3. Sends cold emails to valid leads

EXAMPLE:
  python lead_scrapper.py all \\
      --country usa \\
      --target 100 \\
      --from you@gmail.com \\
      --app-password "xxxx xxxx xxxx xxxx" \\
      --name "John Smith"

NOTE: Get Gmail App Password at myaccount.google.com → Security → App Passwords
""",
    )
    p.add_argument('--country',      required=True, metavar='COUNTRY',
                   help='Country to scrape (usa, uk, uae, india, pakistan, etc.)')
    p.add_argument('--target',       type=int, default=100, metavar='N',
                   help='Number of leads to collect (default: 100)')
    p.add_argument('--niches',       nargs='+', metavar='NICHE',
                   help='Business types (optional, uses defaults if not set)')
    p.add_argument('--no-headless',  dest='headless', action='store_false', default=True,
                   help='Show browser window live')
    p.add_argument('--from',         required=True, dest='gmail', metavar='EMAIL',
                   help='Your Gmail address')
    p.add_argument('--app-password', required=True, metavar='PASSWORD',
                   help='Gmail App Password (16 chars)')
    p.add_argument('--name',         required=True, metavar='NAME',
                   help='Your name for email signature')
    p.add_argument('--limit',        type=int, default=20, metavar='N',
                   help='Max emails to send (default: 20)')
    p.add_argument('--template',     default=None, metavar='FILE',
                   help='Custom email template file')

    return parser


def main():
    print(BANNER)
    parser = build_parser()

    # Show full help if no args
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Lazy imports to avoid circular import issues
    if args.command == 'scrape':
        from core.scraper_cmd import run_scrape
        run_scrape(args)

    elif args.command == 'validate':
        from core.validator_cmd import run_validate
        run_validate(args)

    elif args.command == 'email':
        from core.emailer_cmd import run_email
        run_email(args)

    elif args.command == 'whatsapp':
        from core.whatsapp_cmd import run_whatsapp
        run_whatsapp(args)

    elif args.command == 'all':
        from core.pipeline import run_all
        run_all(args)


if __name__ == '__main__':
    main()