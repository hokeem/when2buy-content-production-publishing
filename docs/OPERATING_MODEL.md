# When2Buy X 内容生产运行手册

## 当前闭环

`Apify采集 → 原文与媒体归档 → 最新优先队列 → 原创文案和实体视觉 → Postiz发布 → 公开URL核验 → 72小时指标 → Report Hub面板`

GitHub 是事实源，Report Hub 是展示层。生成的实时 HTML 不是数据库，也不提交 Git。

## 生产规则

1. 只以 `@WhaleInsider` 和 `@StockMKTNewz` 作为选题入口。
2. 排除置顶、回复、纯转发、推广和重复内容。
3. 按原帖 `postedAt` 从新到旧处理，每轮最多5条；热度只能打破相同时间。
4. 保留事件、主体/Ticker、关键数字、事实顺序和信息密度，只轻微重排语言。
5. 结尾固定为 `When2Buy — your U.S. stock partner.`
6. 公共文案和图片不得出现来源账号、来源链接、`according to`、`reported by`、`Market radar` 或免责声明。
7. 每条使用生图模型生成完整1:1实体场景，再叠加一次准确 Logo。纯文字卡和通用雷达背景不合格。
8. 发布前运行内容标准检查；只有 Postiz 返回 `PUBLISHED` 和公开 X URL 才记录成功。
9. 指标由 Postiz API 优先获取，只记录可归因的真实数值，追踪窗口为发布后72小时。
10. 运行结束验证状态和凭据安全，再提交事实数据、队列、素材与文本摘要。

## 自动任务

| 任务 | 时间 | 是否写状态 | 输出 |
|---|---|---:|---|
| `when2buy-freshness-production` | 每小时 05、25、45 分 | 是，唯一周期写入者 | X内容、状态、内容工厂、数据页 |
| `when2buy-weekly-content-analysis` | 每周一 10:00 | 否 | 只发布周报 |

独立数据任务和稳定面板同步任务已经暂停，禁止与生产任务并发恢复。

## 报告边界

- 内容工厂：`--target content`
- 数据表现：`--target performance`
- 周报：`--target weekly`

三个 target 独立渲染、独立发布。生成 HTML 位于本地 `reports/`，由 `.gitignore` 排除。面板读取 `data/state.json`，图片使用 GitHub 中已提交的素材 URL；Report Hub 不会反向修改 GitHub。

## 凭据与安全

凭据只从受限环境读取。禁止打印、写入状态、报告、HTML或Git。不得用点击结果冒充发布成功，不得在没有公开URL时重复发送。
