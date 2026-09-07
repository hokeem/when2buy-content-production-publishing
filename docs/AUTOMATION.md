# When2Buy 自动运行说明

## 唯一事实源

GitHub 只保存可以长期审计和恢复的事实：

- `data/state.json`：采集、制作、发布和指标快照
- `data/production-queue.json`：最新优先的生产队列
- `deliverables/`：原始媒体和最终内容素材
- `scripts/`、`skills/`：生成与发布逻辑
- `reports/latest.md`：文本运行摘要

Report Hub 只负责展示。内容工厂、数据表现页和周报 HTML 都是从上述事实现场生成的本地构建产物，不提交 Git，也不会从 Report Hub 反向写回 GitHub。

数据流是单向的：

`Apify / Postiz → GitHub 状态与素材 → HTML 渲染 → Report Hub`

## 两个长期任务

### 1. 统一生产任务

- Paseo ID：`f6640382`
- Cron：`5,25,45 * * * *`
- 时区：`Asia/Shanghai`
- 职责：指标到期检查、Apify 采集、制作最多5条、Postiz 发布、状态提交、内容工厂与数据页发布。
- 所有会修改 `data/state.json` 的周期性行为都归这个任务所有。

指标采集只在北京时间 09 点这一小时执行。成功快照具有每日幂等性，帖子只在发布后的72小时窗口内追踪。

### 2. 每周分析任务

- Paseo ID：`4b6ffef9`
- Cron：`0 10 * * 1`
- 时区：`Asia/Shanghai`
- 职责：只读最近7天状态，生成并发布周报。
- 使用独立工作树，不修改状态、不发布社交内容、不提交生成 HTML。

## 已暂停的重复任务

- `cc20e138 when2buy-performance-review`
- `822f21f3 when2buy-stable-report-sync`

两者原先都会重新生成、提交和发布面板，与生产任务重合，并且可能同时修改同一工作树。现在不再运行。

## 报告发布命令

```bash
python3 scripts/publish_run_panel.py --target content
python3 scripts/publish_run_panel.py --target performance
python3 scripts/publish_run_panel.py --target weekly
```

每个命令只修改自己的固定 Report Hub 页面，不顺带刷新其他页面。

## 恢复规则

- 生产失败：下一轮读取相同状态继续，已成功取得公开 X URL 的帖子不得重发。
- 指标失败：不得写入全空快照；下一次北京时间09点窗口重试。
- 面板失败：从 GitHub 状态重新渲染对应 target，再更新原固定 slug。
- Git 冲突：以远端新增记录为基础合并，不得覆盖或回滚已发布状态。
- 凭据只来自受限运行环境，禁止进入 Git、HTML、日志或对话。
