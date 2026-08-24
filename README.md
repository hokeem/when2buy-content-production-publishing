# when2buy 内容制作与发布

这是面向 Codex Agent 的 when2buy 美股内容生产与 X 发布系统。它不是旧工作台的网页源码复制，而是可迁移的执行内核：Skill、真实案例、Agent 规则、持久化状态和自动报告。

## 最核心的运行逻辑

这不是一个自由发散的财经选题器。Agent 每天在北京时间 `08:30`、`12:30`、`18:30`、`22:30` 必须首先扫描：

- `https://x.com/WhaleInsider`
- `https://x.com/StockMKTNewz`

它会收集两个账号自上次运行以来的全部合格原创帖，选出最强的尚未覆盖选题，然后让 when2buy 发同一个事件、同一组关键事实和数字、同一时效窗口的内容。文案和画面必须重新创作，不复制对标账号的独特句子或图片。

上游新闻、SEC 文件和公司公告只用于验证事实，不能代替这两个对标账号进行选题。

## 交付内容

- `skills/when2buy-content-publisher/`：新 Codex 可直接调用的核心 Skill，包含流程、浏览器执行规则和案例库。
- `skills/when2buy-content-publisher/assets/`：真实 when2buy Logo 和 Intel、Riot、宏观日历三张风格成品。
- `skills/when2buy-content-publisher/references/brand-and-style.md`：文案语气、结构、禁用写法和配图规则。
- `data/state.json`：选题、制作队列、已发布内容、指标快照和运行日志。
- `reports/latest.md`：Agent 每次运行后自动刷新的人类可读报告，不需要在页面上点击。
- `scripts/`：状态验证、报告生成和安全检查。

## 给新 Codex 的交接语

```text
请在当前仓库使用 $when2buy-content-publisher 执行 full 模式。这是 benchmark-first 任务：必须先打开 @WhaleInsider 和 @StockMKTNewz，收集上次扫描以来的原创帖；只有两个账号都没有新帖时才回溯 48 小时。选一条最强且 when2buy 未覆盖的对标帖，做同一事件、同一关键事实与数字、同一时效窗口的 when2buy 内容，但用独立英文和原创画面表达。制作前必须读取 brand-and-style.md 和 cases.md，使用仓库内的真实 Logo，并对照三张风格成品。完成后更新 data/state.json 和 reports/latest.md。
```

## 生成最新报告

```bash
python3 scripts/render_report.py
```

## Apify 对标采集

唯一采集通道是 Apify Actor `scraper-engine/twitter-x-scraper`。它在一次运行中读取 `@WhaleInsider` 与 `@StockMKTNewz` 的公开 profile timeline，不携带 X Cookie；脚本过滤回复与转帖、以 status ID 去重，并只把可回溯的原创帖写入 `data/state.json`。

```bash
export APIFY_TOKEN='…' # 仅在本机或 GitHub Actions Secret 中配置，绝不提交
python3 scripts/collect_apify_benchmarks.py
python3 scripts/render_report.py
```

GitHub Actions 的 `Apify benchmark radar` 在北京时间 08:30、12:30、18:30、22:30 运行。启用前，在仓库 Actions secrets 中设置 `APIFY_TOKEN`；也可先通过 `workflow_dispatch` 手动验证一轮。采集只发现和持久化对标帖，绝不发布 X 内容。

## 凭据

仓库不保存凭据。X 使用本机已登录的浏览器会话；GitHub 使用 GitHub Connector、`gh auth login` 或系统凭据管理器。永远不要把 PAT 写入 `.env`、Git remote URL 或 Git 历史。
