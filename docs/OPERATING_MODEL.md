# when2buy X 内容生产运行手册

## 默认闭环

`Apify 采集 → 原图归档 → 生产队列 → 事实核验 → 原创文案/视觉 → Postiz 发布 → 发布核验 → 状态、报告、HTML 面板`

每次运行只选一个与一条对标帖一对一映射的事件；对标帐号只负责发现与时效，不能作为最终事实来源，也不能复制其措辞或配图。

## 固定输入与输出

| 阶段 | 输入 | 成功输出 | 不通过时 |
|---|---|---|---|
| Radar | Apify、两个固定帐号 | `benchmarkPosts`、`production-queue.json` | 记录 `blocked`，不补造选题 |
| Verify | 候选帖、一级来源 | 可核验事实与来源 URL | 终止该候选 |
| Produce | 已核验事实、品牌资产 | `packages` 中 `ready` 包、1:1 PNG | 不使用对标原图作成品 |
| Publish | ready 包、Postiz | `PUBLISHED` 和公开 X URL | 保持 `ready`/`failed`，不虚报成功 |
| Review | 已发帖、公开指标 | `metricSnapshots`、结论 | 不改写历史快照 |

## 日常运行

1. `python3 skills/when2buy-content-publisher/scripts/preflight.py`
2. `python3 scripts/collect_apify_benchmarks.py`
3. `python3 scripts/archive_benchmark_media.py`
4. `python3 scripts/build_production_queue.py`
5. Agent 核验最强候选，制作 `ready` package。
6. 仅在用户已有当前或持续发布授权时执行：`python3 scripts/postiz_publish.py --package-id <id> --confirm`
7. `python3 scripts/render_report.py && python3 scripts/render_run_panel.py`
8. `python3 skills/when2buy-content-publisher/scripts/state.py validate && python3 scripts/security_scan.py`

## 生产不可变规则

- 默认时区为 Asia/Shanghai；自动 Radar 为 08:30、14:30、20:30。
- 只使用 `@WhaleInsider` 与 `@StockMKTNewz` 作为选题入口。
- 使用精确 `when2buy-logo-reference.png`；1:1、黑底/白字、红色为风险或转折、绿色仅为积极上行。
- Postiz 返回 `QUEUE` 不算发布成功；必须轮询到 `PUBLISHED` 且存在 `releaseURL`。
- API 密钥只从环境变量读取，永不写入状态、报告、HTML、Git 或终端摘要。

## 自动化时钟（Asia/Shanghai）

| 时间 | 执行器 | 职责 |
|---|---|---|
| 08:30、14:30、20:30 | GitHub Actions `Apify benchmark radar` | 采集两位对标帐号、归档原图、重建队列和稳定 HTML 面板，并将状态推回 `main`。 |
| 08:40、14:40、20:40 | Paseo `when2buy-production-publish` | 拉取 `main`；只处理最新且未覆盖的候选；核验、原创制作、Postiz 发布、公开 URL 核验，并推回状态与面板。 |
| 次日 09:05 | Paseo `when2buy-performance-review` | 为已发布内容补充可获取的公开指标和复盘结论；只追加快照，绝不重写历史。 |

生产定时任务拥有针对 `@_When2buy` 的 standing 发布授权，但不是无条件发布器。它必须按本手册的 Verify、Produce、Publish 三道门执行；任一门不通过就记录原因、刷新报告并结束。`POSTIZ_API_KEY` 与 `WHEN2BUY_AUTOPUBLISH_ENABLED=true` 只能放在受限运行环境，不能进入仓库或 GitHub Actions 日志。
