---
name: when2buy-content-publisher
description: "Run the benchmark-first when2buy U.S.-market X workflow end to end. At four fixed daily windows, inspect every new original post from @WhaleInsider and @StockMKTNewz, select the strongest same-topic opportunities, verify the underlying facts, create independently worded when2buy English posts and branded images, prepare browser publishing, collect metrics, and produce an agent-readable report. Use for daily when2buy competitor monitoring, mirrored-topic production, X publishing, scheduled runs, performance reviews, or migration to another Codex agent."
---

# when2buy Content Publisher

Operate from the repository root. Treat `data/state.json` as the durable handoff between agents.

## Non-negotiable operating model

Run a **benchmark-first mirror desk**, not a general finance idea generator.

1. Begin every `radar`, `produce`, or `full` run by opening both exact feeds:
   - `https://x.com/WhaleInsider`
   - `https://x.com/StockMKTNewz`
2. Capture every new original post since the previous successful scan. Exclude replies, repost-only entries, promotions, and unrelated crypto content.
3. If neither account has a new eligible post, scan backward up to 48 hours. Do not invent an unrelated topic merely to fill a slot.
4. Make when2buy cover the **same news event, company/ticker, key disclosed facts, decisive numbers, and urgency window** as the selected benchmark post.
5. Do not copy the benchmark's distinctive sentences, jokes, commentary, or artwork. `Same content` means the same verified topic and factual payload expressed in original when2buy wording and visuals.
6. Store the benchmark status URL and mapping before producing. A package without a `benchmarkPostId`, benchmark URL, and mirrored-facts list is invalid.

Scheduled scans use Asia/Shanghai time at **08:30, 12:30, 18:30, and 22:30**. Read [scheduled-task.md](references/scheduled-task.md) for the exact behavior at each window.

## Select the run mode

- `radar`: inspect sources and populate five ranked opportunities.
- `produce`: turn the strongest eligible opportunity into a complete text-and-image package.
- `publish`: publish a ready package through the signed-in X browser session.
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
4. Trace every material claim to a primary source or authoritative financial reporting. Record what was confirmed and what remains uncertain.
5. Rank benchmark posts by freshness, market impact, factual clarity, visual potential, and duplication risk. Store up to five one-to-one opportunities; never create an unrelated filler topic.
6. Produce from the highest-ranked benchmark post. Preserve the selected topic, tickers, factual sequence, key numbers, and urgency; independently write the narration and analysis.
7. Create one 1:1 branded image using the exact `assets/when2buy-logo-reference.png` logo and the visual rules in [brand-and-style.md](references/brand-and-style.md). Compare the draft against all three supplied style examples before accepting it.
8. Complete research, copy, and image production autonomously. For browser-based publishing, stop at `ready` and request action-time confirmation immediately before clicking Post; this is an execution confirmation, not a separate editorial review. Platform login, CAPTCHA, account lock, or materially inconsistent facts also require user attention.
9. After publishing, open the public status URL and verify that text and media are visible. Only then set status to `published` and store the URL.
10. Record the run and metric snapshot with `state.py`; run validation and `python3 scripts/render_report.py` again.

## Publishing invariants

- Use the intended `when2buy` X account; verify the visible handle before composing.
- Never import, print, commit, or transmit cookies, passwords, personal access tokens, API keys, or browser profiles.
- Do not send DMs, reply to unrelated users, follow accounts, or mass-engage unless the current user request separately authorizes that exact action.
- Do not mark a post published based only on clicking the button. Require its public URL.
- Do not label generated media as AI unless the user or platform requires it. Never remove a platform-required provenance label.
- Do not make investment guarantees, fabricate quotes, or imply inside information.
- Do not replace the two benchmark accounts with a generic news search. Upstream sources verify facts; they do not replace benchmark-first topic selection.
- On uncertainty, publish nothing and record a `blocked` run with a precise reason.

## Completion

Return a compact run summary: selected topic, published URL or blocker, image path, sources used, report path, and next scheduled action.
