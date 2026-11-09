from html import escape
from html.parser import HTMLParser
import os
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


links = []
for path in sorted((site / "reports").rglob("*.html")):
    parser = Title()
    parser.feed(path.read_text(encoding="utf-8-sig"))
    title = "".join(parser.parts).strip() or path.stem
    url = quote(path.relative_to(site).as_posix())
    links.append(f'<li><a href="{url}">{escape(title)}</a></li>')

repo = os.environ.get("GITHUB_REPOSITORY")
branch = quote(os.environ.get("GITHUB_REF_NAME", "main"), safe="")
upload = f'<a href="https://github.com/{repo}/upload/{branch}/reports">上传 HTML 报告</a>' if repo else ""
page = (root / "index.html").read_text(encoding="utf-8")
page = page.replace("@@UPLOAD@@", upload).replace("@@COUNT@@", str(len(links)))
(site / "index.html").write_text(page.replace("@@REPORTS@@", "".join(links)), encoding="utf-8")
