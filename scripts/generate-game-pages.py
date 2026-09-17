#!/usr/bin/env python3
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "store-site"
GAMES = json.loads((SITE / "games.json").read_text())
CONTACT = "support@etfradarapp.com"
EFFECTIVE = "September 17, 2026"


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(title)}">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>
"""


cards = []
for game in GAMES:
    slug = game["slug"]
    name = game["name"]
    tagline = game["tagline"]
    summary = game["summary"]
    base = SITE / "games" / slug
    (base / "support").mkdir(parents=True, exist_ok=True)
    (base / "privacy").mkdir(parents=True, exist_ok=True)

    (base / "index.html").write_text(page(
        f"{name} — Mobile Game",
        f"""<h1>{html.escape(name)}</h1>
    <p class="tagline">{html.escape(tagline)}</p>
    <div class="card"><p>{html.escape(summary)}</p></div>
    <nav aria-label="Support links">
      <a href="/games/{slug}/support/">Support</a>
      <a href="/games/{slug}/privacy/">Privacy Policy</a>
    </nav>
    <p><small><a href="/games/">All games</a></small></p>"""), encoding="utf-8")

    (base / "support" / "index.html").write_text(page(
        f"Support — {name}",
        f"""<h1>{html.escape(name)} Support</h1>
    <div class="card">
      <p>If you need help, found a problem, or want to share feedback, email
      <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
      <p>Please include your device model, iOS version, and a short description of what happened.</p>
    </div>
    <nav><a href="/games/{slug}/">Home</a><a href="/games/{slug}/privacy/">Privacy Policy</a></nav>"""), encoding="utf-8")

    (base / "privacy" / "index.html").write_text(page(
        f"Privacy Policy — {name}",
        f"""<h1>Privacy Policy</h1>
    <p><small>Effective {EFFECTIVE}</small></p>
    <p>{html.escape(name)} does not collect, transmit, sell, or share personal data.</p>
    <h2>Data stored on your device</h2>
    <p>The game may store progress, settings, and scores locally on your device. This information is not sent to us or to third parties. Removing the app deletes this local data according to iOS behavior.</p>
    <h2>Accounts, analytics, advertising, and tracking</h2>
    <p>The iOS app has no accounts, advertising, cross-app tracking, or third-party analytics configured.</p>
    <h2>Children</h2>
    <p>The app does not knowingly collect information from anyone, including children.</p>
    <h2>Contact</h2>
    <p>For privacy questions, email <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
    <nav><a href="/games/{slug}/">Home</a><a href="/games/{slug}/support/">Support</a></nav>"""), encoding="utf-8")

    cards.append(f'<div class="card"><h2><a href="/games/{slug}/">{html.escape(name)}</a></h2><p>{html.escape(tagline)}</p></div>')

(SITE / "games").mkdir(exist_ok=True)
(SITE / "games" / "index.html").write_text(page(
    "Playable Games",
    "<h1>Playable Games</h1><p class=\"tagline\">Support and privacy information</p>" + "".join(cards)), encoding="utf-8")
