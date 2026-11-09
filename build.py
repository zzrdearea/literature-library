from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
from urllib.parse import quote

root = Path(__file__).resolve().parent
site = root / "_site"
if site.exists():
    shutil.rmtree(site)
shutil.copytree(root / "reports", site / "reports")


class Title(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.active = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


categories = json.loads((root / "categories.json").read_text(encoding="utf-8"))
groups = {key: [] for key in categories}
legacy = []
for path in sorted((site / "reports").rglob("*.html")):
    parser = Title()
    parser.feed(path.read_text(encoding="utf-8-sig"))
    title = "".join(parser.parts).strip() or path.stem
    url = quote(path.relative_to(site).as_posix())
    folder = path.relative_to(site / "reports").parts[0]
    links = groups.get(folder, legacy)
    links.append(f'<li><a href="{url}">{escape(title)}</a></li>')

sections = []
for folder, label in categories.items():
    links = groups[folder]
    sections.append(f'<section><header><h2>{escape(label)} · {len(links)}</h2></header><ul>{"".join(links)}</ul></section>')
if legacy:
    sections.append(f'<section><h2>未分类报告 · {len(legacy)}</h2><ul>{"".join(legacy)}</ul></section>')
page = (root / "index.html").read_text(encoding="utf-8")
(site / "index.html").write_text(page.replace("@@REPORTS@@", "".join(sections)), encoding="utf-8")
