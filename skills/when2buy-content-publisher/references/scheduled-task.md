# Scheduled task

Paseo is the only recurring production scheduler. It runs at `5,25,45 * * * *` in `Asia/Shanghai`, so the maximum collection wait is 20 minutes. GitHub Actions remains available for manual recovery and push validation but has no recurring collection schedule.

Every run performs one uninterrupted chain:

1. Fetch/rebase `main`, load credentials without printing them, and run preflight.
2. Collect only `@WhaleInsider` and `@StockMKTNewz` through Apify.
3. Exclude pinned posts, replies, repost-only entries, and duplicates; archive original media.
4. Build the queue and preserve its newest-first order. Never re-sort by heat.
5. Produce up to five newest unproduced packages. Keep the core event and information density; end with exactly `When2Buy — your U.S. stock partner.` Public text and artwork contain no source attribution or disclaimers.
6. Generate a complete entity-led square image with the image-generation model. Add the exact logo afterward and run visual QA. Static typography templates are forbidden.
7. Run `scripts/validate_content_standard.py`, publish through Postiz, and require `PUBLISHED` plus a public X URL.
8. Initialize 72-hour metrics tracking, render the panel, run `python3 scripts/publish_run_panel.py` to update the stable report directly, and push state to `main`. Never run `report list`; registry listing uses separate access control and is not required for a known stable slug.

Process items independently and continue after an item-level failure. A run is successful only when every selected item is either publicly published or has a precise terminal delivery error. Content-review or verification uncertainty is not a terminal blocker.

## Daily Postiz publication metrics (09:05)

Run `python3 scripts/collect_public_metrics.py` once daily. The task operates only on `posts` that were published through Postiz and whose `publishedAt` is no more than 72 hours ago. It first calls `GET /analytics/post/{postizPostId}?date=<1..3>` on the Postiz Public API and maps `Impressions`, `Replies`, `Retweets`, and `Likes` to views/replies/reposts/likes with endpoint and field evidence in each snapshot. The post's public X URL is a secondary fallback only when Postiz is unavailable or returns no usable mapped values; a page that exposes no parseable number creates no observation. Once the 72-hour window ends, it records `posts[].metricsTracking.status = complete`; completed posts are never fetched again. This task does not publish, edit, or delete social content.

Every run stores exact source text, X URL, visible engagement fields, original-media URLs, and artifact paths internally. Existing standing authorization permits Postiz delivery; no interactive confirmation is required.
