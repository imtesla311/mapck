from __future__ import annotations

import json
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "maps/europe/europe_ids.svg"
SIZE = (3055, 2684)
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGION_IMAGE_SIZE = (2400, 1850)


COUNTRIES = [
    {"number": 1, "id": "gISL", "code": "is", "name": "Iceland", "capital": "Reykjavik"},
    {"number": 2, "id": "gIRL", "code": "ie", "name": "Ireland", "capital": "Dublin"},
    {"number": 3, "id": "gGBR", "code": "gb", "name": "United Kingdom", "capital": "London", "alternateNames": ["UK", "Britain", "Great Britain"]},
    {"number": 4, "id": "gPRT", "code": "pt", "name": "Portugal", "capital": "Lisbon"},
    {"number": 5, "id": "gESP", "code": "es", "name": "Spain", "capital": "Madrid"},
    {"number": 6, "id": "gAND", "code": "ad", "name": "Andorra", "capital": "Andorra la Vella"},
    {"number": 7, "id": "gFR1", "code": "fr", "name": "France", "capital": "Paris"},
    {"number": 8, "id": "gBEL", "code": "be", "name": "Belgium", "capital": "Brussels"},
    {"number": 9, "id": "gNLD", "code": "nl", "name": "Netherlands", "capital": "Amsterdam"},
    {"number": 10, "id": "gLUX", "code": "lu", "name": "Luxembourg", "capital": "Luxembourg"},
    {"number": 11, "id": "gDEU", "code": "de", "name": "Germany", "capital": "Berlin"},
    {"number": 12, "id": "gDNK", "code": "dk", "name": "Denmark", "capital": "Copenhagen"},
    {"number": 13, "id": "gNOR", "code": "no", "name": "Norway", "capital": "Oslo"},
    {"number": 14, "id": "gSWE", "code": "se", "name": "Sweden", "capital": "Stockholm"},
    {"number": 15, "id": "gFI1", "code": "fi", "name": "Finland", "capital": "Helsinki"},
    {"number": 16, "id": "gEST", "code": "ee", "name": "Estonia", "capital": "Tallinn"},
    {"number": 17, "id": "gLVA", "code": "lv", "name": "Latvia", "capital": "Riga"},
    {"number": 18, "id": "gLTU", "code": "lt", "name": "Lithuania", "capital": "Vilnius"},
    {"number": 19, "id": "gPOL", "code": "pl", "name": "Poland", "capital": "Warsaw"},
    {"number": 20, "id": "gBLR", "code": "by", "name": "Belarus", "capital": "Minsk"},
    {"number": 21, "id": "gCZE", "code": "cz", "name": "Czechia", "capital": "Prague", "alternateNames": ["Czech Republic"]},
    {"number": 22, "id": "gSVK", "code": "sk", "name": "Slovakia", "capital": "Bratislava"},
    {"number": 23, "id": "gAUT", "code": "at", "name": "Austria", "capital": "Vienna"},
    {"number": 24, "id": "gCHE", "code": "ch", "name": "Switzerland", "capital": "Bern"},
    {"number": 25, "id": "gLIE", "code": "li", "name": "Liechtenstein", "capital": "Vaduz"},
    {"number": 26, "id": "gMCO", "code": "mc", "name": "Monaco", "capital": "Monaco"},
    {"number": 27, "id": "gITA", "code": "it", "name": "Italy", "capital": "Rome"},
    {"number": 28, "id": "gSMR", "code": "sm", "name": "San Marino", "capital": "San Marino"},
    {"number": 29, "id": "gVAT", "code": "va", "name": "Vatican City", "capital": "Vatican City", "alternateNames": ["Holy See", "Vatican"]},
    {"number": 30, "id": "gSVN", "code": "si", "name": "Slovenia", "capital": "Ljubljana"},
    {"number": 31, "id": "gHRV", "code": "hr", "name": "Croatia", "capital": "Zagreb"},
    {"number": 32, "id": "gBIH", "code": "ba", "name": "Bosnia and Herzegovina", "capital": "Sarajevo"},
    {"number": 33, "id": "gMNE", "code": "me", "name": "Montenegro", "capital": "Podgorica"},
    {"number": 34, "id": "gALB", "code": "al", "name": "Albania", "capital": "Tirana"},
    {"number": 35, "id": "gMKD", "code": "mk", "name": "North Macedonia", "capital": "Skopje", "alternateNames": ["Macedonia"]},
    {"number": 36, "id": "gRKS", "code": "xk", "name": "Kosovo", "capital": "Pristina"},
    {"number": 37, "id": "gSRB", "code": "rs", "name": "Serbia", "capital": "Belgrade"},
    {"number": 38, "id": "gHUN", "code": "hu", "name": "Hungary", "capital": "Budapest"},
    {"number": 39, "id": "gROU", "code": "ro", "name": "Romania", "capital": "Bucharest"},
    {"number": 40, "id": "gMDA", "code": "md", "name": "Moldova", "capital": "Chisinau"},
    {"number": 41, "id": "gUKR", "code": "ua", "name": "Ukraine", "capital": "Kyiv", "alternateCapitals": ["Kiev"]},
    {"number": 42, "id": "gRUS", "code": "ru", "name": "Russia", "capital": "Moscow"},
    {"number": 43, "id": "gGRC", "code": "gr", "name": "Greece", "capital": "Athens"},
    {"number": 44, "id": "gBGR", "code": "bg", "name": "Bulgaria", "capital": "Sofia"},
    {"number": 45, "id": "gTUR", "code": "tr", "name": "Turkey", "capital": "Ankara"},
    {"number": 46, "id": "gCYP", "code": "cy", "name": "Cyprus", "capital": "Nicosia"},
    {"number": 47, "id": "gGEO", "code": "ge", "name": "Georgia", "capital": "Tbilisi"},
    {"number": 48, "id": "gARM", "code": "am", "name": "Armenia", "capital": "Yerevan"},
    {"number": 49, "id": "gAZE", "code": "az", "name": "Azerbaijan", "capital": "Baku"},
    {"number": 50, "id": "gMLT", "code": "mt", "name": "Malta", "capital": "Valletta"},
]


OVERRIDES = {
    "gAND": (470, 1060),
    "gBEL": (430, 810),
    "gNLD": (430, 730),
    "gLUX": (425, 875),
    "gDNK": (520, 610),
    "gLIE": (615, 925),
    "gMCO": (470, 1035),
    "gSMR": (710, 1020),
    "gVAT": (710, 1115),
    "gMNE": (750, 1080),
    "gRKS": (890, 1065),
    "gMKD": (915, 1120),
    "gMLT": (760, 1325),
    "gCYP": (1260, 1240),
}


REGIONS = [
    {
        "id": "northwest_europe",
        "name": "Northwest Europe",
        "image": ROOT / "maps/europe/northwest_europe.jpg",
        "crop": (0, 120, 1900, 1600),
        "ids": [
            "gISL", "gIRL", "gGBR", "gDNK", "gNOR", "gSWE", "gFI1",
        ],
    },
    {
        "id": "northeast_europe",
        "name": "Northeast Europe",
        "image": ROOT / "maps/europe/northeast_europe.jpg",
        "crop": (1050, 80, 3055, 1600),
        "ids": [
            "gEST", "gLVA", "gLTU", "gPOL", "gBLR", "gMDA", "gUKR", "gRUS",
        ],
    },
    {
        "id": "southwest_central_europe",
        "name": "Southwest & Central Europe",
        "image": ROOT / "maps/europe/southwest_central_europe.jpg",
        "crop": (0, 760, 2150, 2670),
        "ids": [
            "gPRT", "gESP", "gAND", "gFR1", "gBEL", "gNLD", "gLUX", "gDEU",
            "gCZE", "gSVK", "gAUT", "gCHE", "gLIE", "gMCO", "gITA", "gSMR",
            "gVAT", "gSVN", "gHRV", "gHUN", "gMLT",
        ],
    },
    {
        "id": "southeast_europe",
        "name": "Southeast Europe",
        "image": ROOT / "maps/europe/southeast_europe.jpg",
        "crop": (1000, 700, 3055, 2670),
        "ids": [
            "gBIH", "gMNE", "gALB", "gMKD", "gRKS", "gSRB", "gROU", "gBGR",
            "gGRC", "gTUR", "gCYP", "gGEO", "gARM", "gAZE",
        ],
    },
]


def render_svg(svg_path: Path, output_path: Path, background: str) -> None:
    subprocess.run(
        ["magick", "-background", background, str(svg_path), str(output_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build_mask_positions() -> dict[str, dict[str, object]]:
    root0 = ET.parse(SVG_PATH).getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    positions: dict[str, dict[str, object]] = {}

    for entry in COUNTRIES:
        target_id = entry["id"]
        root = deepcopy(root0)

        for child in list(root):
            if child.tag.endswith("g") and child.attrib.get("id") not in {"Countries"}:
                root.remove(child)

        countries = root.find('.//svg:g[@id="Countries"]', ns)
        assert countries is not None

        for child in list(countries):
            if child.attrib.get("id") != target_id:
                countries.remove(child)

        for elem in countries.iter():
            if elem is countries:
                continue
            elem.attrib["style"] = "fill:#000000;stroke:none;fill-opacity:1;stroke-opacity:0"
            if "fill" in elem.attrib:
                elem.attrib["fill"] = "#000000"
            if "stroke" in elem.attrib:
                elem.attrib["stroke"] = "none"

        with tempfile.TemporaryDirectory() as td:
            svg_file = Path(td) / "country.svg"
            png_file = Path(td) / "country.png"
            ET.ElementTree(root).write(svg_file, encoding="utf-8", xml_declaration=True)
            render_svg(svg_file, png_file, "none")

            img = Image.open(png_file).convert("RGBA")
            if img.size != SIZE:
                img = img.resize(SIZE, Image.Resampling.NEAREST)
            alpha = img.getchannel("A")
            bbox = alpha.getbbox()
            if not bbox:
                raise ValueError(f"No visible pixels for {target_id}")

            pixels = alpha.load()
            xs: list[int] = []
            ys: list[int] = []
            for y in range(bbox[1], bbox[3]):
                for x in range(bbox[0], bbox[2]):
                    if pixels[x, y] > 0:
                        xs.append(x)
                        ys.append(y)

            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            positions[target_id] = {
                "bbox": bbox,
                "centroid": (cx, cy),
            }

    return positions


def build_country_masks() -> dict[str, Image.Image]:
    root0 = ET.parse(SVG_PATH).getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    masks: dict[str, Image.Image] = {}

    for entry in COUNTRIES:
        target_id = entry["id"]
        root = deepcopy(root0)

        for child in list(root):
            if child.tag.endswith("g") and child.attrib.get("id") not in {"Countries"}:
                root.remove(child)

        countries = root.find('.//svg:g[@id="Countries"]', ns)
        assert countries is not None

        for child in list(countries):
            if child.attrib.get("id") != target_id:
                countries.remove(child)

        for elem in countries.iter():
            if elem is countries:
                continue
            elem.attrib["style"] = "fill:#000000;stroke:none;fill-opacity:1;stroke-opacity:0"
            if "fill" in elem.attrib:
                elem.attrib["fill"] = "#000000"
            if "stroke" in elem.attrib:
                elem.attrib["stroke"] = "none"

        with tempfile.TemporaryDirectory() as td:
            svg_file = Path(td) / "country.svg"
            png_file = Path(td) / "country.png"
            ET.ElementTree(root).write(svg_file, encoding="utf-8", xml_declaration=True)
            render_svg(svg_file, png_file, "none")

            img = Image.open(png_file).convert("RGBA")
            if img.size != SIZE:
                img = img.resize(SIZE, Image.Resampling.NEAREST)
            masks[target_id] = img.getchannel("A")

    return masks


def draw_number(draw: ImageDraw.ImageDraw, position: tuple[float, float], number: int, font: ImageFont.FreeTypeFont) -> None:
    x, y = position
    radius = 22
    bounds = (x - radius, y - radius, x + radius, y + radius)
    draw.ellipse(bounds, fill="#0f4c81", outline="white", width=4)

    text = str(number)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    width = right - left
    height = bottom - top
    draw.text((x - width / 2, y - height / 2 - 2), text, font=font, fill="white")


def point_in_crop(point: tuple[float, float], crop: tuple[int, int, int, int]) -> bool:
    x, y = point
    left, top, right, bottom = crop
    return left <= x <= right and top <= y <= bottom


def transform_point(
    point: tuple[float, float],
    crop: tuple[int, int, int, int],
    paste: tuple[int, int],
    scale: float,
) -> tuple[float, float]:
    left, top, _, _ = crop
    paste_x, paste_y = paste
    x, y = point
    return (paste_x + (x - left) * scale, paste_y + (y - top) * scale)


def build_region_image(
    region: dict[str, object],
    base_image: Image.Image,
    positions: dict[str, dict[str, object]],
) -> tuple[Image.Image, dict[str, int]]:
    canvas = Image.new("RGB", REGION_IMAGE_SIZE, "white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(FONT_PATH, 52)
    number_font = ImageFont.truetype(FONT_PATH, 30)

    crop = region["crop"]
    margin_x = 40
    margin_top = 110
    margin_bottom = 35
    max_width = REGION_IMAGE_SIZE[0] - margin_x * 2
    max_height = REGION_IMAGE_SIZE[1] - margin_top - margin_bottom
    crop_width = crop[2] - crop[0]
    crop_height = crop[3] - crop[1]
    scale = min(max_width / crop_width, max_height / crop_height)

    cropped = base_image.crop(crop)
    resized = cropped.resize(
        (round(crop_width * scale), round(crop_height * scale)),
        Image.Resampling.LANCZOS,
    )
    paste_x = (REGION_IMAGE_SIZE[0] - resized.width) // 2
    paste_y = margin_top
    canvas.paste(resized, (paste_x, paste_y))

    draw.text((margin_x, 30), region["name"], font=title_font, fill="black")
    draw.rectangle(
        (paste_x, paste_y, paste_x + resized.width, paste_y + resized.height),
        outline="#8a8a8a",
        width=3,
    )

    numbering: dict[str, int] = {}
    for number, country_id in enumerate(region["ids"], start=1):
        numbering[country_id] = number
        centroid = positions[country_id]["centroid"]
        override_anchor = OVERRIDES.get(country_id)
        label_anchor = override_anchor if override_anchor and point_in_crop(override_anchor, crop) else centroid

        centroid_panel = transform_point(centroid, crop, (paste_x, paste_y), scale)
        label_panel = transform_point(label_anchor, crop, (paste_x, paste_y), scale)

        if override_anchor and point_in_crop(override_anchor, crop):
            draw.line((centroid_panel[0], centroid_panel[1], label_panel[0], label_panel[1]), fill="#0f4c81", width=3)

        draw_number(draw, label_panel, number, number_font)

    return canvas, numbering


def main() -> None:
    positions = build_mask_positions()
    masks = build_country_masks()

    with tempfile.TemporaryDirectory() as td:
        base_png = Path(td) / "europe_base.png"
        render_svg(SVG_PATH, base_png, "white")
        img = Image.open(base_png).convert("RGB")
        if img.size != SIZE:
            img = img.resize(SIZE, Image.Resampling.LANCZOS)

    # Rebuild clear country borders from per-country masks so internal boundaries stay visible.
    border_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_layer)
    for mask in masks.values():
        bbox = mask.getbbox()
        if not bbox:
            continue
        edge = mask.filter(ImageFilter.FIND_EDGES)
        edge = edge.point(lambda p: 255 if p > 0 else 0)
        border_layer.paste((120, 120, 120, 255), (0, 0), edge)

    img = Image.alpha_composite(img.convert("RGBA"), border_layer).convert("RGB")
    countries_by_id = {entry["id"]: entry for entry in COUNTRIES}

    for region in REGIONS:
        image, numbering = build_region_image(region, img, positions)
        image_path = region["image"]
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(image_path, quality=92)

        region_json = {
            "id": region["id"],
            "name": region["name"],
            "entityLabel": "country",
            "mapImage": str(image_path.relative_to(ROOT)).replace("\\", "/"),
            "numberedMapImage": str(image_path.relative_to(ROOT)).replace("\\", "/"),
            "questionTypes": ["numbered_region", "capital", "reverse_capital"],
            "countries": [],
        }

        for country_id in region["ids"]:
            entry = countries_by_id[country_id]
            region_json["countries"].append(
                {
                    "id": entry["code"],
                    "name": entry["name"],
                    "capital": entry["capital"],
                    "alternateNames": [entry["name"], *entry.get("alternateNames", [])],
                    "alternateCapitals": [entry["capital"], *entry.get("alternateCapitals", [])],
                    "mapNumber": numbering[country_id],
                }
            )

        region_path = ROOT / f"data/regions/{region['id']}.json"
        region_path.parent.mkdir(parents=True, exist_ok=True)
        region_path.write_text(json.dumps(region_json, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
