"""Create a redacted, preliminary cookie-consent review from collected evidence."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit


CONSENT_WORDS = ("cookie", "cookies", "同意", "隐私", "接受", "拒绝", "consent", "accept", "reject")


def host(url):
    try:
        return urlsplit(url).hostname or ""
    except ValueError:
        return ""


def review(evidence):
    snapshot = evidence.get("snapshot") or {}
    cookies = snapshot.get("cookies") or []
    text = (evidence.get("page_text_excerpt") or "").lower()
    domain = evidence.get("domain") or ""
    request_hosts = sorted({host(x.get("url", "")) for x in evidence.get("requests", [])} - {""})
    # A hostname outside the target's domain is a lead, not proof of tracking.
    external_hosts = [h for h in request_hosts if h != domain and not h.endswith("." + domain)]
    set_cookie_responses = sum(bool(x.get("set_cookie")) for x in evidence.get("responses", []))
    complete = bool(snapshot) and not evidence.get("error")
    return {
        "rank": evidence.get("rank"),
        "domain": domain,
        "scenario": evidence.get("scenario"),
        "collection_complete": complete,
        "http_status": evidence.get("http_status"),
        "observed_cookie_count": len(cookies),
        "cookie_names_and_domains": sorted({(x.get("name", ""), x.get("domain", "")) for x in cookies}),
        "local_storage_keys": sorted((snapshot.get("local_storage") or {}).keys()),
        "session_storage_keys": sorted((snapshot.get("session_storage") or {}).keys()),
        "set_cookie_response_count": set_cookie_responses,
        "external_request_hosts": external_hosts,
        "consent_related_words_in_excerpt": [word for word in CONSENT_WORDS if word in text],
        "assessment": "inconclusive",
        "reason": (
            "Collection failed or was incomplete; inspect local evidence."
            if not complete else
            "A fresh visit only shows observations. Classify cookie purposes, verify the EU network location, "
            "inspect the banner visually, and compare reject/accept/withdraw scenarios before assessment."
        ),
        "note": "No cookie values, page text, request URLs or storage values are included. "
                "Names and hostnames can still be sensitive: inspect before sharing.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, help="Path to results/<site>/evidence.json")
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    print(json.dumps(review(evidence), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
