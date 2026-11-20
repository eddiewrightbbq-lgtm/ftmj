# FTMJ initial data model

FTMJ uses standard FollowTheMoney (FtM) entities for the graph and keeps filing-specific fields in a structured report register. This avoids inventing a Jackson-only graph schema before the first current forms have been reviewed.

| FTMJ concept | FtM schema | Relationship or properties |
|---|---|---|
| Elected official or candidate | `Person` | Source-backed name; a candidate is not assumed to hold office |
| Campaign committee, PAC, organization donor, or vendor | `Organization` | Name and only source-supported identifiers |
| Municipal government | `PublicBody` | City of Jackson as the authority for municipal offices |
| Mayor or council seat | `Position` | One position per office/ward as needed |
| Person holding a city office | `Occupancy` | Links a `Person` to a `Position` over the verified term dates |
| Campaign receipt or expenditure | `Payment` | `payer`, `beneficiary`, `date`, `amount`, `purpose`, `recordId`, `sourceUrl`, `publisher`, and page reference |

For a receipt, the donor is the payer and the candidate committee is the beneficiary. For a disbursement, the committee is the payer and the recipient is the beneficiary. The transaction direction follows the filing and does not imply impropriety. FtM defines `Payment` as a monetary payment between parties; preserve source-specific categories such as loan and in-kind separately in the filing register rather than silently treating them as ordinary cash contributions.

## Filing register and analytical tables

The campaign report is the source record; individual payment rows are children of that report. Keep report fields in a normalized filing table (for example, in BigQuery), then export the verified parties and payments as FtM JSON:

- **Filing:** `report_id`, candidate/committee, office sought, election cycle, report type, period start/end, received/filed date, amendment status, original source URI, SHA-256, page count, clerk/source office, coverage status, and review status.
- **Receipt:** transaction ID, transaction date, amount this period, source category, donor name/type, reported employer/occupation only when needed, year-to-date aggregate, report ID, and page.
- **Disbursement:** transaction ID, date, amount, recipient name/type, purpose, year-to-date aggregate, report ID, and page.
- **Summary totals:** itemized/non-itemized totals, total receipts, total disbursements, and cash on hand remain report-period facts. Do not manufacture payment entities from report summary totals.

City Clerk filings can contain personal addresses. Keep originals in private source storage; omit donor mailing addresses from the public dataset by default. Employer and occupation values are source-reported text, not verified facts about a person. Never infer missing identity, employer, occupation, or relationship information.

## Identity policy

Name-only deduplication is unsafe for people with common names. The importer creates party identifiers scoped to a filing unless a reviewer supplies a stable key supported by evidence. Keep the original source spelling and curate cross-report links from stable identifiers or corroborating sources. Candidate identity and committee identity are separate entities.

## Provenance and review policy

The original filing remains the source of truth. Each extracted transaction must point to its report and source page. Preserve the original PDF unchanged, record its checksum and retrieval/receipt dates, and track the reviewer and corrections. OCR is a draft, not verification. Keep `not_found`, `not_yet_posted`, and `request_pending` distinct from a zero-activity filing or an explicit zero report.

## Coverage and uncertainty

Municipal campaign-finance filings are paper-submitted to the City Clerk, while the Mississippi Secretary of State search only indexes electronically filed reports. The City Clerk's public archive currently exposes 2017–2018 report PDFs. Therefore, FTMJ must track collection coverage by candidate/committee, office, election cycle, and reporting period. A missing online file is not evidence that a report was never filed or that no money moved.

See [source-landscape.md](source-landscape.md) for current source access and intake implications.
