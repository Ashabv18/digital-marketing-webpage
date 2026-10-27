#!/usr/bin/env python3
"""Build the standalone Kaala Mithra digital-marketing page."""
import base64
import io
import os
import re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
IMAGES = {
    "%%GROWTH_HERO%%": ("hero-growth.png", 1240, 82),
    "%%SEARCH_IMAGE%%": ("search-visibility.png", 1120, 82),
    "%%SOCIAL_IMAGE%%": ("social-content.png", 1120, 82),
    "%%PAID_IMAGE%%": ("paid-campaigns.png", 1120, 82),
}


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def image_data(filename, max_width, quality):
    image = Image.open(os.path.join(ASSETS, filename)).convert("RGB")
    if image.width > max_width:
        height = round(image.height * max_width / image.width)
        image = image.resize((max_width, height), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def main():
    html = read("index.src.html").replace("%%CSS%%", read("theme.css").replace("%%FONTS%%", read("fonts.css")))
    with open(os.path.join(ASSETS, "logo.png"), "rb") as fh:
        logo = base64.b64encode(fh.read()).decode("ascii")
    html = html.replace("%%LOGO%%", "url('data:image/png;base64," + logo + "')")
    image_bytes = 0
    for token, (filename, width, quality) in IMAGES.items():
        data = image_data(filename, width, quality)
        if token not in html:
            raise ValueError(f"Expected image token not found: {token}")
        html = html.replace(token, data)
        image_bytes += len(data)
    leftovers = re.findall(r"%%[A-Z_]+%%", html)
    if leftovers:
        raise ValueError("Unresolved build tokens: " + ", ".join(sorted(set(leftovers))))
    output = os.path.join(HERE, "index.html")
    with open(output, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Built {output} ({os.path.getsize(output) / 1024:.0f} KB; embedded images {image_bytes / 1024:.0f} KB).")


if __name__ == "__main__":
    main()
