# Postiz delivery policy

Postiz acceptance and X publication are separate events. Persist the Postiz task ID immediately after the create request returns and set the package to `publishing` before polling.

- Minimum gap between accepted submissions: 15 minutes.
- Rolling maximum: 4 submissions per hour and 24 per 24 hours.
- Scheduled cycle maximum: 1 submission.
- Delayed-success grace: 60 minutes.
- An accepted task in `QUEUE`, `ERROR`, or `FAILED` remains `publishing` during the grace window.
- Reconcile by Postiz task ID on every run. Never resubmit an accepted task without a public URL.
- Only `PUBLISHED` plus a public X URL creates a `posts` record.
- After the grace window, an unchanged downstream error may become terminal `failed`; a later verified success must still upgrade it to `published`.

Defaults live in `scripts/postiz_delivery_policy.py` and may be made more conservative through environment variables. Scheduled agents must not relax them.
