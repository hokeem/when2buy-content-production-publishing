---
name: when2buy-content-publisher
description: "Run the when2buy U.S.-market X content workflow end to end: monitor benchmark accounts and primary sources, choose timely topics, verify market facts, write original English posts, create branded images, publish through the signed-in browser when authorized, collect post metrics, and produce an agent-readable run report. Use for daily when2buy research, content production, X publishing, performance reviews, scheduled runs, or migration to another Codex agent."
---

# when2buy Content Publisher

Operate from the repository root. Treat `data/state.json` as the durable handoff between agents.

## Select the run mode

- `radar`: inspect sources and populate five ranked opportunities.
- `produce`: turn the strongest eligible opportunity into a complete text-and-image package.
- `publish`: publish a ready package through the signed-in X browser session.
- `metrics`: refresh public metrics for published posts.
- `review`: compare performance and record an evidence-backed next experiment.
- `full`: run radar, produce, publish, and record the initial snapshot.

Read only the references needed for the selected mode:

- Read [editorial-system.md](references/editorial-system.md) for radar, production, or review.
- Read [cases.md](references/cases.md) before the first production run in a new environment.
- Read [browser-execution.md](references/browser-execution.md) for publish or metrics.
- Read [data-contract.md](references/data-contract.md) before modifying state.
- Read [scheduled-task.md](references/scheduled-task.md) when setting up recurring runs.

## Core workflow

1. Run `python3 skills/when2buy-content-publisher/scripts/state.py validate`.
2. Inspect `data/state.json`; do not repeat a topic or publish duplicate copy.
3. Research the newest public posts from `@WhaleInsider` and `@StockMKTNewz`, then trace material claims to primary sources or authoritative financial reporting.
4. Rank candidates by freshness, market impact, factual clarity, visual potential, and duplication risk. Store exactly five when enough eligible candidates exist; never invent filler.
5. Write independently. Preserve facts, tickers, numbers, and urgency, but do not copy distinctive wording, jokes, structure, or commentary from another account.
6. Verify every number, date, company name, and transaction detail. Record source URLs and verification notes.
7. Create one 1:1 branded image. Use `assets/when2buy-logo-reference.png` as the logo reference. Keep the graphic legible at mobile size and avoid unsupported claims.
8. If the current task or scheduled-task prompt explicitly authorizes direct publishing, publish without requesting another editorial approval. Otherwise stop at `ready` and ask once. Platform login, CAPTCHA, account lock, or materially inconsistent facts always require user attention.
9. After publishing, open the public status URL and verify that text and media are visible. Only then set status to `published` and store the URL.
10. Record the run and metric snapshot with `state.py`; run validation and `python3 scripts/render_report.py` again.

## Publishing invariants

- Use the intended `when2buy` X account; verify the visible handle before composing.
- Never import, print, commit, or transmit cookies, passwords, personal access tokens, API keys, or browser profiles.
- Do not send DMs, reply to unrelated users, follow accounts, or mass-engage unless the current user request separately authorizes that exact action.
- Do not mark a post published based only on clicking the button. Require its public URL.
- Do not label generated media as AI unless the user or platform requires it. Never remove a platform-required provenance label.
- Do not make investment guarantees, fabricate quotes, or imply inside information.
- On uncertainty, publish nothing and record a `blocked` run with a precise reason.

## Completion

Return a compact run summary: selected topic, published URL or blocker, image path, sources used, report path, and next scheduled action.
