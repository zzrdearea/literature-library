from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import re
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
    document = path.read_text(encoding="utf-8-sig")
    back = "../" * (len(path.relative_to(site).parts) - 1) + "index.html"
    navigation = f'<nav data-pagefind-ignore style="padding:10px 5%;background:#f4f3ef"><a style="color:#253f59" href="{back}">← 文献目录</a></nav>'
    document = re.sub(r"(<body\b[^>]*>)", lambda m: m[0] + navigation, document, count=1, flags=re.I)
    details = ""
    figure = ""
    if url == "reports/gdcm/index.html":
        for anchor, heading in [("training", "模型训练方法"), ("example", "单句输入示例")]:
            document = document.replace(f"<h2>{heading}", f'<h2 id="{anchor}">{heading}')
            details += f'<a href="{url}#{anchor}">{heading} →</a>'
        details = f'<div class="shortcuts">{details}</div>'
        figure = f'<a class="figure" href="{url}"><img src="reports/gdcm/figures/concept_utilization.png" alt="GDCM 十个概念的利用情况"><span>概念利用情况</span></a>'
    path.write_text(document,encoding="utf-8")
    links.append(f'<li data-group="{escape(key)}" data-url="{url}"><article><div class="entry"><small>{escape(label)}</small><h3><a href="{url}">{escape(title)}</a></h3>{summary}<p class="excerpt" hidden></p>{details}</div>{figure}</article></li>')


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
