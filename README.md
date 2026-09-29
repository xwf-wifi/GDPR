# Tranco Top 100 Cookie Consent Study

This repository contains a reproducible sample and a browser evidence collector for studying cookie consent on the Tranco top 100 domains. It does **not** issue automated legal verdicts. A domain may be an API, CDN, inaccessible page, or serve different content by location. The committed Tranco archive is list **64X3X**, not a live ranking; preserve that ID and the collection date in reports.

## Start on Windows

### Desktop window for teammates

The no-code path is the `GDPR-Research-Windows-v3` ZIP attached to a successful **Build Windows desktop app** GitHub Actions run. Download and extract the whole ZIP into a new writable folder, then double-click `GDPR-Research-v3.exe`. The package is built on Windows and bundles Chromium; teammates do not need to install Python or run commands. The workflow downloads and tests its own artifact, including Chromium; a hands-on Windows website collection test is still needed before group distribution.

### Mac app

The **Build macOS desktop app** workflow offers two archives: `GDPR-Research-Mac-Apple-Silicon` for M-series Macs and `GDPR-Research-Mac-Intel` for Intel Macs. Download the matching artifact, extract the outer GitHub ZIP and then the enclosed `GDPR-Research-Mac-*.zip` using Archive Utility. Open `GDPR-Research-Mac.app` from Finder. The app saves its workbook and evidence under `~/Documents/GDPR-Research/`, outside the app bundle. It includes its own Chromium and Python dependencies. The build is not signed with an Apple Developer ID or notarized; macOS may block first launch. Only if you trust the downloaded app, follow Apple's **System Settings → Privacy & Security → Open Anyway** guidance. The CI checks the extracted archive and launches the bundled browser, but an actual Finder launch and live site collection on a teammate's Mac still need testing.

Enter a Tranco top-100 domain or homepage URL, click **采集网站**, inspect the screenshot, fill the policy claim and Cookie purpose fields, then click the save buttons. **打开工作簿** opens the local `reports/GDPR_review.xlsx`. The app visits the domain homepage; URL paths are not part of this first pilot. It only implements the initial no-interaction visit. Data remains inside the extracted folder, and team members' separate copies do not sync automatically.

For the current source version, install once with `setup.cmd` and then double-click `启动工具.cmd` to open the same interface. The command-line alternative remains available for troubleshooting.

### Command-line fallback

Install Python, clone the repository, then open CMD inside the project folder:

```cmd
setup.cmd
run.cmd baidu.com
```

`setup.cmd` installs the Python packages and Chromium once. `run.cmd DOMAIN` collects one exact domain in the Tranco sample and refreshes `reports/GDPR_review.xlsx`. Open that **one workbook** to inspect the screenshot, website row and Cookie details. To refresh the workbook without visiting another site, run `.venv\Scripts\python.exe export_workbook.py`. The exporter keeps the human-edited claim and classification columns when it rebuilds the workbook. Close the workbook in Excel before refreshing it.

For a five-site pilot, run `run.cmd google.com`, `run.cmd cloudflare.com`, `run.cmd microsoft.com`, `run.cmd wikipedia.org`, and `run.cmd baidu.com` one at a time. Check every screenshot for error pages and verify the site row before progressing to the full sample. If the browser is blocked or the page fails, record that outcome rather than calling it compliant or noncompliant.

## Python/Linux alternative

```bash
python prepare_sites.py
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python collect.py --domain baidu.com
python export_workbook.py
```

`data/top100.json` records the exact original ranks. `results/001_google.com/evidence.json` and `initial.png` contain evidence from a fresh browser context. Run `python collect.py --limit 100` once the pilot and location are configured. The collector does not click on banners; that is deliberate for the initial pre-consent observation. `results/` is ignored by Git because page text and cookies can contain personal or session data. Review and redact evidence before sharing it.

For the Baidu pilot, `python analyze.py results/084_baidu.com/evidence.json` can print a redacted diagnostic summary. The workbook is the team's main record. It contains 100 site rows, a Cookie detail sheet, and compressed screenshot previews. Claim fields and cookie purposes are blank or marked unreviewed until a teammate checks the policy and evidence. The workbook excludes cookie values and full request URLs. See `demos/baidu.md` for the remaining steps.

Evidence collected before the response-header fix lacks `set_cookie_detection`. For those files the analyzer reports the `Set-Cookie` response count as unknown, even if the old collector recorded zero. Re-run collection with the current script to measure that field.

## Team review in the workbook

Fill the yellow columns on the website sheet with the policy URL, a short verified GDPR claim excerpt (if one exists), its source URL, the date, the observed consent interface and an evidence-based assessment. On the Cookie sheet, fill purpose, supporting source and classification only after checking them. Re-running `run.cmd` preserves these manual fields using the site rank/domain and Cookie identity. It refreshes observations and thumbnails from the latest local evidence. Do not edit identifiers such as rank, domain, Cookie name or path to store review notes; those columns are rebuilt from the source.

The collector currently captures only the initial, no-interaction scenario. The rejection, acceptance and withdrawal scenarios, policy discovery and LLM assistance remain future work. A Cookie name, screenshot or request hostname alone cannot establish a legal violation. Raw `results/` files can contain session values and stay local; review even the workbook before sharing its screenshots.

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
