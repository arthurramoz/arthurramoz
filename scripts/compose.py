"""Compose the profile artwork from local project covers and refreshed charts."""
import base64
import re
from pathlib import Path
from xml.sax.saxutils import escape

root = Path(__file__).resolve().parents[1]
assets = root / "assets"
s = (assets / "profile-showcase-v2.svg").read_text(encoding="utf8")
for old, new in [
    ("#1a1a1f", "#ffffff"), ("#373740", "#e7eef2"),
    ("#f0f0f2", "#202734"), ("#90e0ef", "#087e98"),
    ("#ff8fab", "#b92c60"), ("#292932", "#eef4f7"),
    ("#24242c", "#eef4f7"), ("#393942", "#e1e9ef"),
    ("#555560", "#e1e9ef"),
]:
    s = s.replace(old, new)
# Keep white brand marks legible on light chips.
s = s.replace('fill="#ffffff"', 'fill="#ffffff"', 1)
s = s.replace('fill="white"', 'fill="#263447"')
s = s.replace('fill="#ffffff" font', 'fill="#263447" font')
s = s.replace('<rect width="100%" height="100%" rx="9" fill="#eef4f7"/>',
              '<rect width="100%" height="100%" rx="9" fill="#e4ebf1"/>')
s = s.replace('viewBox="0 0 960 951"', 'viewBox="0 0 960 2260"')
s = s.replace('width="960" height="951"', 'width="960" height="2260"')
font = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
parts = [f'<g font-family="{font}"><text x="44" y="1007" font-size="27" font-weight="650" fill="#202734">Selected work</text>']
projects = [("cqt", "Certeza que Tem"), ("qb", "Queimando o Bacon"),
            ("elementa", "Elementa"), ("elevenlabs", "Eleven Labs"),
            ("solange", "Dra. Solange"), ("portfolio", "Portfolio")]
for i, (key, title) in enumerate(projects):
    x = 44 + (i % 2) * 450
    y = 1035 + (i // 2) * 295
    data = base64.b64encode((assets / "projects" / f"{key}.webp").read_bytes()).decode()
    parts.extend([
        f'<defs><clipPath id="project-{key}"><rect x="{x}" y="{y}" width="422" height="237" rx="18"/></clipPath></defs>',
        f'<image x="{x}" y="{y}" width="422" height="237" preserveAspectRatio="xMidYMid slice" clip-path="url(#project-{key})" href="data:image/webp;base64,{data}"/>',
        f'<text x="{x}" y="{y+267}" font-size="21" font-weight="600" fill="#202734">{escape(title)}</text>',
    ])
parts.append('<text x="44" y="1980" font-size="27" font-weight="650" fill="#202734">GitHub</text></g>')
chart = (assets / "activity.svg").read_text(encoding="utf8")
chart = chart.replace('<svg ', '<svg x="44" y="2010" width="872" height="230" class="chart" ', 1)
chart = chart.replace('text{', '.chart text{').replace('.bar{', '.chart .bar{')
chart = chart.replace("#f0f0f2", "#202734").replace("#1a1a1f", "#f4f7fa").replace("#42424c", "#e1e9ef").replace("#48cae4", "#087e98").replace("#fb6f92", "#b92c60")
parts.append(chart)
(assets / "dashboard-white.svg").write_text(s[:-6] + "".join(parts) + "</svg>", encoding="utf8")
