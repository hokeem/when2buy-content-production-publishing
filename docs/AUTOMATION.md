# when2buy 自动运行说明

本仓库的自动化由三段相互解耦的时钟组成，统一使用 `Asia/Shanghai`：

1. **Radar（GitHub Actions，08:30 / 14:30 / 20:30）**：从 `@WhaleInsider`、`@StockMKTNewz` 拉取公开原创帖，保存原文、链接、互动数据与原始媒体归档；重建 `data/production-queue.json`、`reports/latest.md` 和唯一的 `reports/run-panel.html`。
2. **Production + publish（Paseo，08:40 / 14:40 / 20:40）**：等待 Radar 的状态已在 `main` 后执行。默认的 QUICK MARKET RADAR 模式从两个固定对标账号中选择最新未覆盖的候选，在保存来源账号、原帖 URL 和原始媒体后，生成全新英文文案和 when2buy 原创方图；通过 `scripts/postiz_publish.py` 发布到 `@_When2buy`，并轮询到公开 X URL。
3. **Performance review（Paseo，每日 09:05）**：执行 `python3 scripts/collect_public_metrics.py`，只对发布后 72 小时窗口内的 Postiz 已发布内容追加每日公开指标快照；不发布内容，也不修改旧快照。窗口结束后写入 `metricsTracking.status=complete`，此后永不再请求该帖子。

## 运行环境

- GitHub Actions 只需要仓库 Secret `APIFY_TOKEN`。
- Paseo 的生产任务只从受限运行环境读取 `POSTIZ_API_KEY`、`POSTIZ_BASE_URL`、`WHEN2BUY_POSTIZ_HANDLE` 和 `WHEN2BUY_AUTOPUBLISH_ENABLED=true`。这些变量绝不写入 Git、报告或终端输出。
- 稳定面板使用既有的 report-hub 目标更新；它没有创建新公开 URL 的权限。

## QUICK MARKET RADAR 模式

- 仅使用 `@WhaleInsider` 与 `@StockMKTNewz` 的已归档原创帖作为快速雷达来源；保留来源账号、状态 URL、原文和媒体归档。
- 不要求在发布前完成独立事实核验，但成文必须明确标注：`Market radar — reported by @account; not independently verified.`
- 所有第三方的预测、排名、交易条款、价格、概率、目标或指控都必须以“reported by @account”归因表达，不能写成已证实事实。
- 不提供交易推荐、买卖指令、收益承诺或确定性结论；仍必须使用原创文案和原创配图。

## 发布数据追踪

- `data/state.json` 的 `metricSnapshots` 是唯一指标来源；快照只追加，绝不覆盖历史观测。
- `posts[].metricsTracking` 保存 `windowStart`、`windowEnd`、`status`、`lastAttemptAt` 与完成原因；唯一允许的状态流转是 `active → complete`。`complete` 帖子绝不再次抓取。
- 每个已发布内容在 `reports/run-panel.html` 显示公开 X URL、最新可得 views/replies/reposts/likes、最后检查时间、发布后首 24 小时内按时间顺序记录的快照，以及可展开的完整快照历史。
- 当公开页面没有显示某个计数，或没有在首 24 小时采集到快照时，面板必须显示 `—` 或明确的“未采集”提示，而不是推算值。
- 抓取器只请求 `posts[].url` 指向的公开 X 状态页；每个 `metricSnapshots` 记录该 URL、检查时间与页面结果，确保每个数值可归因。

## 可恢复性

- GitHub Actions 失败：在 Actions 中重跑 `Apify benchmark radar`，不应手工编辑 state。
- Production 失败：下一个时间窗会读取同一队列；任何未完成 package 必须保留为 `ready` 或 `failed` 并带原因，避免重复发布。
- 发布状态不明：不得再次发送；先用 `scripts/postiz_publish.py` 的 Postiz 查询结果和公开 URL 确认。
- 面板失败：重新运行 `python3 scripts/render_report.py && python3 scripts/render_run_panel.py`，再同步既有 report-hub URL。

每项任务开始都要 `git fetch origin main && git rebase origin/main`；提交时只能暂存本流程拥有的 `data/`、`deliverables/`、`reports/` 文件，禁止覆盖其他工作。
