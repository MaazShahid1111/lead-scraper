#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              LEAD SCRAPER - Cold Outreach Tool               ║
║   Scrape → Validate → Email / WhatsApp | Google Maps         ║
╚══════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.scraper_cmd   import run_scrape
from core.validator_cmd import run_validate
from core.emailer_cmd   import run_email
from core.whatsapp_cmd  import run_whatsapp
from core.pipeline      import run_all


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║            LEAD SCRAPER  —  Cold Outreach Tool               ║
║       Scrape → Validate → Email / WhatsApp                   ║
╚══════════════════════════════════════════════════════════════╝
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog='lead_scraper',
        description='Automated lead generation & cold outreach tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Scrape 500 USA businesses (no website, has email/phone)
  python lead_scraper.py scrape --country usa --target 500

  # Validate collected emails (free SMTP — no API needed)
  python lead_scraper.py validate --file usa_leads.json

  # Send cold emails (20/day limit recommended)
  python lead_scraper.py email --file usa_leads_valid.json \\
      --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" \\
      --name "Your Name" --limit 20

  # Send WhatsApp messages (opens browser, scan QR once)
  python lead_scraper.py whatsapp --file usa_leads.json \\
      --name "Your Name" --limit 30

  # Run full pipeline: scrape → validate → email
  python lead_scraper.py all --country usa --target 100 \\
      --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" \\
      --name "Your Name"

COUNTRIES:  usa  uk  canada  australia  ireland  new_zealand
        """
    )

    sub = parser.add_subparsers(dest='command', metavar='COMMAND')
    sub.required = True

    # ── SCRAPE ────────────────────────────────────────────────
    p = sub.add_parser('scrape', help='Scrape Google Maps for leads')
    p.add_argument('--country',    required=True,
                   choices=['usa','uk','canada','australia','ireland','new_zealand'])
    p.add_argument('--target',     type=int, default=500, metavar='N',
                   help='Stop after N leads (default: 500)')
    p.add_argument('--cities',     nargs='+', metavar='CITY')
    p.add_argument('--niches',     nargs='+', metavar='NICHE')
    p.add_argument('--output',     default=None, metavar='FILE')
    p.add_argument('--no-headless', dest='headless', action='store_false', default=True,
                   help='Show browser window')

    # ── VALIDATE ──────────────────────────────────────────────
    p = sub.add_parser('validate', help='Verify emails via free SMTP')
    p.add_argument('--file',   required=True, metavar='FILE')
    p.add_argument('--delay',  type=float, default=2.0, metavar='SECS')
    p.add_argument('--output', default=None, metavar='FILE')

    # ── EMAIL ─────────────────────────────────────────────────
    p = sub.add_parser('email', help='Send cold emails via Gmail SMTP')
    p.add_argument('--file',         required=True, metavar='FILE')
    p.add_argument('--from',         required=True, dest='gmail', metavar='EMAIL')
    p.add_argument('--app-password', required=True, metavar='PASSWORD')
    p.add_argument('--name',         required=True, metavar='NAME')
    p.add_argument('--limit',        type=int, default=20, metavar='N')
    p.add_argument('--delay-min',    type=int, default=3,  metavar='SECS')
    p.add_argument('--delay-max',    type=int, default=8,  metavar='SECS')
    p.add_argument('--template',     default=None, metavar='FILE')

    # ── WHATSAPP ──────────────────────────────────────────────
    p = sub.add_parser('whatsapp',
        help='Send WhatsApp messages (opens browser, scan QR once)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Send WhatsApp messages to leads that have phone numbers.

Opens a real Chrome window → you scan QR once → it sends automatically.
Uses long random delays (configurable) to avoid bans.
        """
    )
    p.add_argument('--file',            required=True, metavar='FILE',
                   help='JSON leads file with phone numbers')
    p.add_argument('--name',            required=True, metavar='NAME',
                   help='Your name for message signature')
    p.add_argument('--limit',           type=int, default=30, metavar='N',
                   help='Max messages to send this session (default: 30)')
    p.add_argument('--template',        default=None, metavar='FILE',
                   help='Custom message template file')
    p.add_argument('--delay-min',       type=int, default=8,  metavar='MINS',
                   help='Min minutes between messages (default: 8)')
    p.add_argument('--delay-max',       type=int, default=18, metavar='MINS',
                   help='Max minutes between messages (default: 18)')
    p.add_argument('--batch-min',       type=int, default=3,  metavar='N',
                   help='Min messages per batch before long break (default: 3)')
    p.add_argument('--batch-max',       type=int, default=6,  metavar='N',
                   help='Max messages per batch before long break (default: 6)')
    p.add_argument('--batch-pause-min', type=int, default=45, metavar='MINS',
                   help='Min minutes for long batch break (default: 45)')
    p.add_argument('--batch-pause-max', type=int, default=90, metavar='MINS',
                   help='Max minutes for long batch break (default: 90)')

    # ── ALL ───────────────────────────────────────────────────
    p = sub.add_parser('all', help='Full pipeline: scrape → validate → email')
    p.add_argument('--country',      required=True,
                   choices=['usa','uk','canada','australia','ireland','new_zealand'])
    p.add_argument('--target',       type=int, default=100)
    p.add_argument('--from',         required=True, dest='gmail')
    p.add_argument('--app-password', required=True)
    p.add_argument('--name',         required=True)
    p.add_argument('--limit',        type=int, default=20)

    return parser


def main():
    print(BANNER)
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        'scrape':    run_scrape,
        'validate':  run_validate,
        'email':     run_email,
        'whatsapp':  run_whatsapp,
        'all':       run_all,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()