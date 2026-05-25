from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE_IMAGE = ROOT / "maps/canada/canada_blank_map_preview.png"
OUTPUT = ROOT / "maps/canada/canada_provinces_numbered.png"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

NUMBERS = [
    {"number": 1, "center": (760, 1200)},
    {"number": 2, "center": (1750, 1600)},
    {"number": 3, "center": (2100, 1220)},
    {"number": 4, "center": (720, 2400)},
    {"number": 5, "center": (1260, 2280)},
    {"number": 6, "center": (1715, 2270)},
    {"number": 7, "center": (2135, 2235)},
    {"number": 8, "center": (2510, 2620)},
    {"number": 9, "center": (3190, 2340)},
    {"number": 10, "center": (3350, 1700)},
    {"number": 11, "center": (3200, 2620), "anchor": (2975, 2590)},
    {"number": 12, "center": (3335, 2870), "anchor": (3185, 2800)},
    {"number": 13, "center": (3200, 2470), "anchor": (2980, 2460)},
]


def draw_number(draw: ImageDraw.ImageDraw, center: tuple[int, int], number: int, font: ImageFont.FreeTypeFont) -> None:
    x, y = center
    radius = 44
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="#0f4c81", outline="white", width=6)

    text = str(number)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    draw.text((x - (right - left) / 2, y - (bottom - top) / 2 - 3), text, font=font, fill="white")


def main() -> None:
    base = Image.open(BASE_IMAGE).convert("RGB")
    base_pixels = base.load()

    province_mask = Image.new("L", base.size, 0)
    mask_pixels = province_mask.load()
    for y in range(base.height):
        for x in range(base.width):
            r, g, b = base_pixels[x, y]
            if r > 100 or g > 100 or b > 100:
                mask_pixels[x, y] = 255

    image = Image.new("RGB", base.size, "white")
    image.paste((120, 126, 135), (0, 0), province_mask)

    edge_mask = province_mask.filter(ImageFilter.FIND_EDGES)
    edge_mask = edge_mask.point(lambda p: 255 if p > 0 else 0)
    image.paste((48, 52, 58), (0, 0), edge_mask)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 50)

    for entry in NUMBERS:
        anchor = entry.get("anchor")
        if anchor:
            draw.line((anchor[0], anchor[1], entry["center"][0], entry["center"][1]), fill="#0f4c81", width=6)
        draw_number(draw, entry["center"], entry["number"], font)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)


if __name__ == "__main__":
    main()
