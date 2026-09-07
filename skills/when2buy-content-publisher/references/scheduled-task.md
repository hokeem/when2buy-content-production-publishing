# Scheduled task

Paseo owns recurring production. GitHub Actions is manual recovery and CI only; it has no recurring content schedule.

## Ownership model

GitHub is the canonical store for source data, delivery state, code, and media:

- `data/state.json`
- `data/production-queue.json`
- `deliverables/`
- renderer and workflow code

Report Hub is the canonical presentation layer. The live generated files below are local build artifacts and are not committed to Git:

- `reports/run-panel.html`
- `reports/metrics-dashboard.html`
- `reports/weekly/*.html`

A report is always rebuilt from GitHub-backed state and then published to its fixed Report Hub slug. Nothing reads data back from Report Hub.

## Unified production schedule

The only state-writing recurring task runs at `5,25,45 * * * *` in `Asia/Shanghai`.

Every run:

1. Fetch/rebase `main`, load protected credentials without printing them, and validate state/preflight.
2. On the third benchmark scan of each hour (the `:45` run), run `python3 scripts/collect_public_metrics.py`. The collector is idempotent within each UTC hour and only queries posts published during their first 72 hours; it never performs a full-history metrics crawl.
3. Collect only `@WhaleInsider` and `@StockMKTNewz` through Apify.
4. Exclude pinned posts, replies, repost-only entries, promotions, and duplicates; archive original media.
5. Preserve newest-first queue order and process up to five unpublished items.
6. Produce concise original copy and a complete entity-led generated square image; add the exact logo once and run QA.
7. Validate and publish through Postiz. Require `PUBLISHED` and a public X URL.
8. Validate state/security and commit only canonical data, media, packages, and `reports/latest.md`.
9. Render and publish the content and performance surfaces explicitly:
   - `python3 scripts/publish_run_panel.py --target content`
   - `python3 scripts/publish_run_panel.py --target performance`

This task is the sole recurring writer of `data/state.json`, preventing concurrent state and Git conflicts.

## Weekly analysis schedule

Every Monday at 10:00 Asia/Shanghai, a separate read-only worktree renders and publishes only the weekly surface:

`python3 scripts/publish_run_panel.py --target weekly`

It does not collect data, publish social content, modify state, or push generated HTML to Git. The report covers the latest seven calendar days versus the preceding seven, Top 10 by latest attributable views, observable strengths, topic/time-window medians, coverage, and next actions. Missing metrics are never invented.

## Retired schedules

The standalone daily performance task and stable report-sync task are paused. Their responsibilities are now owned by the unified production task. Do not re-enable them unless the ownership model changes.
