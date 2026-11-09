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
        self.description = ""

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            meta = dict(attrs)
            if meta.get("name") == "description":
                self.description = meta.get("content") or ""
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
    key = folder if folder in categories else "unfiled"
    label = categories.get(folder, "未分类")
    summary = f'<p>{escape(parser.description)}</p>' if parser.description else ""
    links.append(f'<li data-group="{escape(key)}"><small>{escape(label)}</small><a href="{url}">{escape(title)}<span aria-hidden="true">↗</span></a>{summary}</li>')

rows = [link for group in groups.values() for link in group] + legacy
counts = [(key, name, len(groups[key])) for key, name in categories.items()]
if legacy:
    counts.append(("unfiled", "未分类", len(legacy)))
buttons = []
for key, name, count in [("all", "全部报告", len(rows)), *counts]:
    buttons.append(f'<button type="button" data-key="{escape(key)}" aria-pressed="{str(key == "all").lower()}">{escape(name)}<b>{count}</b></button>')
page = (root / "index.html").read_text(encoding="utf-8")
page = page.replace("@@NAV@@", "".join(buttons)).replace("@@COUNT@@", str(len(rows)))
(site / "index.html").write_text(page.replace("@@REPORTS@@", "".join(rows)), encoding="utf-8")
