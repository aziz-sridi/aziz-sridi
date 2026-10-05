"""Small offline check for the calendar parser and generated README images."""

import json
import base64
import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from generate_profile import ASSETS, ROOT, NS, ContributionParser, validate_days, palette, graph_svg


def main():
    parser = ContributionParser()
    parser.feed('''<td id="a" data-date="2026-01-01" data-level="4"></td>
<tool-tip for="a">1,234 contributions on January 1st.</tool-tip>
<td id="b" data-date="2026-01-02" data-level="0"></td>
<tool-tip for="b">No contributions on January 2nd.</tool-tip>''')
    assert parser.days["a"]["count"] == 1234
    assert parser.days["b"]["count"] == 0
    days = json.loads((ASSETS / "contributions.json").read_text(encoding="utf-8"))["days"]
    validate_days(days)
    try:
        validate_days(days[:-1] + [days[-2]])
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate calendar dates must fail")
    # Reference headings from GitHub: full Sunday start and a partial first week.
    for start, columns in [(date(2025, 10, 5), [0, 4, 9, 13, 17, 21, 26, 30, 35, 39, 43, 48]),
                           (date(2026, 1, 1), [0, 5, 9, 14, 18, 23, 27, 31, 36, 40, 44, 49])]:
        calendar = [{"date": (start + timedelta(days=i)).isoformat(), "count": 0, "level": 0} for i in range(365)]
        svg = ET.fromstring(graph_svg(calendar, False))
        labels = [text for text in svg.iter(f"{NS}text") if "month-label" in text.get("class", "").split()]
        months = [date(2026, (start.month - 1 + i) % 12 + 1, 1).strftime("%b") for i in range(12)]
        assert [label.text for label in labels] == months
        assert [float(label.get("x")) for label in labels] == [round(248 + col * 12 * .97, 2) for col in columns], "Month headings must match GitHub's week columns"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in re.findall(r'(?:src|srcset)="(\./[^"]+)"', readme):
        svg = ET.parse(ROOT / path).getroot()
        assert svg.find(f"{NS}title") is not None
        assert svg.find(f"{NS}desc") is not None
        assert svg.find(f".//{NS}script") is None
        if "one-punch" in path:
            frames = json.loads((ASSETS / "saitama/frames.json").read_text(encoding="utf-8"))["frames"]
            original_images = {(ASSETS / "saitama" / frame["file"]).read_bytes() for frame in frames}
            images = list(svg.iter(f"{NS}image"))
            assert len(images) == len(original_images), "Embed each distinct sprite once"
            assert {base64.b64decode(image.get("href").split(",")[1]) for image in images} == original_images
            assert len([g for g in svg.iter(f"{NS}g") if g.get("class") == "punch-frame"]) == 10
            cells = [r for r in svg.iter(f"{NS}rect") if r.get("class") == "tile"]
            assert len(cells) == len(days)
            for cell, day in zip(cells, days):
                assert cell.find(f"{NS}title").text == f"{day['date']}: {day['count']} contributions"
                assert cell.get("fill") == palette("-dark" in path)["cells"][day["level"]]
            directions = [float(re.search(r'--dx:([-\d.]+)px', cell.get("style"))[1]) for cell in cells]
            assert min(directions) < 0 < max(directions)
            arrivals = [float(re.search(r'animation-delay:([\d.]+)s', cell.get("style"))[1]) for cell in cells]
            assert max(arrivals[:7]) < min(arrivals[-7:]), "The wave must reach the far side later"
        assert "prefers-reduced-motion" in (ROOT / path).read_text(encoding="utf-8")
    for anchor in re.findall(r'href="#([^"]+)"', readme):
        assert f"## {anchor.replace('-', ' ').title()}".lower() in readme.replace("One-Punch", "One Punch").lower()
    print("PASS: parser, calendar integrity, GitHub month spacing, SVGs, day counts, reduced motion, and README links")


if __name__ == "__main__":
    main()
