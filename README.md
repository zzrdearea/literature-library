# 共享文献报告库

## 首次部署

把本目录内的文件放在仓库根目录，包含隐藏目录 .github。默认发布分支为 main。在仓库 Settings → Pages → Build and deployment → Source 选择 GitHub Actions。推送一次提交，或在 Actions → Publish report library 中点击 Run workflow。发布完成后，Settings → Pages 显示访问网址。

## 成员投稿

成员需接受仓库协作者邀请，使用有写入权限的账号推送。首次克隆：

```sh
git clone https://github.com/zzrdearea/literature-library.git
cd literature-library
```

每次投稿先在仓库内运行 `git pull --rebase origin main`，然后把报告放进对应分类目录（category-01 到 category-05）。例如第三类的新报告放入 `reports/category-03/my-paper/index.html`，配图放在同一篇报告的子目录。按实际文件夹名执行：

```sh
git add -- reports/category-03/my-paper/
git commit -m "新增第三类文献报告"
git push origin main
```

若推送时同伴已更新 main，运行 `git pull --rebase origin main`，处理可能的冲突，再推送。Actions 发布成功后，读者刷新首页即可浏览和检索新报告。

团队确定分类名称后，在 categories.json 修改显示名称即可，目录编号保持固定。页面标题取自 HTML 的 title。更新同一文件保留原链接，删除文件后下次发布会移除目录和索引中的记录。

图表可以内嵌，也可随报告放在独立子目录，用相对路径引用。正文需要写进 HTML；浏览器执行 JavaScript 后才出现的正文请先导出为静态页面。只接受可信成员的网页，按网站可见范围选择报告。搜索覆盖 HTML 正文，PDF 附件内容不进入索引。

## 本地检查

在本目录运行以下命令，然后访问 http://localhost:8000。首次生成索引需要联网安装 Pagefind。

```
python build.py
npx --yes pagefind@1.4.0 --site _site --glob "reports/**/*.html" --force-language zh
python -m http.server 8000 --directory _site
```
