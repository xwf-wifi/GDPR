"""Collect observable browser evidence; never infer legal compliance automatically."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


def snapshot(page, context):
    return {
        "cookies": context.cookies(),
        "local_storage": page.evaluate("() => Object.fromEntries(Object.entries(localStorage))"),
        "session_storage": page.evaluate("() => Object.fromEntries(Object.entries(sessionStorage))"),
    }


def collect_site(browser, site, output_root: Path, timeout_ms: int) -> dict:
    # Each site has a fresh browser context: no consent or storage crosses sites.
    context = browser.new_context(locale="en-GB", timezone_id="Europe/Brussels")
    page = context.new_page()
    requests = []
    responses = []
    page.on("request", lambda req: requests.append({"url": req.url, "method": req.method, "resource_type": req.resource_type}))
    # response.headers intentionally omits cookie-related headers in Playwright.
    page.on("response", lambda res: responses.append({"url": res.url, "status": res.status, "set_cookie": res.header_value("set-cookie") is not None}))
    rank, domain = site["rank"], site["domain"]
    result = {"rank": rank, "domain": domain, "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "scenario": "fresh_visit_no_interaction", "browser_locale": "en-GB", "timezone": "Europe/Brussels",
              "set_cookie_detection": "header_value"}
    site_dir = output_root / f"{rank:03d}_{domain}"
    site_dir.mkdir(parents=True, exist_ok=True)
    try:
        response = page.goto(f"https://{domain}/", wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(3000)
        result.update({"final_url": page.url, "http_status": response.status if response else None,
                       "page_title": page.title(), "snapshot": snapshot(page, context),
                       "page_text_excerpt": page.locator("body").inner_text(timeout=5000)[:8000]})
        page.screenshot(path=str(site_dir / "initial.png"), full_page=False, timeout=10000)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"[:1000]
    finally:
        result["requests"] = requests
        result["responses"] = responses
        result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (site_dir / "evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        context.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites", type=Path, default=Path("data/top100.json"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--limit", type=int, default=1, help="Start with one site; use 100 for the full sample")
    parser.add_argument("--start-rank", type=int, default=1)
    parser.add_argument("--domain", help="Collect one exact domain from the committed Tranco sample")
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()
    if args.limit < 1 or args.start_rank < 1:
        parser.error("limit and start-rank must be positive")
    sites = json.loads(args.sites.read_text(encoding="utf-8"))["sites"]
    if args.domain:
        selected = [site for site in sites if site["domain"] == args.domain.lower()]
        if not selected:
            parser.error("domain is not in data/top100.json")
    else:
        selected = [site for site in sites if site["rank"] >= args.start_rank][: args.limit]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        try:
            for site in selected:
                result = collect_site(browser, site, args.output, args.timeout_ms)
                print(f"{site['rank']:3} {site['domain']}: {'error' if result.get('error') else 'captured'}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
