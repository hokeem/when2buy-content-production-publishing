#!/usr/bin/env python3
"""Small, consistent Postiz Public API client used by production scripts."""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.getenv('POSTIZ_BASE_URL', 'https://api.postiz.com/public/v1').rstrip('/')
DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    'Chrome/140.0.0.0 Safari/537.36'
)
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class PostizAPIError(RuntimeError):
    pass


def request_json(path, method='GET', data=None, content_type='application/json', timeout=45):
    """Call Postiz with a browser-compatible signature.

    GET is retried for transient responses. Mutating requests are never retried
    because an ambiguous retry can duplicate a public post.
    """
    key = os.getenv('POSTIZ_API_KEY')
    if not key:
        raise PostizAPIError('POSTIZ_API_KEY is unavailable in the local credential paths')

    headers = {
        'Authorization': key,
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': os.getenv('POSTIZ_USER_AGENT', DEFAULT_USER_AGENT),
    }
    if data is not None:
        headers['Content-Type'] = content_type

    attempts = 3 if method.upper() == 'GET' else 1
    for attempt in range(attempts):
        try:
            request = Request(BASE + path, data=data, headers=headers, method=method)
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            body = exc.read(600).decode('utf-8', 'replace')
            if exc.code in RETRYABLE_STATUS and attempt + 1 < attempts:
                time.sleep(2 ** attempt)
                continue
            raise PostizAPIError(f'Postiz HTTP {exc.code}: {body}') from exc
        except (URLError, TimeoutError) as exc:
            if method.upper() == 'GET' and attempt + 1 < attempts:
                time.sleep(2 ** attempt)
                continue
            raise PostizAPIError(f'Postiz network error: {type(exc).__name__}') from exc
