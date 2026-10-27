#!/usr/bin/env python3
"""Static acceptance checks for the standalone digital-marketing page."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "index.html"
WA_DESTINATION = "https://api.whatsapp.com/send/?phone=916361842299&text&type=phone_number&app_absent=0"
DIAL_DESTINATION = "tel:+916361842299"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.images = []
        self.links = []
        self.scripts = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a": self.anchors.append(attrs)
        elif tag == "img": self.images.append(attrs)
        elif tag == "link": self.links.append(attrs)
        elif tag == "script": self.scripts.append(attrs)

    def handle_data(self, data):
        self.text.append(data)


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print("PASS", message)


def main():
    html = PAGE.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)
    parser.close()
    visible = " ".join(parser.text)

    check("Kaala Mithra — AI Tech Solution" in visible, "brand identity is present")
    check("Digital Marketing" in visible and "<title>Digital Marketing Services" in html, "page is branded and titled for digital marketing")
    check("%%" not in html, "all build placeholders are resolved")
    check(len(parser.images) == 4, "hero and three digital-marketing channel images are embedded")
    check(all(i.get("src", "").startswith("data:image/") for i in parser.images), "all images are embedded as data URIs")
    check(all(i.get("alt", "").strip() for i in parser.images), "all images have descriptive alt text")
    check(all("illustrative" in i.get("alt", "").lower() or "concept" in i.get("alt", "").lower() for i in parser.images), "all campaign imagery is described as illustrative")
    check(html.count('class="concept-tag"') == 3 and "Illustrative marketing concept" in visible, "hero and channel-card visuals are visibly labeled as concepts")
    check("<form" not in html.lower(), "there is no enquiry form")

    whatsapp = [a for a in parser.anchors if (a.get("href") or "").startswith("https://api.whatsapp.com/")]
    dial = [a for a in parser.anchors if (a.get("href") or "").startswith("tel:")]
    check(len(whatsapp) == 5, f"WhatsApp actions are present ({len(whatsapp)} links)")
    check(all(a.get("href") == WA_DESTINATION for a in whatsapp), "every WhatsApp link uses +91 63618 42299")
    check(all(a.get("target", "_self").lower() == "_self" for a in whatsapp), "WhatsApp links stay in the same tab")
    check(len(dial) == 3, f"dial actions are present ({len(dial)} links)")
    check(all(a.get("href") == DIAL_DESTINATION for a in dial), "every dial action uses tel:+916361842299")
    check(parse_qs(urlsplit(WA_DESTINATION).query).get("phone") == ["916361842299"], "WhatsApp URL carries the correct international number")
    check("+91 63618 42299" in visible, "contact number is displayed consistently")
    check('href="mailto:kaalamithra.sales@gmail.com"' in html, "email contact uses kaalamithra.sales@gmail.com")
    check(not any(a.get("target", "").lower() == "_blank" for a in whatsapp), "no WhatsApp link opens a popup or new tab")

    for section_id in ("home", "channels", "services", "approach", "process", "contact"):
        check(f'id="{section_id}"' in html, f"navigation target #{section_id} exists")
    check("@media(max-width:640px)" in html and "@media(max-width:900px)" in html, "responsive mobile and tablet styles are embedded")
    check('id="menuToggle"' in html and "aria-expanded" in html and "nav.hidden=!open" in html, "mobile menu has an accessible toggle")
    check(not parser.links, "there are no external stylesheet or favicon dependencies")
    check(all(not script.get("src") for script in parser.scripts), "all scripts are inline")
    check("data:font/woff2;base64," in html, "font files are embedded")
    check("data:image/png;base64," in html, "brand logo is embedded")
    check(not re.search(r"<script[^>]+src=|<link[^>]+href=(?!\"data:)", html, re.I), "the page makes no external asset requests")
    check('id="year"' in html and "new Date().getFullYear()" in html, "copyright year updates automatically")
    print(f"RESULT: all checks passed · {len(parser.anchors)} total links · {PAGE.stat().st_size / 1024:.0f} KB self-contained HTML")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print("FAIL", exc)
        sys.exit(1)
