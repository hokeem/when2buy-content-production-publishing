# State data contract

`data/state.json` is the single tracked source of truth.

## Top-level fields

- `version`: schema version.
- `updatedAt`: ISO-8601 timestamp of the last successful state write.
- `account`: intended X handle and timezone.
- `benchmarks`: monitored discovery accounts.
- `radar`: ranked opportunities from the most recent scan.
- `packages`: generated text-and-image packages.
- `posts`: verified public posts.
- `metricSnapshots`: append-only public observations.
- `experiments`: controlled content tests and conclusions.
- `runs`: append-only execution log.

## Status vocabulary

- Package: `draft`, `ready`, `publishing`, `published`, `blocked`, `failed`.
- Run: `started`, `succeeded`, `partial`, `blocked`, `failed`.

## Stable IDs

- Radar: `radar-YYYYMMDD-HHMM-rank` in Asia/Shanghai.
- Package: `pkg-YYYYMMDD-topic-slug`.
- Post: X status ID when available; otherwise package ID until publication.
- Snapshot: `statusId-YYYYMMDDTHHMMSSZ`.
- Run: `run-YYYYMMDDTHHMMSSZ-mode`.

## Write rules

Use `skills/when2buy-content-publisher/scripts/state.py` for validation and append operations. Write atomically. Preserve unknown fields for forward compatibility. Never record secrets or copied third-party commentary.
