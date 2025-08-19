"""
Utility to add 'user' tags to Datadog hosts without overwriting existing tags.

This script reads a list of host names from `hosts.txt`, fetches the
current tags for each host using the official `datadog_api_client`, computes
which tags from the user are not already present, and adds only the new tags
via `TagsApi.create_host_tags`.

Usage examples:
  # add tags to hosts listed in hosts.txt
  python host-tag-update.py --tags "env:prod,role:web"

  # add tags to a single host
  python host-tag-update.py --host my-host --tags "env:prod,role:web"

Requirements:
  pip install datadog-api-client
  DD_API_KEY, DD_APP_KEY and DD_SITE set in the environment or provided via
  client Configuration if you prefer.
"""

from typing import List, Set
import argparse
import os
import sys

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.tags_api import TagsApi
from datadog_api_client.v1.model.host_tags import HostTags


def normalize_tag(tag: str) -> str:
    """Basic normalization for tags: strip and collapse internal whitespace.

    Keeps the original case; Datadog tags are case-sensitive in general.
    """
    if not tag or not isinstance(tag, str):
        return ""
    return ":".join([p.strip() for p in tag.strip().split(":", 1)])


def read_hosts(file_path: str = "hosts.txt") -> List[str]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_existing_tags(api: TagsApi, host: str) -> Set[str]:
    """Return the set of tags currently attached to the host.

    If the host is unknown or the API returns an error, an empty set is
    returned and the caller can decide how to proceed.
    """
    try:
        resp = api.get_host_tags(host_name=host)
        tags = getattr(resp, "tags", None)
        return set(tags) if tags else set()
    except Exception as e:
        print(f"Failed to fetch tags for {host}: {e}")
        return set()


def add_tags(api: TagsApi, host: str, tags_to_add: Set[str]) -> List[str]:
    """Add only the supplied tags (assumed to be new) to the given host.

    Returns the list of tags that were added.
    """
    if not tags_to_add:
        return []

    body = HostTags(host=host, tags=list(tags_to_add))
    try:
        resp = api.create_host_tags(host_name=host, body=body)
        return list(getattr(resp, "tags", list(tags_to_add)))
    except Exception as e:
        print(f"Failed to add tags to {host}: {e}")
        return []


def merge_and_add(api: TagsApi, host: str, desired_tags: List[str]) -> None:
    desired = {t for t in (normalize_tag(t) for t in desired_tags) if t}
    if not desired:
        print(f"No valid tags provided for host {host}; skipping")
        """
        host-tag-update
        -----------------

        Add tags to Datadog hosts without overwriting existing tags.

        This utility reads one or more Datadog host identifiers (either from
        `--host` or a `--hosts-file`, default `hosts.txt`), fetches current tags for
        each host using the official `datadog_api_client`, computes which user-
        provided tags are missing, and adds only those tags using
        `TagsApi.create_host_tags` (the script never removes existing tags).

        Key behavior
        - Idempotent: existing tags are preserved; only missing tags are added.
        - Normalizes tags by trimming whitespace (preserves case).
        - Fails early when required credentials or invalid site values are missing.

        Requirements
        - Python 3.8+
        - datadog-api-client (install with `pip install datadog-api-client`)

        Environment variables
        - DD_API_KEY (required)  — Datadog API key
        - DD_APP_KEY (required)  — Datadog app key
        - DD_SITE (optional)     — must be one of `datadoghq.com` or `datadoghq.eu`
                                                             if set; used to choose the API base URL.

        CLI flags
        - --tags / -t      : comma-separated tags to add (e.g. `env:prod,role:web`) (required)
        - --host           : single Datadog host identifier to update (bypasses hosts-file)
        - --hosts-file / -f: path to hosts file (one Datadog host identifier per line)
        - --dd-site        : override `DD_SITE` from the environment (must be `datadoghq.com` or `datadoghq.eu`)

        Exit codes
        - 0 : success
        - 1 : missing credentials (DD_API_KEY or DD_APP_KEY)
        - 2 : invalid DD_SITE value

        Examples
        ```bash
        export DD_API_KEY="<your_api_key>"
        export DD_APP_KEY="<your_app_key>"
        export DD_SITE=datadoghq.eu

        python host-tag-update.py --host my-host.example.com --tags "env:prod,role:web"

        # or bulk from hosts.txt
        python host-tag-update.py --tags "env:prod,role:web"
        ```

        Notes
        - The script relies on the datadog-api-client `Configuration` which also
            reads `DD_API_KEY` and `DD_APP_KEY` from the environment by default.
        - Consider adding a `--dry-run` mode or retries/backoff for production use.
        """
    desired_tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if args.host:
        hosts = [args.host]
    else:
        hosts = read_hosts(args.hosts_file)

    if not hosts:
        print("No hosts found to update; provide --host or a hosts-file with hosts")
        return

    # Preference: explicit --dd-site > environment DD_SITE.
    dd_site = args.dd_site or os.environ.get("DD_SITE")

    # Allow only the two official sites; map to their API hosts deterministically.
    allowed_sites = {"datadoghq.com", "datadoghq.eu"}

    # Decide the Configuration host based on site only. Fail fast on invalid site.
    if dd_site:
        if dd_site not in allowed_sites:
            print("Invalid DD_SITE: must be one of datadoghq.com or datadoghq.eu")
            sys.exit(2)
        host_url = f"https://api.{dd_site}"
        configuration = Configuration(host=host_url)
    else:
        configuration = Configuration()

    # Fail early if required credentials are missing
    api_key = os.environ.get("DD_API_KEY")
    app_key = os.environ.get("DD_APP_KEY")
    if not api_key or not app_key:
        print("Missing Datadog credentials: please set DD_API_KEY and DD_APP_KEY environment variables (or provide them via Configuration).")
        sys.exit(1)

    # The datadog_api_client Configuration reads DATADOG_API_KEY/DATADOG_APP_KEY from env by default.
    with ApiClient(configuration) as api_client:
        api = TagsApi(api_client)
        for host in hosts:
            merge_and_add(api, host, desired_tags)


if __name__ == "__main__":
    main()
