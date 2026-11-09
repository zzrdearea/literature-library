# 课题组协作资料库

[打开小组工作台](https://zzrdearea.github.io/literature-library/)

## 成员投稿

接受仓库协作者邀请后，首次运行：

```sh
git clone https://github.com/zzrdearea/literature-library.git
cd literature-library
```

每次开始前执行 `git pull --rebase origin main`。个人分享可直接放入分类目录，支持 HTML、DOCX、SVG、PDF。例如推荐算法对应 reports/category-05/。

共同任务在分类目录下新建文件夹。复制以下内容到该文件夹的 README.md，填写真实信息。即使只有进度、还没有文件，也可以提交。

```markdown
# 工作名称

参与人：成员甲、成员乙
状态：进行中
当前进度：已完成哪些工作，下一步准备做什么。

## 进展记录
- 日期，成员：本次完成的工作。
```

把工作材料放在 README.md 旁或子目录。HTML 直接在线阅读，SVG 和 DOCX 有预览及原文件链接，其他工作附件按文件链接展示。配图和辅助文件放进 figures/、images/ 或 assets/。状态通常填写「进行中」「已完成」或「待更新」。更新时追加进展记录，按需要修改当前进度。

例如在仓库根目录提交推荐算法分类中的项目：

```sh
git add -- reports/category-05/项目简称/
git commit -m "更新项目进度与材料"
git push origin main
```

推送冲突时先同步远端再重试。网站按对应任务目录最后一次 Git 提交排序。工作名称、参与人、文件名可检索，成员、类别与状态可组合筛选。所有提交到此公开库的材料和进度都公开可读。

## 部署与本地预览

在 Settings → Pages 选择 GitHub Actions。推送 main 后自动构建并发布。本地运行：

```sh
python build.py
python -m http.server 8000 --directory _site
```

打开 http://localhost:8000 。大类名称由团队在 categories.json 配置。
