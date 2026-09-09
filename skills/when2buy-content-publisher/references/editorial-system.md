# Editorial system

## Radar inputs

Monitor the newest original public posts from `@WhaleInsider` and `@StockMKTNewz` before using any other discovery source. The selected benchmark post determines the when2buy topic; upstream research only verifies and enriches its factual payload. Prefer:

1. SEC filings and company investor-relations releases.
2. Federal Reserve, BLS, BEA, Treasury, CFTC, exchanges, and other official data.
3. Reuters, AP, Bloomberg, FT, WSJ, CNBC, and established trade publications.
4. Benchmark X posts only as discovery and timing evidence.

Do not treat engagement counts as factual verification.

For each captured benchmark post, store:

- exact X status ID and URL;
- benchmark account and visible publication time;
- visible text and media type;
- company/ticker, event type, key numbers, and factual order;
- whether when2buy has already covered the same event;
- upstream sources used for verification.

## Publication order

Sort eligible non-pinned benchmark posts strictly by `postedAt`, newest first. Engagement breaks a tie only when two source timestamps are identical. Market impact, factual clarity, visual potential, and when2buy fit may guide presentation, but they never promote an older post over a newer eligible post.

Each recommendation must map one-to-one to one captured benchmark post. Never combine two unrelated benchmark posts into a synthetic topic.

## Copy system

Write in English unless the task says otherwise. Preserve the benchmark post's factual payload and approximate information density:

1. Lead with the named subject and core event.
2. Preserve the decisive number or second fact when the source includes one.
3. Reorder wording lightly without adding analysis or commentary.
4. End immediately after the factual payload; do not append the retired When2Buy partner line, a replacement fixed tagline, or a CTA.

Use cashtags when natural. Do not print the benchmark handle, source URL, sourcing language, a verification disclaimer, investment-advice boilerplate, hashtags, or another CTA. Benchmarking may preserve public facts, tickers, numbers, and short official labels, but must not copy distinctive narration, jokes, or punchlines.

## Visual system

- Canvas: 1:1, high contrast, optimized for a phone feed.
- Branding: use the supplied circular when2buy logo once, with clear space.
- Hierarchy: one dominant fact, one short supporting line, one relevant company or market visual.
- Text: no paragraph blocks; proofread every visible number and date.
- Style: black or near-black base, white type, red/green accents only where semantically correct.
- Provenance: keep source links in state even when they are not printed on the image.

## Experiments and review

Change one major variable per experiment: hook, visual hierarchy, post length, publishing window, or CTA. Capture only publicly visible, attributable views, likes, replies, and reposts while a post is within its first 72 hours; append each observation and stop all collection after the 72-hour window. Compare medians, not a single viral outlier.

For each review, record evidence, conclusion, next change, minimum sample size, and rollback condition. Do not claim causality when topic importance or account distribution could explain the result.
