# FTMJ filing intake workflow

1. Request or collect public campaign-finance reports from the Jackson Municipal Clerk.
2. Save each original file unchanged. Record office, filer, reporting period, receipt date, retrieval date, filename, and SHA-256 checksum in the intake register.
3. Create a transcription row per itemized receipt or expenditure using `data/transaction_template.csv`.
4. Mark unclear handwriting, ambiguous names, and missing fields for manual review. Do not infer a missing value.
5. Have a second reviewer compare every transcribed row with the filing page. Retain the original spelling and amount.
6. Import the reviewed CSV with `ftmj import-transactions`.
7. Validate the resulting `.ijson` with `ftm validate` before adding it to a staging dataset.
8. Publish only reviewed records with visible source citations and coverage notes.

## Review labels

- `unreviewed`: machine or first-pass transcription only.
- `reviewed`: checked against the cited page by a human.
- `corrected`: changed after review, with reason and reviewer recorded in the intake register.
- `unreadable`: source is retained, but a reliable transcription was not possible.

Do not treat OCR confidence as source verification.
