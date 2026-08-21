# when2buy 内容制作与发布

这是面向 Codex Agent 的 when2buy 美股内容生产与 X 发布系统。它不是旧工作台的网页源码复制，而是可迁移的执行内核：Skill、真实案例、Agent 规则、持久化状态和自动报告。

## 交付内容

- `skills/when2buy-content-publisher/`：新 Codex 可直接调用的核心 Skill，包含流程、浏览器执行规则和案例库。
- `data/state.json`：选题、制作队列、已发布内容、指标快照和运行日志。
- `reports/latest.md`：Agent 每次运行后自动刷新的人类可读报告，不需要在页面上点击。
- `scripts/`：状态验证、报告生成和安全检查。

## 给新 Codex 的交接语

```text
请在当前仓库使用 $when2buy-content-publisher，先运行状态校验，然后按 full 模式执行 when2buy 今日内容流程。使用已登录的 X 浏览器会话直接发布，发布后验证公开 URL，更新 data/state.json 并运行 python3 scripts/render_report.py。不要发私信，不要导入或保存 Cookie，不要复制其他博主的独特文案。
```

## 生成最新报告

```bash
python3 scripts/render_report.py
```

## 凭据

仓库不保存凭据。X 使用本机已登录的浏览器会话；GitHub 使用 GitHub Connector、`gh auth login` 或系统凭据管理器。永远不要把 PAT 写入 `.env`、Git remote URL 或 Git 历史。
