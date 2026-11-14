"""Compose the profile artwork from local project covers and refreshed charts."""
import base64
import re
from pathlib import Path
from xml.sax.saxutils import escape

root = Path(__file__).resolve().parents[1]
assets = root / "assets"
s = (assets / "profile-showcase-v2.svg").read_text(encoding="utf8")
s = s.replace('font-size="80"', 'font-size="54"').replace('font-size="25"', 'font-size="22"')
s = s.replace('viewBox="0 0 960 951"', 'viewBox="0 0 960 2260"')
s = s.replace('width="960" height="951"', 'width="960" height="2260"')
font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
parts = [f'<g font-family="{font}"><text x="44" y="527" font-size="27" font-weight="650" fill="#f0f0f2">Projects</text>']
projects = [("cqt", "Certeza que Tem"), ("qb", "Queimando o Bacon"),
            ("elementa", "Elementa"), ("elevenlabs", "Eleven Labs"),
            ("solange", "Dra. Solange"), ("portfolio", "Portfolio")]
for i, (key, title) in enumerate(projects):
    x = 44 + (i % 2) * 450
    y = 555 + (i // 2) * 295
    data = base64.b64encode((assets / "projects" / f"{key}.png").read_bytes()).decode()
    parts.extend([
        f'<defs><clipPath id="project-{key}"><rect x="{x}" y="{y}" width="422" height="237" rx="18"/></clipPath></defs>',
        f'<image x="{x}" y="{y}" width="422" height="237" preserveAspectRatio="xMidYMid slice" clip-path="url(#project-{key})" href="data:image/png;base64,{data}"/>',
        f'<text x="{x}" y="{y+267}" font-size="21" font-weight="600" fill="#f0f0f2">{escape(title)}</text>',
    ])
parts.append('<text x="44" y="1500" font-size="27" font-weight="650" fill="#f0f0f2">GitHub</text></g>')
chart = (assets / "activity.svg").read_text(encoding="utf8")
chart = chart.replace('<svg ', '<svg x="44" y="1530" width="872" height="230" class="chart" ', 1)
chart = chart.replace('text{', '.chart text{').replace('.bar{', '.chart .bar{')
parts.append(chart)
(assets / "dashboard-refined.svg").write_text(s[:-6] + "".join(parts) + "</svg>", encoding="utf8")

# Convert text to Montserrat outlines so the artwork renders identically on GitHub.
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
ns = "{http://www.w3.org/2000/svg}"
tree = ET.fromstring((assets / "dashboard-refined.svg").read_text(encoding="utf8"))
# Move the technology groups below projects and GitHub activity.
stack_group = ET.Element(ns + "g", {"transform": "translate(0 1260)"})
for child in list(tree):
    is_heading = child.tag == ns + "g" and any(
        item.tag == ns + "text" and item.text in
        ("Frontend & design", "Backend & data", "Cloud & delivery")
        for item in child
    )
    is_divider = child.tag == ns + "path" and child.get("d") == "M44 514H916"
    if is_heading or is_divider:
        tree.remove(child)
        stack_group.append(child)
tree.append(stack_group)
fonts = {}
def outline(parent, inherited=None):
    inherited = dict(inherited or {})
    inherited.update(parent.attrib)
    for child in list(parent):
        if child.tag != ns + "text":
            outline(child, inherited)
            continue
        attrs = dict(inherited)
        attrs.update(child.attrib)
        text_content = "".join(child.itertext())
        weight = 700 if text_content == "Arthur Ramos" else min(900, int(attrs.get("font-weight", "400")) + 250)
        if text_content in ("Projects", "GitHub", "Frontend & design", "Backend & data", "Cloud & delivery"):
            weight = 700
        if weight not in fonts:
            fonts[weight] = instantiateVariableFont(TTFont(assets / "Montserrat.ttf"), {"wght": weight})
        font = fonts[weight]
        glyphs = font.getGlyphSet()
        cmap = font.getBestCmap()
        scale = float(attrs.get("font-size", "16")) / font["head"].unitsPerEm
        text = "".join(child.itertext())
        spacing = float(attrs.get("letter-spacing", "0")) / scale
        names = [cmap.get(ord(c), ".notdef") for c in text]
        width = sum(glyphs[n].width for n in names) + max(0,len(names)-1)*spacing
        x = float(attrs.get("x", "0"))
        if attrs.get("text-anchor") == "middle": x -= width*scale/2
        if attrs.get("text-anchor") == "end": x -= width*scale
        group = ET.Element(ns+"g", {"fill": attrs.get("fill", "#f0f0f2"), "transform": f"translate({x} {attrs.get('y','0')}) scale({scale} {-scale})", "aria-label": text})
        offset = 0
        for name in names:
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            ET.SubElement(group, ns+"path", {"d":pen.getCommands(), "transform":f"translate({offset} 0)"})
            offset += glyphs[name].width + spacing
        parent.insert(list(parent).index(child),group)
        parent.remove(child)
outline(tree)
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.ElementTree(tree).write(assets / "dashboard-refined.svg", encoding="utf-8")
