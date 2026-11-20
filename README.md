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

Start from `data/transaction_template.csv`. Keep one row per itemized receipt or expenditure and preserve the original filing separately. For contributions, fill the donor fields and leave recipient fields blank; for expenditures, fill the recipient fields and leave donor fields blank. Do not use OCR output as final data until a person has reviewed it against the source page.

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

## Next implementation steps

1. Confirm the exact GCP project ID and create the source-document bucket and restricted staging environment.
2. Obtain an initial batch of Jackson Municipal Clerk campaign-finance reports and record their provenance.
3. Transcribe a small batch into the CSV template, compare every value to its source page, and refine the fields based on actual Jackson forms.
4. Add the local-report and office/term model only after the first filings show which custom fields are needed.
5. Build OCR-assisted intake and a searchable review interface; human review remains required before publication.

## License and upstream model

FtM is maintained by OpenSanctions and is MIT licensed. This starter is an independent Jackson-focused project that uses the FtM package; it is not affiliated with or endorsed by OpenSanctions, FollowTheMoney.org, the City of Jackson, or the Mississippi Secretary of State.
