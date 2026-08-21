# Scheduled task design

Use a standalone scheduled task so each run starts clean and reports into Scheduled. Keep durable state in Git and `data/state.json`, not a long-lived chat.

## Recommended cadence (Asia/Shanghai)

- 08:30: scan both benchmark accounts from the prior 48 hours, store all new eligible originals, rank up to five, and produce the strongest package.
- 12:30: scan both accounts for posts since the 08:30 run, merge only new status IDs, rerank, and produce the strongest unused topic.
- 18:30: scan both accounts for posts since the 12:30 run, rerank, and produce the strongest unused topic.
- 22:30: scan both accounts once more, produce a catch-up package when an unused high-impact post exists, then refresh metrics and write the daily review.

Every window starts with `@WhaleInsider` and `@StockMKTNewz`. General web search is only for upstream fact verification after a benchmark post has been selected.

## Task prompt

```text
Use $when2buy-content-publisher in this repository. This is a benchmark-first run: open https://x.com/WhaleInsider and https://x.com/StockMKTNewz before searching anywhere else, capture every new eligible original since the previous scan, and use a 48-hour fallback only when there are no new posts. Select the strongest unused benchmark post and make when2buy cover the same event, ticker, key facts, decisive numbers, factual order, and urgency in independently written language and original when2buy visuals. Read the mandatory brand, style, and case references; use the exact bundled logo and compare the image against all three examples. Verify claims upstream, store the package as ready, update data/state.json, run python3 scripts/render_report.py, validate state, and notify the user that one exact browser publishing action is ready for confirmation. Do not substitute a generic finance topic, send DMs, follow accounts, reply to users, import cookies, or claim publication without a verified public URL.
```

Run against the local project when browser access and generated local files are required. Keep the computer on and the desktop app running. Test the task manually before enabling the schedule. After the user confirms a ready package, use a foreground run to publish and verify it.
