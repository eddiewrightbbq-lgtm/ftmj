# FTMJ source landscape — Jackson municipal campaign finance

**Checked:** 2026-11-20  
**Scope:** Jackson, Mississippi municipal candidates, officeholders, campaign committees, and itemized campaign transactions.

## What is digitally available

- Mississippi law routes campaign-finance filings for municipal candidates, their committees, and municipal political committees to the Municipal Clerk. The Secretary of State says county and municipal reports may only be filed on paper with the relevant clerk. Paper reports can be emailed, faxed, hand-delivered, or mailed; the applicable deadline is receipt by 5:00 p.m. (See the [Mississippi Secretary of State campaign-finance page](https://www.sos.ms.gov/elections-voting/campaign-finance).)
- The Secretary of State campaign-finance portal currently says its online filing system is disabled because of systemic reliability issues. Its public search covers records filed electronically; it says manually filed paper reports are not searchable by candidate, office, contribution, or expenditure. The portal also warns that converted searchable information can contain errors and directs users to the actual report for confirmation. (See the [portal notice](https://cfportal.sos.ms.gov/online/portal.aspx) and [public-search information](https://cfportal.sos.ms.gov/online/portal/cf/page/cf-search/Portal.aspx).)
- The City Clerk campaign-finance page is a digital archive of linked report PDFs. The page says reports are posted as received, but the currently visible archive lists 2017 and 2018 material. It is useful as an initial source, but it is not evidence of complete current coverage. (See the [City Clerk campaign-finance archive](https://cityclerkjxn.wixsite.com/cityclerk/campaign-finance-reports).)
- A sample PDF from that archive is a scanned, six-page “Report of Receipts and Disbursements.” It includes candidate/committee, office sought, election cycle, report type, reporting period, summary totals, itemized receipts, and itemized disbursements. Individual receipt rows can include source category, date, amount, donor name, mailing address, employer, occupation, and year-to-date aggregate. Disbursement rows include recipient, date, amount, address, purpose, and year-to-date aggregate. Treat it as a 2017 sample; confirm the current form and fields against current filings. ([Sample City Clerk report PDF](https://a11f31a6-6518-463d-8584-8b066daaba00.filesusr.com/ugd/3ac5ae_4d4060f9bd5849e2a68b37784c8b5de9.pdf).)

A 2025 news investigation reported that a public-records request did not produce all reports sought and that some reports were obtained in person. This is a warning about coverage and records access, not a source for transaction-level values. (See [Mississippi Today’s 2025 reporting](https://mississippitoday.org/2025/04/03/financial-interests-in-the-jackson-municipal-elections/).)

## Intake implications

1. Use the official City Clerk archive and actual filing PDFs as source documents. Use the Secretary of State public search as a supplementary discovery tool, not as a complete inventory of municipal filings.
2. For each requested time range, track the expected filing set and the reports actually obtained. Record `not_found`, `not_yet_posted`, `request_pending`, `received_paper`, and `received_digital` as distinct statuses; absence from a portal does not mean no report was filed.
3. When requesting records, ask for reports by candidate/committee, report type, reporting period, receipt date, and amendments. Preserve the clerk's received or stamped date when present.
4. Keep the original PDF or scan unchanged, calculate a SHA-256 checksum, and link every transcription to its report ID and page. Record OCR as a draft only; verify each transaction against the source page.
5. Do not use news summaries or portal-converted values as substitutes for the underlying report. Record them only as leads to documents.

## Data-model implications

- Keep report-level fields separately from transaction-level payments: candidate or committee, office sought, election cycle, report type, period start/end, filed/received date, amendment status, summary totals, and coverage status.
- Represent the candidate and committee as `Person` and `Organization`; represent an itemized receipt or disbursement as a `Payment` with the payer and beneficiary set according to the filing direction.
- Preserve the filing's source category (individual, PAC, corporation, loan, in-kind, or other) and the original line/page reference as source metadata. Do not silently classify loans or in-kind entries as ordinary cash contributions.
- Store donor employer/occupation as source-reported text only if the project has a documented use for it. Do not infer employers or occupations. Avoid publishing donor mailing addresses by default; preserve the untouched source document and decide separately whether any address field is necessary and appropriate for the public dataset.
- Build officeholder history from official election results and term dates, using `Position` and `Occupancy` in the FtM graph. Keep election candidacy separate from holding office.

## Primary references

- [Mississippi campaign-finance rules and filing locations](https://www.sos.ms.gov/elections-voting/campaign-finance)
- [Mississippi campaign-finance portal notice](https://cfportal.sos.ms.gov/online/portal.aspx)
- [Mississippi campaign-finance public-search scope and reliability notice](https://cfportal.sos.ms.gov/online/portal/cf/page/cf-search/Portal.aspx)
- [Jackson City Clerk archive](https://cityclerkjxn.wixsite.com/cityclerk/campaign-finance-reports)
- [FollowTheMoney `Payment` schema](https://followthemoney.tech/explorer/schemata/Payment/)
