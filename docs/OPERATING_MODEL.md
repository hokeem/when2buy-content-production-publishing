# when2buy X 内容生产运行手册

## 默认闭环

`Apify 采集 → 原图归档 → 生产队列 → 快速来源披露 → 原创文案/视觉 → Postiz 发布 → 发布核验 → 状态、报告、HTML 面板`

每次运行对每条新捕获的合格对标帖建立一对一原创输出；对标帐号只负责发现与时效，不能复制其措辞或配图。QUICK MARKET RADAR 模式允许以这两个固定来源的已捕获帖子快速发布；独立核验不足时必须改写成带来源归因的 market-radar 或更广泛趋势/背景帖，而不是丢弃，并且不将第三方主张表述为已证实事实。

## 固定输入与输出

| 阶段 | 输入 | 成功输出 | 不通过时 |
|---|---|---|---|
| Radar | Apify、两个固定帐号 | `benchmarkPosts`、`production-queue.json` | 记录 `blocked`，不补造选题 |
| Quick radar | 候选帖、账号与状态 URL | 每条候选都有原创输出、来源捕获、显著未核验披露、无交易建议 | 因运营或交付失败而保留原因；不得仅因未独立核验而丢弃 |
| Produce | 已核验事实、品牌资产 | `packages` 中 `ready` 包、1:1 PNG | 不使用对标原图作成品 |
| Publish | ready 包、Postiz | `PUBLISHED` 和公开 X URL | 保持 `ready`/`failed`，不虚报成功 |
| Review | 已发帖、公开指标 | `metricSnapshots`、结论 | 不改写历史快照 |

## 日常运行

1. `python3 skills/when2buy-content-publisher/scripts/preflight.py`
2. `python3 scripts/collect_apify_benchmarks.py`
3. `python3 scripts/archive_benchmark_media.py`
4. `python3 scripts/build_production_queue.py`
5. QUICK MARKET RADAR：为每条新合格候选保存账号与状态 URL，并制作 `ready` package；以“Market radar — reported by @account; not independently verified.”披露。第三方预测、排名、交易条款、价格和概率必须保持归因，不能写成事实；无法独立核验时改为 market-radar 或更广泛背景角度。
6. 仅在用户已有当前或持续发布授权时执行：`python3 scripts/postiz_publish.py --package-id <id> --confirm`
7. `python3 scripts/render_report.py && python3 scripts/render_run_panel.py`
8. `python3 skills/when2buy-content-publisher/scripts/state.py validate && python3 scripts/security_scan.py`

## 生产不可变规则

- 默认时区为 Asia/Shanghai；自动 Radar 为 08:30、14:30、20:30。
- 只使用 `@WhaleInsider` 与 `@StockMKTNewz` 作为选题入口。
- 使用精确 `when2buy-logo-reference.png`；1:1、黑底/白字、红色为风险或转折、绿色仅为积极上行。
- Postiz 返回 `QUEUE` 不算发布成功；必须轮询到 `PUBLISHED` 且存在 `releaseURL`。
- API 密钥只从环境变量读取，永不写入状态、报告、HTML、Git 或终端摘要。
- QUICK MARKET RADAR 不提供交易建议或保证；它只在两个固定对标账号的来源披露下发布原创市场雷达内容。

## 自动化时钟（Asia/Shanghai）

| 时间 | 执行器 | 职责 |
|---|---|---|
| 08:30、14:30、20:30 | GitHub Actions `Apify benchmark radar` | 采集两位对标帐号、归档原图、重建队列和稳定 HTML 面板，并将状态推回 `main`。 |
| 08:40、14:40、20:40 | Paseo `when2buy-production-publish` | 拉取 `main`；只处理最新且未覆盖的候选；核验、原创制作、Postiz 发布、公开 URL 核验，并推回状态与面板。 |
| 每日 09:05 | Paseo `when2buy-performance-review` | 运行 `scripts/collect_public_metrics.py`；仅在 Postiz 发布后的 72 小时窗口内先读取 Postiz Public API 的每帖 analytics，公开 X URL 仅作 API 失败/空值时的数值后备；窗口结束即标记 `metricsTracking=complete` 且永不再抓取。 |

生产定时任务拥有针对 `@_When2buy` 的 standing 发布授权，但不是无条件发布器。它必须按本手册的 Verify、Produce、Publish 三道门执行；任一门不通过就记录原因、刷新报告并结束。`POSTIZ_API_KEY` 与 `WHEN2BUY_AUTOPUBLISH_ENABLED=true` 只能放在受限运行环境，不能进入仓库或 GitHub Actions 日志。
