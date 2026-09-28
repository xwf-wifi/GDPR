"""Export redacted site and cookie tables for spreadsheet review."""

import argparse
import csv
import json
from pathlib import Path

from analyze import review


CLAIM_FIELDS = ["rank", "domain", "policy_url", "claim_status", "claim_source_url", "claim_excerpt", "reviewed_at", "notes"]
SITE_FIELDS = CLAIM_FIELDS + ["collection_status", "collected_at_utc", "http_status", "cookie_count", "local_storage_count", "session_storage_count", "set_cookie_response_count", "external_request_hosts", "consent_words_in_excerpt", "cookie_assessment"]
COOKIE_FIELDS = ["rank", "domain", "scenario", "cookie_name", "cookie_domain", "cookie_path", "expires", "http_only", "secure", "same_site", "purpose", "purpose_source_url", "classification_status"]
COOKIE_REVIEW_FIELDS = ["rank", "domain", "scenario", "cookie_name", "cookie_domain", "cookie_path", "purpose", "purpose_source_url", "classification_status"]
COOKIE_KEY = COOKIE_REVIEW_FIELDS[:6]


def safe(value):
    """Avoid spreadsheet formula execution when opening CSV files."""
    value = "" if value is None else str(value)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: safe(row.get(field)) for field in fields})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites", type=Path, default=Path("data/top100.json"))
    parser.add_argument("--claims", type=Path, default=Path("data/site_claims.csv"))
    parser.add_argument("--cookie-reviews", type=Path, default=Path("data/cookie_reviews.csv"))
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, default=Path("reports"))
    args = parser.parse_args()

    sites = json.loads(args.sites.read_text(encoding="utf-8"))["sites"]
    if not args.claims.exists():
        write_csv(args.claims, CLAIM_FIELDS, [dict(site, claim_status="not_reviewed") for site in sites])
        print(f"Created policy review template: {args.claims}")
    with args.claims.open(newline="", encoding="utf-8-sig") as stream:
        claims = {row["domain"]: row for row in csv.DictReader(stream)}

    site_rows, cookie_rows = [], []
    for site in sites:
        rank, domain = site["rank"], site["domain"]
        claim = claims.get(domain, {})
        row = {**{field: claim.get(field, "") for field in CLAIM_FIELDS}, "rank": rank, "domain": domain,
               "claim_status": claim.get("claim_status") or "not_reviewed", "collection_status": "not_collected",
               "cookie_assessment": "inconclusive"}
        evidence_path = args.results / f"{rank:03d}_{domain}" / "evidence.json"
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            summary = review(evidence)
            snapshot = evidence.get("snapshot") or {}
            row.update({
                "collection_status": "captured" if summary["collection_complete"] else "error",
                "collected_at_utc": evidence.get("started_at_utc"),
                "http_status": summary["http_status"],
                "cookie_count": summary["observed_cookie_count"],
                "local_storage_count": len(snapshot.get("local_storage") or {}),
                "session_storage_count": len(snapshot.get("session_storage") or {}),
                "set_cookie_response_count": summary["set_cookie_response_count"],
                "external_request_hosts": "; ".join(summary["external_request_hosts"]),
                "consent_words_in_excerpt": "; ".join(summary["consent_related_words_in_excerpt"]),
            })
            for cookie in snapshot.get("cookies") or []:
                cookie_rows.append({
                    "rank": rank, "domain": domain, "scenario": evidence.get("scenario", ""),
                    "cookie_name": cookie.get("name"), "cookie_domain": cookie.get("domain"),
                    "cookie_path": cookie.get("path"), "expires": cookie.get("expires"),
                    "http_only": cookie.get("httpOnly"), "secure": cookie.get("secure"),
                    "same_site": cookie.get("sameSite"), "classification_status": "unreviewed",
                })
        site_rows.append(row)

    existing_reviews = []
    if args.cookie_reviews.exists():
        with args.cookie_reviews.open(newline="", encoding="utf-8-sig") as stream:
            existing_reviews = list(csv.DictReader(stream))
    review_by_key = {tuple(row.get(field, "") for field in COOKIE_KEY): row for row in existing_reviews}
    for row in cookie_rows:
        key = tuple(str(row.get(field, "")) for field in COOKIE_KEY)
        if key not in review_by_key:
            review_by_key[key] = {field: str(row.get(field, "")) for field in COOKIE_KEY} | {
                "purpose": "", "purpose_source_url": "", "classification_status": "unreviewed"}
        row.update({field: review_by_key[key].get(field, "") for field in COOKIE_REVIEW_FIELDS[6:]})
    write_csv(args.cookie_reviews, COOKIE_REVIEW_FIELDS, review_by_key.values())
    write_csv(args.output / "site_summary.csv", SITE_FIELDS, site_rows)
    write_csv(args.output / "cookie_inventory.csv", COOKIE_FIELDS, cookie_rows)
    print(f"Exported {len(site_rows)} sites and {len(cookie_rows)} cookie rows to {args.output}")
    print("No cookie values or full request URLs exported. Review names, domains and policy notes before sharing.")


if __name__ == "__main__":
    main()
