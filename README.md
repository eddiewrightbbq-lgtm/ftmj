# FTMJ — Follow the Money Jackson

An initial data ingestion package for structuring publicly filed Jackson, Mississippi campaign-finance records using the OpenSanctions FollowTheMoney (FtM) model.

## Current scope

- Convert a reviewed CSV transcription of campaign transactions into newline-delimited FollowTheMoney entities (`.ijson`).
- Represent donors, campaign committees, vendors, and payments with the standard FtM `Person`, `Organization`, and `Payment` schemas.
- Preserve a filing reference on each payment (`sourceUrl`, `publisher`, `recordId`, and optional source page in the description).
- Keep identity matching conservative: people and organizations are scoped to a report unless a reviewer supplies a stable `*_key` across reports. Names alone are not treated as proof that two records refer to the same person.

This is a starter for the data model and intake workflow. It does not yet collect records from the City Clerk, perform OCR, create a GCP resource, or publish a public-facing site.

## Setup

Python 3.10 or newer is required. FollowTheMoney's Python package uses ICU support for some text-normalization functions; see its installation guide if package installation reports an ICU or `pyicu` error.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
ftmj --help
```

## Convert a reviewed transaction CSV

Start with `data/filing_template.csv` for one row per report, then use `data/transaction_template.csv` for one row per itemized receipt or expenditure. Keep the original filing separately. For contributions, fill the donor fields and leave recipient fields blank; for expenditures, fill the recipient fields and leave donor fields blank. The importer accepts only transaction rows marked `reviewed`; do not use OCR output as final data until a person has checked it against the source page.

```bash
ftmj import-transactions data/transaction_template.csv --output data/transactions.ijson
```

The command rejects missing required fields and malformed amounts/dates instead of silently dropping or guessing them. If a donor/payee cannot be classified confidently as an individual or organization, resolve that in the review spreadsheet before import.

## FtM validation

The generated stream can be inspected and validated with the FtM CLI:

```bash
ftm validate -i data/transactions.ijson -o data/transactions.validated.ijson
```

## Data handling rules

1. Retain each acquired filing unchanged and record its retrieval date, source office, and file checksum in the intake register.
2. Keep a source URL or stable source-document reference on each extracted record and capture a page number when available.
3. Distinguish what a filing says from an analyst's interpretation. Do not label an association as a conflict, violation, or wrongdoing without separately verified evidence.
4. Store only facts needed for the public-interest research. Do not infer home addresses, family connections, or identities from name similarity alone.
5. Keep corrections traceable to the source filing and reviewer.

## Project status and next steps

- GCP project: `ftmj-515313`; the Codex identity connection has passed a read-only project verification.
- GitHub starter: [`eddiewrightbbq-lgtm/ftmj`](https://github.com/eddiewrightbbq-lgtm/ftmj).
- GCP architecture: proposed, not provisioned. See [`docs/gcp-architecture.md`](docs/gcp-architecture.md).
- Municipal campaign-finance source coverage: documented in [`docs/source-landscape.md`](docs/source-landscape.md).

1. Obtain a small sample of Jackson Municipal Clerk campaign-finance reports and register their provenance.
2. Transcribe a small batch into the CSV template, compare every value to its source page, and refine fields against actual Jackson forms.
3. Review the proposed Cloud Storage and BigQuery design and grant only the needed resource-level permissions.
4. Provision the selected resources after the design and billing controls are agreed.
5. Add local-office and officeholder-term records after source documents for those records are identified and reviewed. Add a public review interface only after the intake process is established.

## License and upstream model

FtM is maintained by OpenSanctions and is MIT licensed. This starter is an independent Jackson-focused project that uses the FtM package; it is not affiliated with or endorsed by OpenSanctions, FollowTheMoney.org, the City of Jackson, or the Mississippi Secretary of State.

