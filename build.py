from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import re
from urllib.parse import quote
from xml.etree import ElementTree as ET
from zipfile import ZipFile

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
for source in sorted((site / "reports").rglob("*")):
    kind = source.suffix.lower()
    if kind not in (".svg", ".docx") or source.name.startswith("~$"):
        continue
    if any(part.lower() in {"assets", "figures", "images"} for part in source.relative_to(site / "reports").parts[:-1]):
        continue
    title = source.stem
    href = quote(source.name, safe="")
    if kind == ".svg":
        svg = ET.parse(source).getroot()
        ns = "{http://www.w3.org/2000/svg}"
        title = svg.findtext(ns + "title") or title
        paragraphs = ["".join(node.itertext()) for node in svg.iter()
                      if node.tag in {ns + "text", ns + "desc", "text", "desc"}]
        preview = f'<img src="{href}" alt="{escape(title)}">'
    else:
        w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with ZipFile(source) as doc:
            body = ET.fromstring(doc.read("word/document.xml"))
            if "docProps/core.xml" in doc.namelist():
                props = ET.fromstring(doc.read("docProps/core.xml"))
                title = props.findtext("{http://purl.org/dc/elements/1.1/}title") or title
        paragraphs = ["".join(t.text or "" for t in p.iter(w + "t")) for p in body.iter(w + "p")]
        preview = ""
    text = "".join(f"<p>{escape(line)}</p>" for line in paragraphs if line.strip())
    output = source.with_name(source.name + ".html")
    if output.exists():
        raise ValueError(f"预览页文件名冲突: {output}")
    output.write_text(f'''<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>
<style>body{{margin:0;background:#faf9f6;color:#202d39;font:17px/1.8 system-ui,sans-serif}}main{{max-width:900px;margin:3rem auto;padding:0 5%}}img{{width:100%;height:auto;background:white}}a{{color:#754036}}p{{overflow-wrap:anywhere}}</style>
</head><body><main><h1>{escape(title)}</h1><a download href="{href}">下载 {kind[1:].upper()} 原文件</a>{preview}{text}</main></body></html>''', encoding="utf-8")
from datetime import datetime, timezone
import subprocess

reports = root / "reports"
entries = []
members = set()
asset_dirs = {"assets", "images", "figures"}


def updated(path):
    rel = path.relative_to(root).as_posix()
    result = subprocess.run(["git", "log", "-1", "--format=%ct", "--", rel],
                            cwd=root, capture_output=True, text=True)
    return int(result.stdout.strip() or path.stat().st_mtime)


def add_entry(source, title, people, status, progress, files, history, task):
    folder = source.relative_to(reports).parts[0]
    group = folder if folder in categories else "unfiled"
    stamp = updated(source)
    day = datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()
    links = []
    for f in files:
        target = site / f.relative_to(root)
        if f.suffix.lower() in {".docx", ".svg"} and target.with_name(target.name + ".html").exists():
            target = target.with_name(target.name + ".html")
        link = quote(target.relative_to(site).as_posix())
        caption = '阅读 HTML 报告' if f.name == 'index.html' else f.name
        links.append(f'<a href="{link}">{escape(caption)}</a>')
    members.update(people)
    meta = " · ".join(map(escape, [categories.get(group, "未分类"), status, *people, day]))
    name = escape(title)
    if not task:
        name = f'<a href="{link}">{name}</a>'
    content = f'<small>{meta}</small><h3>{name}</h3>'
    if progress:
        content += f'<p>{escape(progress)}</p>'
    if task:
        content += '<div class="shortcuts">' + "".join(links) + '</div>'
    if history:
        content += '<details><summary>进展记录</summary>' + "".join(f'<p>{escape(h)}</p>' for h in history) + '</details>'
    if task and files:
        filenames = " ".join(f.name for f in files)
    else:
        filenames = source.name
    entries.append((stamp, group, f'<li data-group="{escape(group)}" data-status="{escape(status)}" data-people="{escape(json.dumps(people, ensure_ascii=False))}" data-search="{escape(" ".join([title, *people, filenames]))}"><article><div class="entry">{content}</div></article></li>'))


def material(f):
    return (f.is_file() and not f.name.startswith((".", "~$")) and
            f.name.lower() != "readme.md" and not asset_dirs.intersection(x.lower() for x in f.relative_to(reports).parts[:-1]))


tasks = {f.parent: f for f in reports.rglob("README.md") if len(f.relative_to(reports).parts) >= 2 and f.parent.name not in categories and not asset_dirs.intersection(f.relative_to(reports).parts)}
def owner(f):
    return next((p for p in f.parents if p in tasks), None)

for directory, readme in tasks.items():
    fields = {}
    title = directory.name
    history = []
    in_log = False
    for line in readme.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            in_log = line[3:].strip() == "进展记录"
        elif in_log and line:
            history.append(line.removeprefix("- ").strip())
        else:
            match = re.match(r"^(参与人|状态|当前进度)\s*[:：]\s*(.*)$", line)
            if match:
                fields[match[1]] = match[2]
    people = [x.strip() for x in re.split("[、,，;；]", fields.get("参与人", "")) if x.strip()]
    files = sorted(f for f in directory.rglob("*") if material(f) and owner(f) == directory)
    add_entry(directory, title, people, fields.get("状态") or "待更新", fields.get("当前进度", ""), files, history, True)

for f in sorted(reports.rglob("*")):
    if not material(f) or owner(f) or f.suffix.lower() not in {".html", ".svg", ".docx", ".pdf"}:
        continue
    title, description = f.stem, ""
    preview = site / f.relative_to(root)
    if f.suffix.lower() in {".docx", ".svg"}:
        preview = preview.with_name(preview.name + ".html")
    if preview.suffix.lower() == ".html":
        parser = Title()
        parser.feed(preview.read_text(encoding="utf-8-sig"))
        title = "".join(parser.parts).strip() or title
        description = parser.description
    add_entry(f,title,[],"资料分享",description,[f],[],False)

for path in (site / "reports").rglob("*.html"):
    back = "../" * (len(path.relative_to(site).parts) - 1) + "index.html"
    nav = f'<nav data-pagefind-ignore style="padding:10px 5%"><a href="{back}">← 小组工作台</a></nav>'
    document = path.read_text(encoding="utf-8-sig")
    if path.relative_to(site).as_posix() == "reports/gdcm/index.html":
        for anchor, heading in [("training","模型训练方法"),("example","单句输入示例")]:
            document = document.replace(f"<h2>{heading}", f'<h2 id="{anchor}">{heading}')
    path.write_text(re.sub(r"(<body\b[^>]*>)", lambda m:m[0]+nav, document, count=1, flags=re.I),encoding="utf-8")

groups = dict(categories)
if any(group == "unfiled" for _,group,_ in entries):
    groups["unfiled"] = "未分类"
buttons = []
for key, label in {"all":"全部工作", **groups}.items():
    count = sum(key == "all" or group == key for _,group,_ in entries)
    buttons.append(f'<button type="button" data-key="{escape(key)}" aria-pressed="{str(key=="all").lower()}">{escape(label)}<b>{count}</b></button>')
page = (root/"index.html").read_text(encoding="utf-8")
page = page.replace("@@NAV@@","".join(buttons)).replace("@@PEOPLE@@","".join(f'<option>{escape(p)}</option>' for p in sorted(members)))
page = page.replace("@@REPORTS@@","".join(row for _,_,row in sorted(entries,key=lambda x:-x[0])))
(site/"index.html").write_text(page,encoding="utf-8")
