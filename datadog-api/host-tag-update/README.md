# host-tag-update

Utility to add tags to Datadog hosts without overwriting existing tags.

This small CLI reads a list of Datadog host identifiers (one per line) or accepts a single host via `--host`, fetches the current tags for each host using the official `datadog_api_client`, computes which user-provided tags are missing, and adds only the new tags using the Datadog Tags API.

## Features

- Merges user-provided tags with existing host tags (idempotent add).
- Uses the official `datadog_api_client` for API calls.
- Supports per-host updates and batch updates from a `hosts.txt` file.
- Fails early when required credentials or invalid site values are missing.

## Requirements

- Python 3.8+
- `datadog-api-client` Python library

Install requirements:

```bash
pip install datadog-api-client
```

## Important environment variables

- `DD_API_KEY` (required) — Datadog API key
- `DD_APP_KEY` (required) — Datadog application key
- `DD_SITE` (optional) — must be either `datadoghq.com` or `datadoghq.eu` if set; used to select the API base URL

Notes:
- The script requires `DD_API_KEY` and `DD_APP_KEY` to be set in the environment; it will exit early with a message if either is missing.
- `DD_SITE` is limited to `datadoghq.com` or `datadoghq.eu`. If unset, the client default is used.

## Usage

Basic usage (reads hosts from `hosts.txt`):

```bash
export DD_API_KEY="<your_api_key>"
export DD_APP_KEY="<your_app_key>"
export DD_SITE=datadoghq.eu   # optional; must be datadoghq.com or datadoghq.eu

python host-tag-update.py --tags "env:prod,role:web"
```

Update a single host by name (Datadog host identifier):

```bash
python host-tag-update.py --host my-host.example.com --tags "env:prod,role:web"
```

Notes on `--tags`:
- Provide a comma-separated list of tags (e.g. `env:prod,role:web`).
- Tags are normalized by trimming whitespace; the script preserves case.

## `hosts.txt` format

One Datadog host identifier per line. Empty lines are ignored.

Example `hosts.txt`:

```
my-host-1.example.com
my-host-2.example.com
```

## Exit codes

- `0` — success (script completed)
- `1` — missing required credentials (`DD_API_KEY` or `DD_APP_KEY`)
- `2` — invalid `DD_SITE` value (must be `datadoghq.com` or `datadoghq.eu`)

## Implementation notes

- The script uses `TagsApi.get_host_tags` to fetch existing tags and `TagsApi.create_host_tags` to add new tags. It does not replace or remove existing tags.
- Consider adding retries/backoff and structured logging for production use.
- If you prefer, you can provide API keys via a custom `Configuration` object instead of environment variables (the client supports that).

## Next steps / Suggestions

- Add a `--dry-run` mode to show changes without calling the API.
- Add unit tests for the tag-merge logic.
- Add retry/backoff (e.g., `tenacity`) around API calls to handle transient errors and rate limits.

---

File: `host-tag-update.py` — companion script that performs the operations described above.
