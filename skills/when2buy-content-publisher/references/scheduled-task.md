# Scheduled task

All times are Asia/Shanghai (UTC+8). GitHub Actions runs the Apify collection automatically; it never posts to X.

- 08:30: collect both benchmark timelines, archive available original media, and build the source-preserving production queue.
- 14:30: repeat the collection and rerank only uncovered, eligible events.
- 20:30: repeat the collection, refresh the queue, and leave the strongest verified candidate ready for the next production pass.

## Daily Postiz publication metrics (09:05)

Run `python3 scripts/collect_public_metrics.py` once daily. The task operates only on `posts` that were published through Postiz and whose `publishedAt` is no more than 72 hours ago. It first calls `GET /analytics/post/{postizPostId}?date=<1..3>` on the Postiz Public API and maps `Impressions`, `Replies`, `Retweets`, and `Likes` to views/replies/reposts/likes with endpoint and field evidence in each snapshot. The post's public X URL is a secondary fallback only when Postiz is unavailable or returns no usable mapped values; a page that exposes no parseable number creates no observation. Once the 72-hour window ends, it records `posts[].metricsTracking.status = complete`; completed posts are never fetched again. This task does not publish, edit, or delete social content.

Every run stores exact source text, X URL, visible engagement fields when provided, remote original-media URLs, and artifact paths. An agent must independently verify material facts, write an original when2buy post, and create an original branded visual before a package becomes `ready`. Publishing still needs action-time confirmation.
