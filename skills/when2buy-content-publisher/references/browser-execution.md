# Browser execution

## Publish

1. Use the supported in-app browser control capability and navigate to `https://x.com/compose/post`.
2. Confirm the visible account handle is the intended when2buy account. Stop if it is not.
3. Inspect the current composer state. Clear only unsent content created by this run.
4. Enter the approved post text exactly as stored in the package.
5. Upload the generated image from its absolute local path and wait for the preview.
6. Proofread text, image, ticker, numbers, and dates in the visible composer.
7. If the task carries explicit direct-publish authorization, click Post. Do not add another approval checkpoint.
8. Wait for success navigation or toast, open the resulting status, and confirm text and media are public.
9. Store the exact status URL and `publishedAt`. If the public URL cannot be verified, record `verification_failed`, not `published`.

Never use DOM injection or hidden network calls to bypass the normal website UI. Never upload cookies or browser profiles.

## Metrics

1. Open each published status URL due for a snapshot.
2. Read only visible public metrics. Do not estimate hidden values.
3. Normalize abbreviations carefully (`1.2K` = 1200); preserve `null` for unavailable metrics.
4. Append a new snapshot with the observation time. Never overwrite an older observation.
5. Record a blocker when the post is unavailable, the session is logged out, the account is limited, or the metric is not visible.

## Recovery

- Logged out: stop and request interactive login. Do not import cookie files.
- CAPTCHA or account challenge: stop and request user action.
- Duplicate composer submission: inspect the profile before retrying.
- Upload failure: retry once after checking the local file. Do not repeatedly post text-only unless authorized.
- Rate limit or platform error: record the error and defer; do not hammer the action.
