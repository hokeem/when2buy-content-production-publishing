# 新 Agent 交接卡

从仓库根目录开始。先读 `AGENTS.md`、`README.md`、`skills/when2buy-content-publisher/SKILL.md`，然后读 `data/state.json`。

## 允许自动做的事

- 使用 Apify 采集两个对标帐号、下载对标原图、构建候选队列。
- 查找并引用一级来源核验事实。
- 生成原创 when2buy 文案、原创视觉、报告和本地 HTML 面板。
- 在任务中含有当前或 standing 发布授权，且 `POSTIZ_API_KEY` 存在时，通过 Postiz 发布。

## 发布前必查

1. `package.status == ready`。
2. package 有 benchmark status URL、`mirroredFacts`、至少一个核验来源、真实图片路径。
3. Postiz integration 的 profile 必须是 `@_When2buy`。
4. 发布后必须获得 `PUBLISHED` + X `releaseURL`；否则不能写为 published。

## 交付格式

返回：对标链接、核验来源、文案、图片路径、X 发布链接/阻断原因、报告路径、HTML 面板路径。
