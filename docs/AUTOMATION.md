# when2buy 自动运行说明

本仓库的自动化由三段相互解耦的时钟组成，统一使用 `Asia/Shanghai`：

1. **Radar（GitHub Actions，08:30 / 14:30 / 20:30）**：从 `@WhaleInsider`、`@StockMKTNewz` 拉取公开原创帖，保存原文、链接、互动数据与原始媒体归档；重建 `data/production-queue.json`、`reports/latest.md` 和唯一的 `reports/run-panel.html`。
2. **Production + publish（Paseo，08:40 / 14:40 / 20:40）**：等待 Radar 的状态已在 `main` 后执行。它只选一条新且强的候选，必须用一级来源核验，生成全新英文文案和 when2buy 原创方图；通过 `scripts/postiz_publish.py` 发布到 `@_When2buy`，并轮询到公开 X URL。
3. **Performance review（Paseo，次日 09:05）**：只给成熟的已发帖追加新的指标快照与可行动结论，不发布内容，也不修改旧快照。

## 运行环境

- GitHub Actions 只需要仓库 Secret `APIFY_TOKEN`。
- Paseo 的生产任务只从受限运行环境读取 `POSTIZ_API_KEY`、`POSTIZ_BASE_URL`、`WHEN2BUY_POSTIZ_HANDLE` 和 `WHEN2BUY_AUTOPUBLISH_ENABLED=true`。这些变量绝不写入 Git、报告或终端输出。
- 稳定面板使用既有的 report-hub 目标更新；它没有创建新公开 URL 的权限。

## 可恢复性

- GitHub Actions 失败：在 Actions 中重跑 `Apify benchmark radar`，不应手工编辑 state。
- Production 失败：下一个时间窗会读取同一队列；任何未完成 package 必须保留为 `ready` 或 `failed` 并带原因，避免重复发布。
- 发布状态不明：不得再次发送；先用 `scripts/postiz_publish.py` 的 Postiz 查询结果和公开 URL 确认。
- 面板失败：重新运行 `python3 scripts/render_report.py && python3 scripts/render_run_panel.py`，再同步既有 report-hub URL。

每项任务开始都要 `git fetch origin main && git rebase origin/main`；提交时只能暂存本流程拥有的 `data/`、`deliverables/`、`reports/` 文件，禁止覆盖其他工作。
