---
name: when2buy-content-publisher
description: "Run the freshness-first when2buy U.S.-market X workflow end to end. Every 15 minutes, inspect new original posts from @WhaleInsider and @StockMKTNewz, process the newest eligible non-pinned post, create concise when2buy English copy and an entity-led generated image, publish safely through Postiz, collect metrics, and update the report."
---

# when2buy Content Publisher

Operate from the repository root. Treat `data/state.json` as the durable handoff between agents.

## Non-negotiable operating model

1. Begin every `radar`, `produce`, or `full` run with both exact feeds: `@WhaleInsider` and `@StockMKTNewz`.
2. Capture every new original since the previous successful scan. Exclude pinned posts, replies, repost-only entries, and promotions.
3. Apply a hard 90-minute source TTL. If neither account has a new eligible post in that window, finish successfully without publishing. Never backfill.
4. Cover the same event, company/ticker, decisive numbers, and urgency as the selected benchmark. Use original When2Buy wording and artwork.
5. Keep source provenance internally. Every package requires `benchmarkPostId`, benchmark URL, and mirrored facts.

## Scheduled fast-follow mode

The canonical Paseo task runs at minute `00,15,30,45` of every hour in Asia/Shanghai. Process at most one newest eligible post per run.

Before every submission, reconcile existing Postiz tasks. Postiz acceptance is not publication: persist the accepted task immediately as `publishing`, then reconcile it until `PUBLISHED` plus a public X URL. A temporary `ERROR` remains pending during the 60-minute delayed-success grace period. Never retry an accepted task.

Enforce the account-level safety limits in [postiz-delivery-policy.md](references/postiz-delivery-policy.md): at least 15 minutes between accepted submissions, no more than four per rolling hour, no more than twenty per rolling 24 hours, and one per scheduled cycle.

## Run modes and required references

- `radar`: capture and rank fresh sources.
- `produce`: create a complete text-and-image package.
- `publish`: safely submit or reconcile one ready package.
- `metrics`: refresh public metrics.
- `review`: record an evidence-backed experiment.
- `full`: run the complete freshness-first cycle.

For radar, produce, or full runs, read `editorial-system.md`, `brand-and-style.md`, and `cases.md`. For publishing or metrics, also read `browser-execution.md`, `data-contract.md`, and `postiz-delivery-policy.md`. For recurring execution, read `scheduled-task.md`.

## Core workflow

1. Run preflight and state validation. Read targeted state summaries; never dump the full state file or repository listing into the agent context.
2. Scan both benchmark feeds through Apify and append new originals with exact URL, timestamp, text, account, and media provenance.
3. Run `scripts/reconcile_postiz_publications.py --lookback-hours 72`, then build the hard-TTL queue.
4. Process only the first item. Recheck source age before image generation and immediately before Postiz submission.
5. Preserve the source event, entity/ticker, decisive number, factual order, urgency, and information density. End after the facts. Do not add a fixed tagline, attribution, source handle/URL, disclaimer, commentary, or CTA.
6. Generate one complete 1:1 entity-led visual; reject pure-text or generic cards. Composite the exact repository logo once and save prompt/QA metadata.
7. Validate content, then invoke `scripts/postiz_publish_batch.py` with exactly one package ID. `deferred` and `pending_reconciliation` are safe non-error outcomes and must not be bypassed.
8. Only write `published` after a public URL is verified. Refresh metrics and reports, validate state/security, commit canonical files, push `HEAD:main`, verify the remote commit, and publish only the fixed report slugs.
9. Finish within the schedule slot. Persist recoverable state and exit on a bounded timeout so one run cannot suppress later Cron cycles.

## Publishing invariants

- Verify the enabled integration is `@_When2buy`.
- Never expose credentials, cookies, tokens, or browser profiles.
- Never duplicate an accepted Postiz delivery.
- Never mark publication from a click or accepted task alone; require a public X URL.
- Never publish expired backlog or bypass the account-level limiter.
- Do not fabricate facts, quotes, guarantees, or inside information.

## Completion

Return a compact summary: selected topic, `published`/`pending_reconciliation`/`deferred` outcome, public URL when available, image path, report link, and next scheduled action.
