"""
host-tag-update
-------------------

Add tags to Datadog hosts without overwriting existing tags.

This utility reads one or more Datadog host identifiers (either from
--host or a --hosts-file (default hosts.txt)), fetches current tags for
each host using the official datadog_api_client, computes which
user-provided tags are missing, and adds only those tags using
TagsApi.create_host_tags (the script never removes existing tags).
"""

from typing import List, Set
import argparse
import os
import sys

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.tags_api import TagsApi
from datadog_api_client.v1.model.host_tags import HostTags


def normalize_tag(tag: str) -> str:
    if not tag or not isinstance(tag, str):
        return ""
    return ":".join([p.strip() for p in tag.strip().split(":", 1)])


def read_hosts(file_path: str = "hosts.txt") -> List[str]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_existing_tags(api: TagsApi, host: str) -> Set[str]:
    try:
        resp = api.get_host_tags(host_name=host)
        tags = getattr(resp, "tags", None)
        return set(tags) if tags else set()
    except Exception as e:
        print(f"Failed to fetch tags for {host}: {e}")
        return set()


def add_tags(api: TagsApi, host: str, tags_to_add: Set[str]) -> List[str]:
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
        return
    current = get_existing_tags(api, host)
    tags_to_add = desired - current
    if not tags_to_add:
        print(f"Host {host} already has desired tags; nothing to add.")
        return
    added = add_tags(api, host, tags_to_add)
    print(f"Added tags to {host}: {added}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add tags to Datadog hosts without overwriting existing tags")
    parser.add_argument("-t", "--tags", required=True, help="comma-separated tags to add (e.g. 'env:prod,role:web')")
    parser.add_argument("--host", help="single Datadog host identifier to update (bypasses hosts-file)")
    parser.add_argument("-f", "--hosts-file", default="hosts.txt", help="path to hosts file (one host per line)")
    parser.add_argument("--dd-site", help="override DD_SITE from the environment (datadoghq.com or datadoghq.eu)")
    args = parser.parse_args()

    if args.host:
        hosts = [args.host]
    else:
        hosts = read_hosts(args.hosts_file)

    if not hosts:
        print("No hosts found to update; provide --host or a hosts-file with hosts")
        sys.exit(0)

    desired_tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    dd_site = args.dd_site or os.environ.get("DD_SITE")
    allowed_sites = {"datadoghq.com", "datadoghq.eu"}
    if dd_site:
        if dd_site not in allowed_sites:
            print("Invalid DD_SITE: must be one of datadoghq.com or datadoghq.eu")
            sys.exit(2)
        configuration = Configuration(host=f"https://api.{dd_site}")
    else:
        configuration = Configuration()

    api_key = os.environ.get("DD_API_KEY")
    app_key = os.environ.get("DD_APP_KEY")
    if not api_key or not app_key:
        print("Missing Datadog credentials: please set DD_API_KEY and DD_APP_KEY environment variables (or provide them via Configuration).")
        sys.exit(1)

    try:
        with ApiClient(configuration) as api_client:
            api = TagsApi(api_client)
            for host in hosts:
                merge_and_add(api, host, desired_tags)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
