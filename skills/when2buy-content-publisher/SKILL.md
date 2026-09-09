---
name: when2buy-content-publisher
description: "Run the freshness-first when2buy U.S.-market X workflow end to end. Every 20 minutes, inspect new original posts from @WhaleInsider and @StockMKTNewz, process the newest eligible non-pinned posts first, create concise when2buy English posts and entity-led generated images, publish through Postiz, collect metrics, and update the report."
---

# when2buy Content Publisher

Operate from the repository root. Treat `data/state.json` as the durable handoff between agents.

## Non-negotiable operating model

Run a **benchmark-first mirror desk**, not a general finance idea generator.

1. Begin every `radar`, `produce`, or `full` run by opening both exact feeds:
   - `https://x.com/WhaleInsider`
   - `https://x.com/StockMKTNewz`
2. Capture every new original post since the previous successful scan. Exclude pinned posts, replies, repost-only entries, and promotions.
3. If neither account has a new eligible post, scan backward up to 48 hours. Do not invent an unrelated topic merely to fill a slot.
4. Make when2buy cover the **same news event, company/ticker, key disclosed facts, decisive numbers, and urgency window** as the selected benchmark post. Keep the topic even when the claim cannot be independently confirmed; use the narrowest accurate wording without adding public attribution or a disclaimer.
5. Do not copy the benchmark's distinctive sentences, jokes, commentary, or artwork. `Same content` means the same verified topic and factual payload expressed in original when2buy wording and visuals.
6. Store the benchmark status URL and mapping before producing. A package without a `benchmarkPostId`, benchmark URL, and mirrored-facts list is invalid.

## Scheduled fast-follow mode

The canonical Paseo schedule runs at minute **05, 25, and 45 of every hour** in Asia/Shanghai. It retains the benchmark account, status URL, captured text, and media provenance internally, but never prints the source account, source URL, `according to`, `reported by`, `Market radar`, an unverified disclaimer, or investment-advice boilerplate in public copy or artwork.

Publication order is the order in `data/production-queue.json`: newest eligible non-pinned source first, with engagement used only to break an identical timestamp. Process and publish up to five items per run. Never replace a newer topic with an older hotter one.

## Select the run mode

- `radar`: inspect sources and populate the ranked production queue.
- `produce`: turn every newly eligible opportunity into a complete text-and-image package.
- `publish`: publish a ready package through Postiz.
- `metrics`: refresh public metrics for published posts.
- `review`: compare performance and record an evidence-backed next experiment.
- `full`: run radar, produce, publish, and record the initial snapshot.

Read only the references needed for the selected mode:

- For every `radar`, `produce`, or `full` run, read [editorial-system.md](references/editorial-system.md), [brand-and-style.md](references/brand-and-style.md), and [cases.md](references/cases.md). These are mandatory inputs, not optional inspiration.
- Read [browser-execution.md](references/browser-execution.md) for publish or metrics.
- Read [data-contract.md](references/data-contract.md) before modifying state.
- Read [scheduled-task.md](references/scheduled-task.md) when setting up recurring runs.

## Core workflow

1. Run `python3 skills/when2buy-content-publisher/scripts/preflight.py` and `python3 skills/when2buy-content-publisher/scripts/state.py validate`.
2. Inspect `data/state.json`; determine the last successful benchmark scan time and avoid duplicate topics.
3. Scan both benchmark feeds first. Append the discovered source posts to `benchmarkPosts` with exact status URL, timestamp, visible text, and account.
4. Retain the source mapping internally. Verification may improve wording, but it is not a gate and never causes the workflow to skip a newer captured topic.
5. Process `data/production-queue.json` in listed order. The first item is the newest eligible non-pinned source; engagement cannot promote an older source over it.
6. Preserve the source core event, company/ticker, decisive number, factual order, and information density. Reorder wording lightly. Put the event first and end with exactly `When2Buy — your U.S. stock partner.` Do not add attribution, sourcing, disclaimers, commentary paragraphs, or a second CTA.
7. Use the image-generation model to create a complete 1:1 entity-led scene in one generation. A pure typography card, generic radar background, or programmatically drawn template is invalid. Leave a clean logo-safe area, then composite the exact `assets/when2buy-logo-reference.png` logo once. Record `visualProduction.method=image_model`, the generation prompt, `logoApplied=true`, and `qaStatus=passed` in the package.
8. Complete research, copy, and image production autonomously. First run `python3 scripts/reconcile_postiz_publications.py --lookback-hours 72`, then publish up to five queue-ordered packages with one `python3 scripts/postiz_publish_batch.py --package-id <id> ... --confirm` call. The batch runner is strictly serial, waits between posts, verifies the Postiz integration is `@_When2buy`, and requires `PUBLISHED` plus a public X URL for each item. With standing authorization, publish without interactive confirmation.
9. Only record `published` after Postiz returns `PUBLISHED` and a public X release URL. Then refresh the run panel.
10. Before any external publish call run `python3 scripts/validate_content_standard.py --package-id <id>`. Record the run and metric snapshot with `state.py`; run validation and `python3 scripts/render_report.py` again.

## Publishing invariants

- Use the intended `when2buy` X account; verify the visible handle before composing.
- Never import, print, commit, or transmit cookies, passwords, personal access tokens, API keys, or browser profiles.
- Do not send DMs, reply to unrelated users, follow accounts, or mass-engage unless the current user request separately authorizes that exact action.
- Do not mark a post published based only on clicking the button. Require its public URL.
- Do not label generated media as AI unless the user or platform requires it. Never remove a platform-required provenance label.
- Do not make investment guarantees, fabricate quotes, or imply inside information.
- Do not replace the two benchmark accounts with a generic news search. Upstream sources verify facts; they do not replace benchmark-first topic selection.
- Source provenance remains internal. Public copy and artwork contain no source handle, source URL, `according to`, `reported by`, verification disclaimer, or investment-advice boilerplate.

## Completion

Return a compact run summary: selected topic, published URL or blocker, image path, sources used, report path, and next scheduled action.
