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

## Candidate score

Score each dimension from 0 to 5:

- Freshness: minutes matter for breaking news; hours for earnings; days for analysis.
- Market impact: index weight, dollar scale, policy scope, or cross-asset relevance.
- Factual clarity: named primary source and independently checkable numbers.
- Visual potential: one dominant number, comparison, timeline, or contradiction.
- when2buy fit: U.S. equities, macro, earnings, chips, AI infrastructure, or major capital flows.
- Duplication risk: subtract 0 to 5 when the account recently covered the same angle.

Rank by total score. If two candidates tie, choose the fresher primary-source event.

Each recommendation must map one-to-one to one captured benchmark post. Never combine two unrelated benchmark posts into a synthetic topic.

## Copy system

Write in English unless the task says otherwise. Default to 45-90 words and four short blocks:

1. Lead with the company/ticker and the verified event.
2. State the decisive number or contrast.
3. Explain the investor implication in plain language.
4. End with one sharp observation or question only when it adds value.

Use cashtags when natural. Avoid generic openings, long throat-clearing, hashtags stuffed at the end, guaranteed-return language, and the fixed slogan `This is when2buy, your AI stock friend` unless explicitly requested.

Benchmarking may preserve public facts, tickers, numbers, and short official labels. Rewrite all narration independently. Never lightly paraphrase a top reply or reproduce another creator's punchline.

## Visual system

- Canvas: 1:1, high contrast, optimized for a phone feed.
- Branding: use the supplied circular when2buy logo once, with clear space.
- Hierarchy: one dominant fact, one short supporting line, one relevant company or market visual.
- Text: no paragraph blocks; proofread every visible number and date.
- Style: black or near-black base, white type, red/green accents only where semantically correct.
- Provenance: keep source links in state even when they are not printed on the image.

## Experiments and review

Change one major variable per experiment: hook, visual hierarchy, post length, publishing window, or CTA. Capture impressions, likes, replies, reposts, and bookmarks when visible at 1h, 6h, 24h, and 72h. Compare medians, not a single viral outlier.

For each review, record evidence, conclusion, next change, minimum sample size, and rollback condition. Do not claim causality when topic importance or account distribution could explain the result.
