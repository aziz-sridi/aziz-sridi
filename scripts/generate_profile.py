"""Generate self-contained README art. Python standard library only.

python scripts/generate_profile.py --refresh  # fetch public GitHub history
python scripts/generate_profile.py            # render the saved snapshot
python scripts/check_profile.py               # offline integrity check

Edit intro_svg() for speech, palette() for colors, graph_svg() for the scene.
The daily GitHub Action commits refreshed assets on main, using its built-in
token. Public calendar reads need no additional token or installed packages.
"""

import argparse
import base64
import json
import random
import re
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = "aziz-sridi"
NS = "{http://www.w3.org/2000/svg}"


class ContributionParser(HTMLParser):
    """Read the public calendar and its accessible count labels together."""

    def __init__(self):
        super().__init__()
        self.days = {}
        self.target = None
        self.label = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs and "data-level" in attrs:
            self.days[attrs["id"]] = {
                "date": attrs["data-date"], "level": int(attrs["data-level"])
            }
        if tag == "tool-tip":
            self.target, self.label = attrs.get("for"), ""

    def handle_data(self, data):
        if self.target:
            self.label += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            if self.target in self.days:
                match = re.match(r"\s*(No|[\d,]+) contributions? on ", self.label)
                if not match:
                    raise ValueError("GitHub contribution count format changed")
                count = match[1]
                self.days[self.target]["count"] = 0 if count == "No" else int(count.replace(",", ""))
            self.target = None


def validate_days(days):
    if not 350 <= len(days) <= 372:
        raise ValueError("Expected a full year of GitHub contributions")
    previous = None
    for day in days:
        current = date.fromisoformat(day["date"])
        if previous is not None and current != previous + timedelta(days=1):
            raise ValueError("Calendar dates must be unique and consecutive")
        if not 0 <= day["level"] <= 4 or day["count"] < 0:
            raise ValueError("Invalid contribution level or count")
        if (day["level"] == 0) != (day["count"] == 0):
            raise ValueError("Contribution level and count disagree")
        previous = current


def fetch_days():
    # ponytail: public HTML avoids a secret; use GraphQL if this markup changes.
    request = Request(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "one-punch-commits", "Accept-Language": "en-US"},
    )
    with urlopen(request, timeout=30) as response:
        parser = ContributionParser()
        parser.feed(response.read().decode("utf-8"))
    days = sorted(parser.days.values(), key=lambda day: day["date"])
    validate_days(days)  # Never replace good artwork with an empty/error response.
    return days


def palette(dark):
    return ({"paper": "#161b22", "ink": "#f0eee7", "muted": "#a5abb3",
             "line": "#363c44", "accent": "#f3c64e", "red": "#f1786e",
             "wave": "#f0962b", "wave_core": "#ffd45b",
             "cells": ["#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"]}
            if dark else
            {"paper": "#faf9f6", "ink": "#252a31", "muted": "#606770",
             "line": "#deded8", "accent": "#b58516", "red": "#bc463e",
             "wave": "#f0962b", "wave_core": "#ffd45b",
             "cells": ["#eff2f5", "#aceebb", "#4ac26b", "#2da44e", "#116329"]})


def svg_open(title, description, width, height, p):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
<title id="title">{escape(title)}</title><desc id="description">{escape(description)}</desc>
<style>
text {{ font-family: 'Trebuchet MS', Arial, sans-serif; fill: {p['ink']}; }}
.muted {{ fill: {p['muted']}; }}
.mono {{ font-family: Consolas, 'Liberation Mono', monospace; }}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; }}
  .animated-only {{ display: none !important; }}
}}
</style>'''


def intro_svg(dark, mobile=False):
    p = palette(dark)
    portrait = ET.parse(ASSETS / "aziz-ascii.svg").getroot().find(f"{NS}text")
    rows = "\n".join(f'<tspan x="8" y="{row.attrib["y"]}">{escape(row.text or "")}</tspan>' for row in portrait)
    phrases = ["AI & ML student.", "I explore computer vision.",
               "Seeking an AI internship.", "I build apps for fun."]
    bubble = ("M382 76H812Q845 76 845 109V231Q845 264 812 264H490L447 304L457 264H382Q344 264 344 231V113Q344 76 382 76Z" if mobile else
              "M382 76H812Q845 76 845 109V231Q845 264 812 264H382Q344 264 344 231V218L285 207L344 181V113Q344 76 382 76Z")
    result = svg_open("Hey, I'm Aziz", "ASCII Saitama introduces Aziz, an AI and machine learning student seeking an AI internship. Mobile apps are a hobby.", 560 if mobile else 900, 490 if mobile else 410, p)
    result += f'''<style>
.ascii {{ font: 10px Consolas, 'Liberation Mono', monospace; fill: {p['muted']}; }}
.phrase {{ opacity: 0; animation: phrase 16s linear infinite; }}
.phrase-primary {{ opacity: 1; }}
.reveal {{ animation: type 4s steps(24, end) infinite; transform-origin: 390px 0; }}
.caret {{ animation: cursor 4s steps(24, end) infinite; }}
.caret-mark {{ animation: blink 1s steps(1) infinite; }}
@keyframes phrase {{ 0%, 24.99% {{ opacity: 1; }} 25%, 100% {{ opacity: 0; }} }}
@keyframes type {{ 0%, 5% {{ transform: scaleX(0); }} 50%, 90% {{ transform: scaleX(1); }} 100% {{ transform: scaleX(0); }} }}
@keyframes cursor {{ 0%, 5%, 100% {{ transform: translateX(0); }} 50%, 90% {{ transform: translateX(var(--length)); }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .phrase-primary {{ opacity: 1; }} .reveal {{ transform: none; }} .caret {{ display: none; }} }}
</style>
<path d="M31 20h52M31 20v25M869 20h-52M869 20v25M31 386h52M31 386v-25M869 386h-52M869 386v-25" fill="none" stroke="{p['line']}" stroke-width="1.5" visibility="{'hidden' if mobile else 'visible'}"/>
<g transform="{'translate(10 232) scale(.32)' if mobile else 'translate(0 22) scale(.5)'}"><text class="ascii" xml:space="preserve">{rows}</text></g>
<g transform="{'translate(-323 -54)' if mobile else 'translate(0 0)'}">
<path d="{bubble}" fill="{p['ink']}" opacity=".08" transform="translate(5 7)"/>
<path d="{bubble}" fill="{p['paper']}" stroke="{p['ink']}" stroke-width="2.5" stroke-linejoin="round"/>
<text x="390" y="122" font-size="13" letter-spacing="2.2" class="muted">AI &amp; MACHINE LEARNING.</text>
<text x="387" y="177" font-size="46" font-weight="700" letter-spacing="-2">Hey, I'm Aziz<tspan fill="{p['red']}">.</tspan></text>
'''
    for i, phrase in enumerate(phrases):
        length = len(phrase) * 13.2
        result += f'''<defs><clipPath id="typing-{i}"><rect class="reveal" x="390" y="192" width="{length}" height="36" style="animation-timing-function:steps({len(phrase)},end)"/></clipPath></defs>
<g class="phrase{' phrase-primary' if i == 0 else ''}" style="animation-delay:{i * 4}s;--length:{length}px">
<text class="mono" x="390" y="220" font-size="22" textLength="{length}" lengthAdjust="spacingAndGlyphs" clip-path="url(#typing-{i})">{escape(phrase)}</text>
<g class="caret" style="animation-timing-function:steps({len(phrase)},end)"><path class="caret-mark" d="M394 201v22" stroke="{p['red']}" stroke-width="2"/></g>
</g>\n'''
    result += f'''</g>
<g transform="{'translate(-171 1)' if mobile else 'translate(0 0)'}">
<circle cx="398" cy="317" r="4" fill="{p['accent']}"/>
<text x="415" y="322" font-size="15" class="muted">AI &amp; computer vision</text>
<text x="585" y="322" font-size="15" class="muted" visibility="{'hidden' if mobile else 'visible'}">/</text>
<text x="{415 if mobile else 606}" y="{354 if mobile else 322}" font-size="15" class="muted">Mobile apps for fun</text>
<text x="390" y="{400 if mobile else 355}" font-size="13" class="mono muted">{'Seeking an AI internship.' if mobile else 'Tunisia · Seeking an AI internship.'}</text>
</g>
</svg>'''
    return result


def hero_sprite():
    frames = json.loads((ASSETS / "saitama/frames.json").read_text(encoding="utf-8"))["frames"]
    images, uses = {}, {}
    result = '<defs>'
    for frame in frames:
        source = frame["sourceAsset"]
        if source not in images:
            images[source] = f"sprite-{len(images)}"
            encoded = base64.b64encode((ASSETS / "saitama" / frame["file"]).read_bytes()).decode("ascii")
            result += f'<image id="{images[source]}" width="{frame["width"]}" height="{frame["height"]}" href="data:image/png;base64,{encoded}"/>'
        uses[frame["name"]] = f'<use href="#{images[source]}" x="{-frame["anchorX"]}" y="{-frame["anchorY"]}"/>'
    result += '''</defs><style>
.hero-sprite image { image-rendering: pixelated; }
image[id^="sprite-"] { image-rendering: pixelated; }
.sprite-idle { animation: sprite-idle 12s steps(1,end) infinite; }
.idle-frame { opacity: 0; animation: idle-frame 1s steps(1,end) infinite; }
.idle-first { opacity: 1; }
.punch-frame { opacity: 0; animation: 12s steps(1,end) infinite; }
@keyframes sprite-idle { 0%,19.499%,39%,100% { opacity: 1; } 19.5%,38.999% { opacity: 0; } }
@keyframes idle-frame { 0%,19.999% { opacity: 1; } 20%,100% { opacity: 0; } }
'''
    # Frame six is the extended fist; it lands at 3s, just before the old shockwave.
    beats = [19.5, 21, 22.5, 23.7, 24.3, 25, 28.5, 31, 34, 37, 39]
    for i, (start, end) in enumerate(zip(beats, beats[1:]), 1):
        result += f'@keyframes sprite-punch-{i} {{ 0%,{start - .001:.3f}%,{end}%,100% {{ opacity: 0; }} {start}%,{end - .001:.3f}% {{ opacity: 1; }} }}\n'
    result += '</style><g class="hero-sprite" transform="translate(105 214) scale(1.5)"><g class="sprite-idle">'
    for i in range(5):
        result += f'<g class="idle-frame{" idle-first" if i == 0 else ""}" style="animation-delay:{i * .2:.1f}s">{uses[f"stand_{i + 1}"]}</g>'
    result += '</g><g class="animated-only">'
    for i in range(1, 11):
        result += f'<g class="punch-frame" data-frame="{i}" style="animation-name:sprite-punch-{i}">{uses[f"seriouspunch_{i}"]}</g>'
    return result + '</g></g>'

def graph_svg(days, dark):
    p = palette(dark)
    if dark:
        p["paper"] = "#0d1117"
    total = sum(day["count"] for day in days)
    start, end = date.fromisoformat(days[0]["date"]), date.fromisoformat(days[-1]["date"])
    sunday = start - timedelta(days=(start.weekday() + 1) % 7)
    columns = (end - sunday).days // 7 + 1
    pitch = min(12, 642 / columns)
    result = svg_open("One-Punch Commits", f"{total:,} contributions from {start} to {end}. Pixel Saitama lands a bright punch impact and sends a yellow-orange pressure wave across the calendar, with a smaller aftershock fading behind it. Every contribution square returns to its real date and intensity.", 900, 380, p)
    result += f'''<style>
.tile {{ transform-box: fill-box; transform-origin: center; animation: scatter 12s cubic-bezier(.22,1,.36,1) infinite; }}
.stage {{ animation: shake 12s linear infinite; }}
.shockwave {{ opacity: 0; animation: shock 12s linear infinite; }}
.aftershock {{ animation-name: aftershock; }}
.impact {{ opacity: 0; animation: impact 12s cubic-bezier(.16,1,.3,1) infinite; }}
.impact-rays {{ opacity: 0; animation: impact-rays 12s cubic-bezier(.16,1,.3,1) infinite; }}
.pow {{ fill: {p['red']}; opacity: 0; animation: pow 12s linear infinite; }}
.okay {{ animation: okay 12s linear infinite; }}
@keyframes scatter {{
  0%, 25.167%, 65%, 100% {{ transform: translate(0,0) rotate(0deg) scale(1); opacity: 1; }}
  27% {{ transform: translate(var(--kick-x),var(--kick-y)) rotate(var(--kick-spin)) scale(1.15); opacity: 1; }}
  35% {{ transform: translate(var(--dx),var(--dy)) rotate(var(--spin)) scale(1); opacity: .9; }}
  43% {{ transform: translate(var(--drift-x),var(--drift-y)) rotate(var(--drift-spin)) scale(.85); opacity: .65; }}
}}
@keyframes shake {{ 0%, 24.99%, 27%, 100% {{ transform: translate(0,0); }} 25% {{ transform: translate(-3px,1px); }} 25.6% {{ transform: translate(3px,-1px); }} 26.2% {{ transform: translate(-1px,1px); }} }}
@keyframes shock {{ 0%, 25.5% {{ opacity: 0; transform: translateX(0) scale(.35); }} 25.51% {{ opacity: 1; transform: translateX(0) scale(.35); }} 29% {{ opacity: .9; transform: translateX(180px) scale(.7); }} 34% {{ opacity: .65; transform: translateX(475px) scale(.95); }} 37%, 100% {{ opacity: 0; transform: translateX(660px) scale(1.05); }} }}
@keyframes aftershock {{ 0%, 25.99% {{ opacity: 0; transform: translateX(0) scale(.35); }} 26% {{ opacity: .85; transform: translateX(0) scale(.35); }} 29% {{ opacity: .65; transform: translateX(145px) scale(.7); }} 32.5%, 100% {{ opacity: 0; transform: translateX(350px) scale(.9); }} }}
@keyframes impact {{
  0%, 24.99%, 30%, 100% {{ opacity: 0; transform: scale(.55); }}
  25% {{ opacity: 1; transform: scale(.55); }}
  25.6% {{ opacity: 1; transform: scale(1); }}
  26.5% {{ opacity: 1; transform: scale(1); animation-timing-function: linear; }}
  29.99% {{ opacity: 0; transform: scale(1.2); }}
}}
@keyframes impact-rays {{ 0%, 24.99%, 30%, 100% {{ opacity: 0; transform: scale(.7); }} 25% {{ opacity: 1; transform: scale(.7); }} 26% {{ opacity: .9; transform: scale(1); animation-timing-function: linear; }} 29.99% {{ opacity: 0; transform: scale(1.7); }} }}
@keyframes pow {{ 0%, 23.9%, 36%, 100% {{ opacity: 0; }} 24%, 32% {{ opacity: 1; }} }}
@keyframes okay {{ 0%, 17%, 65%, 100% {{ opacity: 1; }} 18%, 64% {{ opacity: 0; }} }}
</style>
<metadata>Saitama pixel sprite credited to Hacker93, shared by SantinoP: https://scratch.mit.edu/projects/305192876/. CC BY-SA 2.0: https://creativecommons.org/licenses/by-sa/2.0/. Frame timing, shockwave and real contribution calendar arranged for this profile. See assets/saitama/CREDITS.md.</metadata>
<defs><clipPath id="stage-clip"><rect x="15" y="94" width="870" height="232" rx="4"/></clipPath></defs>
<rect x="1" y="1" width="898" height="378" rx="12" fill="{p['paper']}" stroke="{p['line']}"/>
<text x="28" y="42" font-size="27" font-weight="900" font-style="italic" letter-spacing="-1">ONE-PUNCH <tspan fill="{p['red']}">COMMITS</tspan></text>
<text x="29" y="65" font-size="12" class="mono muted">DAILY TRAINING / {start.strftime('%b %Y').upper()} - {end.strftime('%b %Y').upper()}</text>
<text x="869" y="42" text-anchor="end" font-size="16" font-weight="700">{total:,} contributions</text>
<path d="M28 83H872" stroke="{p['line']}"/>
<path d="M28 328H872" stroke="{p['line']}"/>
<g clip-path="url(#stage-clip)"><g class="stage">
<path d="M42 314H218" stroke="{p['line']}" stroke-dasharray="22 7 3 12"/>
<g class="okay"><path d="M43 97h50v27H83l9 10-22-10H43Z" fill="{p['paper']}" stroke="{p['line']}"/><text x="68" y="116" text-anchor="middle" font-size="14" font-weight="700">OK.</text></g>
<g class="pow animated-only"><text x="29" y="108" font-size="14" font-weight="900" font-style="italic" style="fill:{p['red']}">SERIOUS</text><text x="29" y="125" font-size="14" font-weight="900" font-style="italic" style="fill:{p['red']}">COMMIT.</text></g>
{hero_sprite()}'''
    month = None
    for day in days:
        when = date.fromisoformat(day["date"])
        col, row = divmod((when - sunday).days, 7)
        x, y = 248 + col * pitch * .97, 167 + row * 16
        # GitHub month headings follow Sunday columns, not midweek month changes.
        if (month is None or row == 0) and when.month != month and col < columns - 2:
            result += f'<text x="{x:.2f}" y="153" font-size="10" class="month-label mono muted">{when.strftime("%b")}</text>\n'
            month = when.month
        rng = random.Random(when.toordinal())
        dx = rng.choice([-1, 1, 1]) * rng.randint(28, 105)
        dy = rng.randint(-80, 80) + (row - 3) * 12
        spin = rng.choice([-1, 1]) * rng.randint(55, 260)
        delay = (x - 232) / 470
        outline = f' stroke="{p["line"]}" stroke-width=".5"' if day["level"] == 0 else ""
        result += f'''<g transform="translate({x:.2f} {y})"><rect class="tile" width="{pitch - 3:.2f}" height="10" rx="1.5" fill="{p['cells'][day['level']]}"{outline} style="--kick-x:{dx * .6:.1f}px;--kick-y:{dy * .65:.1f}px;--kick-spin:{spin * .45:.1f}deg;--dx:{dx}px;--dy:{dy}px;--spin:{spin}deg;--drift-x:{dx * .9:.1f}px;--drift-y:{dy + 20}px;--drift-spin:{spin * 1.25:.1f}deg;animation-delay:{delay:.3f}s"><title>{day['date']}: {day['count']} contributions</title></rect></g>\n'''
    result += '<g transform="translate(232 208)">'
    for i in range(2):
        result += f'''<g class="shockwave{' aftershock' if i else ''} animated-only">
<g transform="scale({1 if i == 0 else .65})">
<path d="M-28-76C10-65 39-43 57-18L38-48C73-23 91 18 79 49L71 63C58 74 39 78 14 71L0 65C30 64 47 51 44 34L47 42C50 20 34-6 11-24L20-20C6-40-10-58-28-76Z" fill="{p['wave']}"/>
<path d="M-20-68C15-49 41-23 56 2C67 23 66 45 51 59C40 69 26 70 14 68C38 63 49 50 48 34C51 12 24-29-20-68Z" fill="{p['wave_core']}"/>
</g></g>'''
    burst = "M0-11L8-35L12-13L35-22L20-5L44 2L21 10L29 32L9 20L-1 41L-9 20L-32 29L-19 8L-43-3L-18-10L-27-32L-7-18Z"
    result += f'''</g><g transform="translate(239 188)">
<g class="impact-rays animated-only" fill="none" stroke="{p['wave']}" stroke-width="3" stroke-linecap="round"><path d="M25-21l15-12M31 6l20 6M15 29l9 15M-12-29l-8-16M-28-8l-14-4M-20 21l-10 11"/></g>
<g class="impact animated-only"><path d="{burst}" fill="{p['wave']}"/><path d="{burst}" fill="{p['wave_core']}" transform="scale(.7)"/></g>
</g>'''
    result += f'''
</g></g>
<text x="28" y="355" font-size="12" class="mono muted">100 push-ups. 100 sit-ups. git push.</text>
<text x="710" y="355" font-size="11" class="muted">Less</text>'''
    for i, color in enumerate(p["cells"]):
        result += f'<rect x="{744 + i * 16}" y="345" width="11" height="11" rx="2" fill="{color}"/>'
    result += '<text x="829" y="355" font-size="11" class="muted">More</text></svg>'
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    snapshot = ASSETS / "contributions.json"
    days = fetch_days() if args.refresh else json.loads(snapshot.read_text(encoding="utf-8"))["days"]
    validate_days(days)
    outputs = {}
    for dark in (False, True):
        suffix = "-dark" if dark else ""
        outputs[f"saitama-intro{suffix}.svg"] = intro_svg(dark)
        outputs[f"saitama-intro-mobile{suffix}.svg"] = intro_svg(dark, mobile=True)
        outputs[f"one-punch-commits{suffix}.svg"] = graph_svg(days, dark)
    for content in outputs.values():
        ET.fromstring(content)
    for name, content in outputs.items():
        (ASSETS / name).write_text(content + "\n", encoding="utf-8")
    if args.refresh:
        snapshot.write_text(json.dumps({"username": USERNAME, "source": f"https://github.com/users/{USERNAME}/contributions", "days": days}, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(outputs)} SVGs from {len(days)} days / {sum(day['count'] for day in days):,} contributions ({days[-1]['date']}).")


if __name__ == "__main__":
    main()
