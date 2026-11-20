# FTMJ initial data model

FTMJ uses the standard FollowTheMoney entities that already describe the first data we need. It avoids a Jackson-only custom schema until actual City Clerk report formats show that a custom type is necessary.

| FTMJ concept | FtM schema | Relationship or properties |
|---|---|---|
| Candidate or individual donor/payee | `Person` | `name`; matching is not performed automatically |
| Campaign committee, organization donor, or vendor | `Organization` | `name` |
| Campaign receipt or expenditure | `Payment` | `payer`, `beneficiary`, `date`, `amount`, `purpose`, `recordId`, `sourceUrl`, `publisher`, and source-page note in `description` |
| City office and officeholder term (next phase) | `Position` and `Occupancy` | Position identifies the office; occupancy links a person to it over a dated term |
| City procurement (later phase) | `Contract` and `ContractAward` | Contract and supplier award, linked to organizations |

For a contribution, the donor is the payer and the committee is the beneficiary. For an expenditure, the committee is the payer and the recipient is the beneficiary. Transaction direction follows the filing; it does not imply impropriety.

## Identity policy

Name-only deduplication is unsafe for people who share common names. The importer therefore creates party identifiers scoped to a filing unless a reviewer supplies a stable `donor_key`, `recipient_key`, or `committee_key`. Cross-report identity links should be curated and backed by identifiers or corroborating evidence, with the original source spelling retained.

## Provenance policy

The original filing remains the source of truth. Every imported transaction carries the report identifier, filing source URL if known, local clerk as publisher, transaction record ID, and page note. The intake register should separately track the source file's checksum, retrieval timestamp, and reviewer status. Corrections should be stored as new reviewed versions, not silently written over the transcription.

## Coverage and uncertainty

An empty or missing record is not evidence that no transaction occurred. Reports can be incomplete, handwritten, filed on paper, or difficult to read. FTMJ should expose coverage by office, reporting period, and source status so users can see what has and has not been reviewed.
