# when2buy Agent Rules

Use `$when2buy-content-publisher` for all editorial, publishing, metrics, and review work in this repository.

1. Read `data/state.json` before acting, validate it after every write, then regenerate `reports/latest.md`.
2. Keep all agent-to-agent handoff state in tracked JSON; do not rely on chat history.
3. Never commit credentials, cookies, browser profiles, private messages, or raw authentication material.
4. Treat benchmark accounts as discovery inputs, not copy sources. Produce original wording and visuals.
5. In standard mode, verify financial claims against primary sources or authoritative financial reporting before publication. In owner-directed `QUICK MARKET RADAR` mode, publish only with the required benchmark attribution and unverified disclosure; never recast third-party claims as established facts or give trading recommendations.
6. Publish only when the task contains explicit current or standing authorization. The scheduled `when2buy-production-publish` task has standing authorization to publish through Postiz to `@_When2buy`; verify the public URL before recording success.
7. Preserve prior metric snapshots. Append observations; never rewrite history.
8. Keep changes narrow. Stage explicit files only and never overwrite unrelated agent work.
9. For a full run, follow `docs/OPERATING_MODEL.md`; use `scripts/postiz_publish.py` rather than ad-hoc API requests.
10. Every completed run must regenerate `reports/latest.md` and `reports/run-panel.html`. The scheduled report sync may update the already-authorized stable report URL, but must never create a new public destination.
