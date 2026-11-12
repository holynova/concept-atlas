# 概念探险队 / Concept Atlas

用121张清晰线描漫画解释那些字都认识、机制却难懂的概念。覆盖体育、摄影、金融、物理、交通、自然、居家、影音与生活；每张一个概念，3:4竖版，支持分类搜索、放大阅读、文案复制与原图打包下载。

121 illustrated explainers for familiar words with unfamiliar mechanics. A responsive gallery with category filters, search, full-resolution reading, source references and PNG downloads.

![网站预览](./assets/screenshot.png)

- [Cloudflare Demo](https://xiaosang.cc/concept-atlas/)
- [GitHub Repo](https://github.com/holynova/concept-atlas)

<img src="./assets/qr.png" width="180" alt="扫码浏览概念图鉴">

## 本地运行 / Run locally

```sh
npm run dev
```

## 构建与发布 / Build and deploy

```sh
npm run build
npm run stage:portfolio
# 在 holynova.github.io/master 提交并推送 concept-atlas/ 产物
npm run deploy:check
npm run deploy
```

Version 1.2.0 · `main` · Cloudflare Workers Static Assets。源码和部署配置在同一主分支，本地手动发布。`source/manifest-*.json` 保存文案、来源和内置 ImageGen 制作提示词。`source/publication.json` 记录暂时从公开画廊收起的工程化主题；原图与资料仍保存在仓库。图片保留原始PNG，列表与阅读使用独立WebP衍生图。

Worker 配额已满，项目复用现有 `xiaosang-portfolio` Worker 的 `/concept-atlas/` 路径。`stage:portfolio` 将产物复制至相邻作品集仓库，部署前须提交作品集 master。项目与作品集共用一次手动 Cloudflare 部署。
