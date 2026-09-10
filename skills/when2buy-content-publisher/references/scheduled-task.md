# Scheduled task

Paseo owns recurring production. GitHub Actions is manual recovery and CI only; it has no recurring content schedule.

## Ownership model

GitHub is the canonical store for source data, delivery state, code, and media. Report Hub is presentation-only and is rebuilt from `data/state.json`; nothing reads data back from Report Hub.

## Unified production schedule

The only state-writing recurring task runs every 15 minutes at `0,15,30,45 * * * *` in `Asia/Shanghai`. The 15-minute cadence is also the minimum account-level gap between accepted X submissions, so one slow publication cannot create a burst in the following cycle.

Every run:

1. Fetch `main`, load protected credentials without printing them, and validate state/preflight. Do not dump the full state file or entire repository listing into agent context.
2. Run `python3 scripts/reconcile_postiz_publications.py --lookback-hours 72` before any new delivery. An accepted Postiz task stays `publishing` during its 60-minute delayed-success grace period, including when Postiz temporarily reports `ERROR`. Never submit it again.
3. On the first run of each hour, collect public metrics idempotently for posts published during their first 72 hours.
4. Collect only `@WhaleInsider` and `@StockMKTNewz` through Apify. Exclude pinned posts, replies, repost-only entries, promotions, duplicates, and expired items; archive original media.
5. Build the hard-90-minute-TTL queue. Process at most one newest fresh item per run. Never revive or publish backlog.
6. Produce concise original copy and one complete entity-led square generated image, then composite the exact repository logo once.
7. Publish through `scripts/postiz_publish_batch.py`. The hard account-level limits are one accepted submission every 15 minutes, no more than four in a rolling hour, and no more than twenty in a rolling 24 hours. A `deferred` or `pending_reconciliation` result is a successful safety outcome, not a reason to retry.
8. Count publication only after reconciliation obtains `PUBLISHED` and a public `x.com` URL. A persistent `ERROR` becomes terminal only after the 60-minute grace window.
9. Validate state/security, render reports, commit canonical files, push `HEAD:main`, verify the remote commit, and update the fixed content and performance report slugs.

The task must finish within its 15-minute slot. External commands use bounded timeouts. If image generation or an API call cannot finish safely, persist the current state and exit; the next run resumes through state rather than keeping an agent alive indefinitely.

## Weekly analysis schedule

Every Monday at 10:00 Asia/Shanghai, a separate read-only task publishes only the weekly report. It does not collect content, publish social posts, modify state, or write generated HTML to Git.

## Retired schedules

The standalone daily performance and stable report-sync tasks stay paused. Their responsibilities belong to the unified production task.
