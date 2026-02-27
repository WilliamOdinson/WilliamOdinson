#!/usr/bin/env python3
"""Convert <text> elements in an SVG template to <path> using local TTF fonts."""

import sys
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def load_font(path):
    font = TTFont(path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    units_per_em = font["head"].unitsPerEm
    return glyph_set, cmap, units_per_em


def char_to_path(ch, glyph_set, cmap):
    code = ord(ch)
    glyph_name = cmap.get(code)
    if not glyph_name:
        glyph_name = cmap.get(ord(" "))
    if not glyph_name:
        return "", 0
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return pen.getCommands(), glyph_set[glyph_name].width


def text_to_paths(text, glyph_set, cmap, units_per_em, font_size, x, y, anchor="start"):
    scale = font_size / units_per_em
    advances = []
    path_data_list = []
    for ch in text:
        pd, adv = char_to_path(ch, glyph_set, cmap)
        path_data_list.append(pd)
        advances.append(adv * scale)

    total_width = sum(advances)
    if anchor == "end":
        offset_x = x - total_width
    elif anchor == "middle":
        offset_x = x - total_width / 2
    else:
        offset_x = x

    results = []
    cx = offset_x
    for pd, adv in zip(path_data_list, advances):
        if pd:
            transform = f"translate({cx:.2f},{y:.2f}) scale({scale:.6f},{-scale:.6f})"
            results.append((pd, transform))
        cx += adv
    return results


def convert_text(text_content, fonts, font_size, font_weight, fill, x, y, anchor):
    fi = fonts.get(font_weight, fonts.get("400"))
    gs, cm, upe = fi
    paths = []
    for pd, transform in text_to_paths(
        text_content, gs, cm, upe, font_size, x, y, anchor
    ):
        p = ET.Element(f"{{{NS}}}path")
        p.set("d", pd)
        p.set("transform", transform)
        p.set("fill", fill)
        paths.append(p)
    return paths


def process_text_element(text_elem, fonts):
    font_size = float(text_elem.get("font-size", "16"))
    font_weight = text_elem.get("font-weight", "400")
    fill = text_elem.get("fill", "#000")
    anchor = text_elem.get("text-anchor", "start")
    x = float(text_elem.get("x", "0"))
    y = float(text_elem.get("y", "0"))

    g = ET.Element(f"{{{NS}}}g")

    # Direct text
    if text_elem.text and text_elem.text.strip():
        for p in convert_text(
            text_elem.text.strip(), fonts, font_size, font_weight, fill, x, y, anchor
        ):
            g.append(p)

    # <tspan> children
    for tspan in text_elem.findall(f"{{{NS}}}tspan"):
        tx = float(tspan.get("x", str(x)))
        ty = float(tspan.get("y", str(y)))
        tf = tspan.get("fill", fill)
        ts = float(tspan.get("font-size", str(font_size)))
        tw = tspan.get("font-weight", font_weight)
        ta = tspan.get("text-anchor", anchor)
        content = tspan.text or ""
        if content.strip():
            for p in convert_text(content.strip(), fonts, ts, tw, tf, tx, ty, ta):
                g.append(p)

    return g


def main():
    if len(sys.argv) < 5:
        print(
            f"Usage: {sys.argv[0]} <template.svg> <output.svg> <regular.ttf> <bold.ttf>"
        )
        sys.exit(1)

    template_path, output_path, regular_ttf, bold_ttf = sys.argv[1:5]

    fonts = {
        "400": load_font(regular_ttf),
        "700": load_font(bold_ttf),
    }

    tree = ET.parse(template_path)
    root = tree.getroot()

    # Build parent map
    parent_map = {child: parent for parent in root.iter() for child in parent}

    text_elems = list(root.iter(f"{{{NS}}}text"))
    count = 0

    for text_elem in text_elems:
        parent = parent_map.get(text_elem, root)
        g = process_text_element(text_elem, fonts)
        idx = list(parent).index(text_elem)
        parent.remove(text_elem)
        parent.insert(idx, g)
        count += 1

    tree.write(output_path, xml_declaration=True, encoding="unicode")
    print(f"Generated {output_path} with {count} text nodes converted")


if __name__ == "__main__":
    main()
