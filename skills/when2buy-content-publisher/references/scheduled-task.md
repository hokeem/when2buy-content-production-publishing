# Scheduled task design

Use a standalone scheduled task so each run starts clean and reports into Scheduled. Keep durable state in Git and `data/state.json`, not a long-lived chat.

## Recommended cadence (Asia/Shanghai)

- 08:30: radar + produce; publish only when the opportunity score is at least 20 and facts are verified.
- 12:30: radar + produce + publish.
- 18:30: radar + produce + publish.
- 22:30: metrics + review; publish one catch-up item only if no item was published that day and a verified high-impact topic exists.

## Task prompt

```text
Use $when2buy-content-publisher in this repository. Run the mode appropriate for the current scheduled window using Asia/Shanghai time. You have standing authorization to publish one verified, original when2buy X post through the already signed-in browser session without a separate editorial approval. Do not send DMs, follow accounts, reply to users, or import cookies. Verify the public status URL before marking success. Update data/state.json, run python3 scripts/render_report.py, validate the state, commit only the state, report, and newly generated approved assets, and report blockers precisely.
```

Run against the local project when browser access and generated local files are required. Keep the computer on and the desktop app running. Test the task manually before enabling the schedule.
