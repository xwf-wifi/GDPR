# Tranco Top 100 Cookie Consent Study

This repository contains a reproducible sample and a browser evidence collector for studying cookie consent on the Tranco top 100 domains. It does **not** issue automated legal verdicts. A domain may be an API, CDN, inaccessible page, or serve different content by location. The committed Tranco archive is list **64X3X**, not a live ranking; preserve that ID and the collection date in reports.

## Start

```bash
python prepare_sites.py
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python collect.py --limit 1
```

`data/top100.json` records the exact original ranks. `results/001_google.com/evidence.json` and `initial.png` contain evidence from a fresh browser context. Run `python collect.py --limit 100` once the pilot and location are configured. The collector does not click on banners; that is deliberate for the initial pre-consent observation. `results/` is ignored by Git because page text and cookies can contain personal or session data. Review and redact evidence before sharing it.

For the Baidu pilot, run `python collect.py --domain baidu.com`, then `python analyze.py results/084_baidu.com/evidence.json`. The analyzer prints cookie **names and domains**, storage **keys**, response counts, and external request **hostnames**, omitting values and full URLs. Review even this summary before sharing it. Its assessment is deliberately `inconclusive`: this first-visit evidence cannot identify which cookies are necessary or prove GDPR compliance. See `demos/baidu.md` for the remaining steps.

Evidence collected before the response-header fix lacks `set_cookie_detection`. For those files the analyzer reports the `Set-Cookie` response count as unknown, even if the old collector recorded zero. Re-run collection with the current script to measure that field.

## CSV tables

Run `python export_csv.py` after collection. It creates two **local review templates** (`data/site_claims.csv` for policy claims and `data/cookie_reviews.csv` for cookie purposes) and two Excel-compatible exports (`reports/site_summary.csv` and `reports/cookie_inventory.csv`). Edit the review templates, then re-run the exporter to merge those annotations into the reports. Existing review entries are preserved and newly observed cookies are appended. `not_reviewed`/`unreviewed` means no human conclusion yet; `inconclusive` is not a compliance verdict. Record policy URLs, short verified excerpts and review dates; classify cookie purposes only with evidence. The CSVs omit raw cookie values and full request URLs, but names, domains, policy notes, and excerpts still need review before sharing. Local review templates and reports are ignored by Git.

## Research protocol

1. **Sample:** retain all 100 Tranco ranks, even if some are infrastructure domains. Mark `not_user_facing`, `blocked`, `unreachable`, or `observed` separately; do not replace ranks silently. Record date, list ID, browser version, IP country (verified externally), locale, site URL, redirect, and whether the page was accessible. Browser timezone/locale do **not** establish an EU IP location. Use an authorized EU network exit if the study targets EU visitors.
2. **Claims:** locate a cookie notice and privacy/cookie policy using the actual website. Record exact URL, access date, relevant short excerpt, stated purposes, legal basis, and whether the site explicitly claims GDPR compliance. An LLM may extract candidate claims and policy passages, but a person must verify the quote and source. Absence of the phrase “GDPR compliant” does not end the inquiry.
3. **Behavior:** for each user-facing site, independently repeat in fresh browser contexts: no interaction, reject optional cookies, accept optional cookies, and withdraw consent (when supported). Record screenshots, timestamps, cookies, local/session storage, third-party requests and `Set-Cookie` response headers at each stage. Wait a fixed interval after load; follow identical steps across sites. This starter collector implements only the first scenario; the remaining scenarios require site-specific consent interactions and manual verification.
4. **Classification:** determine the purpose of each observed cookie/storage item using the site's disclosure and supporting evidence. Do not treat every cookie as tracking: strictly necessary cookies may be exempt from consent. Requests alone do not prove tracking or personal-data transfer. Flag uncertain classifications for review.
5. **Assessment:** compare verified policy claims with observed behavior. Record `pass`, `potential_issue`, `inconclusive`, or `not_applicable` per criterion, with evidence paths and explanations. Do not label a whole company legally noncompliant from a single screenshot or unknown cookie name.

| Check | Evidence to record |
| --- | --- |
| Prior consent | Were optional cookies or similar storage set before an affirmative choice? |
| Choice | Is rejection available, and are optional purposes separately selectable? |
| Information | Are purposes, parties, and retention described clearly before choice? |
| Withdrawal | Can consent be withdrawn, and does subsequent optional processing stop? |
| Claim consistency | Does the actual browser behavior match the policy's specific claims? |

Applicable rules include **ePrivacy Directive Article 5(3)** for storing/accessing information on a user's device and **GDPR consent rules** when processing personal data. EU/EEA national implementation and site context matter. Treat findings as research observations, not legal advice.

## Sources

- Tranco list and stable IDs: https://tranco-list.eu/ and https://www.measuretheweb.org/programming/tranco
- EU explanation of cookie consent: https://europa.eu/youreurope/business/growing/digitalising/online-privacy/index_en.htm
- EDPB cookie banner task force report: https://www.edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf
- EDPB Guidelines 05/2020 on consent: https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en
- Assignment references: https://link.springer.com/chapter/10.1007/978-3-030-15986-3_17 ; https://arxiv.org/pdf/1808.05096 ; http://www.eurecom.fr/fr/publication/5941/download/sec-publi-5941.pdf ; https://dl.acm.org/ft_gateway.cfm?id=3354212&type=pdf

## Limits of the starter collector

The browser context has an EU locale and timezone, but its network location depends on the machine. Browser cookies include values that may be sensitive. Response header collection only records whether `Set-Cookie` exists, and snapshot cookies show state after the fixed three-second wait. Redirects, CMP dialogs, consent changes, dynamically created frames, cookie purposes, and tracking outcomes require further manual or site-specific analysis. Network errors are recorded, never interpreted as compliance.
