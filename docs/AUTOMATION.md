# when2buy 自动运行说明

本仓库的自动化由三段相互解耦的时钟组成，统一使用 `Asia/Shanghai`：

1. **Radar（GitHub Actions，08:30 / 14:30 / 20:30）**：从 `@WhaleInsider`、`@StockMKTNewz` 拉取公开原创帖，保存原文、链接、互动数据与原始媒体归档；重建 `data/production-queue.json`、`reports/latest.md` 和唯一的 `reports/run-panel.html`。
2. **Production + publish（Paseo，08:40 / 14:40 / 20:40）**：等待 Radar 的状态已在 `main` 后执行。每条新捕获的合格来源帖都必须生成一对一的原创英文文案和 when2buy 原创方图；独立核验不足时改写为带来源归因的 market-radar 或更广泛的趋势/背景帖，而不是丢弃选题。通过 `scripts/postiz_publish.py` 发布到 `@_When2buy`，并轮询到公开 X URL。
3. **Performance review（Paseo，每日 09:05）**：执行 `python3 scripts/collect_public_metrics.py`，只对发布后 72 小时窗口内的 Postiz 已发布内容追加每日公开指标快照；主数据源是 Postiz Public API 的每帖 analytics，公开 X 页面仅在 API 不可用或未返回可映射指标时作为后备。不发布内容，也不修改旧快照。窗口结束后写入 `metricsTracking.status=complete`，此后永不再请求该帖子。

## 运行环境

- GitHub Actions 只需要仓库 Secret `APIFY_TOKEN`。
- Paseo 的生产任务只从受限运行环境读取 `POSTIZ_API_KEY`、`POSTIZ_BASE_URL`、`WHEN2BUY_POSTIZ_HANDLE` 和 `WHEN2BUY_AUTOPUBLISH_ENABLED=true`。这些变量绝不写入 Git、报告或终端输出。
- 稳定面板使用既有的 report-hub 目标更新；它没有创建新公开 URL 的权限。

## QUICK MARKET RADAR 模式

- 仅使用 `@WhaleInsider` 与 `@StockMKTNewz` 的已归档原创帖作为快速雷达来源；保留来源账号、状态 URL、原文和媒体归档。
- 不要求在发布前完成独立事实核验，但成文必须明确标注：`Market radar — reported by @account; not independently verified.`
- 所有第三方的预测、排名、交易条款、价格、概率、目标或指控都必须以“reported by @account”归因表达，不能写成已证实事实。
- 不提供交易推荐、买卖指令、收益承诺或确定性结论；仍必须使用原创文案和原创配图。
- 面板只显示已有 when2buy package（`ready` 或后续状态）的来源→输出行；无输出的 crawl-only 来源仍完整保留在 `data/state.json`，但不作为空白行展示。

## 发布数据追踪

- `data/state.json` 的 `metricSnapshots` 是唯一指标来源；快照只追加，绝不覆盖历史观测。
- `posts[].metricsTracking` 保存 `windowStart`、`windowEnd`、`status`、`lastAttemptAt` 与完成原因；唯一允许的状态流转是 `active → complete`。`complete` 帖子绝不再次抓取。
- 每个已发布内容在同一条“来源 → 输出 → 确认发布”日表行的 `24h data` 单元格显示公开 X URL、最新可得 views/replies/reposts/likes、最后检查时间、发布后首 24 小时内按时间顺序记录的快照，以及可展开的完整快照历史和 72h 状态。
- 当公开页面没有显示某个计数，或没有在首 24 小时采集到快照时，面板必须显示 `—` 或明确的“未采集”提示，而不是推算值。
- 主抓取器请求 `GET /analytics/post/{posts[].postizPostId}?date=<1..3>`；Postiz 标签 `Impressions`、`Replies`、`Retweets`、`Likes` 分别映射为 views/replies/reposts/likes，并把 endpoint、查询天数、原始标签和 analytics 日期写入 `metricSnapshots[].evidence`。仅当 Postiz 失败或无可用映射值时才请求 `posts[].url` 的公开 X 状态页；若页面没有可解析的数值，记录本次尝试但**不**追加指标快照。

## 可恢复性

- GitHub Actions 失败：在 Actions 中重跑 `Apify benchmark radar`，不应手工编辑 state。
- Production 失败：下一个时间窗会读取同一队列；任何未完成 package 必须保留为 `ready` 或 `failed` 并带原因，避免重复发布。
- 发布状态不明：不得再次发送；先用 `scripts/postiz_publish.py` 的 Postiz 查询结果和公开 URL 确认。
- 面板失败：重新运行 `python3 scripts/render_report.py && python3 scripts/render_run_panel.py`，再同步既有 report-hub URL。

每项任务开始都要 `git fetch origin main && git rebase origin/main`；提交时只能暂存本流程拥有的 `data/`、`deliverables/`、`reports/` 文件，禁止覆盖其他工作。
