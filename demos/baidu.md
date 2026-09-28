# Baidu cookie consent pilot — 2026-09-28

## Scope and result

- Sample: Tranco `64X3X`, rank **84**, `baidu.com`.
- Target: the public desktop homepage `https://www.baidu.com/`, logged out.
- Preliminary status: **inconclusive**. This is an observation and a reproducible next step, not a GDPR compliance verdict.
- The cloud browser opened the homepage and displayed ordinary search content. In the visible page text and accessibility view, no cookie consent banner, reject button, or privacy settings control was apparent on initial load. This does not establish that no such control exists for an EU visitor.
- The browser inspection interface did not provide a reliable full cookie jar, HttpOnly cookies, storage, network requests, IP country, or fresh isolated browser context. No evidence was collected for whether optional storage was set before consent. The local Playwright package installed, but the Chromium download failed (incomplete ZIP), so `collect.py` could not run here. No `results/` evidence was fabricated.

## Policy comparison

The [Baidu general privacy policy](https://privacy.baidu.com/policy.html), section “二、我们如何使用 Cookie 和同类技术”, says cookies support site operation, unique visitor statistics, and personalization; it also describes cookies or anonymous identifiers associated with partner advertising and says users may manage or delete cookies. This is a description of use, **not an explicit claim of GDPR compliance** in the reviewed policy. The exact homepage's product-specific policy and EU-facing variant still need checking. Policy text alone cannot prove which cookies the homepage set in this session.

Under the [ePrivacy Directive Article 5(3)](https://eur-lex.europa.eu/eli/dir/2002/58/oj), storing or accessing device information generally calls for prior informed consent, subject to narrow technical necessity exceptions. The [EDPB cookie banner task force report](https://www.edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf) discusses rejection and choice design. Do not infer that every cookie is optional, or that a site outside the EU is automatically covered in every circumstance.

| Question | Pilot observation | Status |
| --- | --- | --- |
| Does the policy describe cookies? | Yes: operation, statistics, personalization and partner services. | Observed in policy |
| Does this policy explicitly claim GDPR compliance? | No explicit claim found in the reviewed general policy. | Limited to this policy |
| Is a banner visible on initial homepage load? | None apparent in the observed browser view. | Observed, location unverified |
| Are optional cookies set before consent? | Full cookie and network evidence unavailable. | Inconclusive |
| Can the user reject and later withdraw consent? | No controlled interaction run. | Inconclusive |
| Is GDPR/ePrivacy applicable to this particular visit? | EU network location and targeting not established. | Inconclusive |

## Reproduce and complete the test

1. On a machine with network access to Playwright's browser download, run `pip install -r requirements.txt` and `python -m playwright install chromium`.
2. Confirm and record the **actual public IP country** (use an authorized EU network exit if testing EU users). Also record browser version, test time, language, redirect URL and whether the site served a different regional version. A Brussels timezone does not change the network location.
3. Run `python collect.py --domain baidu.com`. This captures the initial, no-interaction screenshot and `results/084_baidu.com/evidence.json`. The raw evidence may contain session values and must remain private; `results/` is ignored by Git.
4. Inspect every cookie's domain, expiry and likely purpose against the specific policy. Verify whether any nonessential storage or tracking request appears **before** a choice. A request or unfamiliar name alone is insufficient evidence of tracking.
5. If a consent interface appears, use fresh independent contexts for **reject**, **accept**, and **withdraw**; compare cookies, storage, third-party traffic and screenshots after the same wait. Record exact clicks and times. If there is no interface, record this and check whether optional storage occurred; do not invent accept/reject results.
6. For each criterion, write `pass`, `potential_issue`, `inconclusive` or `not_applicable` with the evidence path and explanation. Have a person verify the policy excerpts and classification.

This repository's collector currently implements step 3 only. Steps 4–6 need manual review and additional controlled collection before a defensible conclusion.
