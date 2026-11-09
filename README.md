# 共享文献报告库

## 首次部署

把本目录内的文件放在仓库根目录，包含隐藏目录 .github。默认发布分支为 main。在仓库 Settings → Pages → Build and deployment → Source 选择 GitHub Actions。推送一次提交，或在 Actions → Publish report library 中点击 Run workflow。发布完成后，Settings → Pages 显示访问网址。

## 成员投稿

在对应大类点击「上传到此类」，用有写入权限的账号把 HTML 直接提交到 main。发布完成后，报告自动归入该类并更新全文索引。团队确定分类名称后，在 categories.json 修改显示名称即可，目录编号保持固定。页面标题取自 HTML 的 title。更新同一文件保留原链接，删除文件后下次发布会移除目录和索引中的记录。

图表可以内嵌，也可随报告放在独立子目录，用相对路径引用。正文需要写进 HTML；浏览器执行 JavaScript 后才出现的正文请先导出为静态页面。只接受可信成员的网页，按网站可见范围选择报告。搜索覆盖 HTML 正文，PDF 附件内容不进入索引。

## 本地检查

在本目录运行以下命令，然后访问 http://localhost:8000。首次生成索引需要联网安装 Pagefind。

```
python build.py
npx --yes pagefind@1.4.0 --site _site --glob "reports/**/*.html" --force-language zh
python -m http.server 8000 --directory _site
```
