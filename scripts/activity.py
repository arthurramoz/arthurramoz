"""Draw both panels from the same public repository snapshot."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

repos = []
page = 1
while True:
    url = f"https://api.github.com/users/arthurramoz/repos?type=owner&per_page=100&page={page}"
    with urlopen(Request(url, headers={"User-Agent": "arthurramoz-profile"}), timeout=30) as response:
        batch = json.load(response)
    repos.extend(r for r in batch if not r["fork"] and not r["private"])
    if len(batch) < 100:
        break
    page += 1

languages = Counter(r["language"] or "Unclassified" for r in repos)
years = Counter(int(r["created_at"][:4]) for r in repos)
today = datetime.now(timezone.utc).date()
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 236"><title>Public original repositories by language and creation year</title>',
       '<style>text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;fill:#f0f0f2}.bar{transform-box:fill-box;transform-origin:left;animation:reveal 1.4s ease-out both}@keyframes reveal{from{transform:scaleX(0)}}@media(prefers-reduced-motion:reduce){.bar{animation:none}}</style>',
       '<rect width="780" height="236" rx="20" fill="#1a1a1f"/>',
       f'<text x="26" y="35" font-size="19" font-weight="600">{len(repos)} public repositories</text>',
       f'<text x="754" y="35" text-anchor="end" font-size="15">{today} UTC</text>',
       '<path d="M26 52H754" stroke="#42424c"/>']
panels = [(26, "Primary language · top four", languages.most_common(4), "#48cae4"),
          (414, "Created per year · latest four", [(y, years[y]) for y in range(today.year-3, today.year+1)], "#fb6f92")]
for x, title, rows, color in panels:
    svg.append(f'<text x="{x}" y="83" font-size="17">{title}</text>')
    peak = max([1] + [count for _, count in rows])
    for i, (label, count) in enumerate(rows):
        y = 113 + i * 31
        svg.extend([f'<text x="{x}" y="{y}" font-size="15">{escape(str(label))}</text>',
                    f'<rect class="bar" x="{x+111}" y="{y-10}" width="{165*count/peak:.1f}" height="9" rx="4" fill="{color}"/>',
                    f'<text x="{x+304}" y="{y}" font-size="15" text-anchor="end">{count}</text>'])
Path("assets/activity.svg").write_text("\n".join(svg + ["</svg>"]), encoding="utf-8")
