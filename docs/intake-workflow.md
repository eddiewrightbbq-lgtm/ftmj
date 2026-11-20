# FTMJ filing intake workflow

1. Request or collect public campaign-finance reports from the Jackson Municipal Clerk.
2. Save each original file unchanged. Record office, filer, reporting period, receipt date, retrieval date, filename, and SHA-256 checksum in the intake register.
3. Create one filing-register row using `data/filing_template.csv`, then one transcription row per itemized receipt or expenditure using `data/transaction_template.csv`. Link every transaction with the exact `report_id`.
4. Mark unclear handwriting, ambiguous names, and missing fields for manual review. Do not infer a missing value.
5. Have a second reviewer compare every transcribed row with the filing page. Retain the original spelling and amount.
6. Set each transaction row to `reviewed` only after comparison to its source page. The importer rejects rows with any other review status.
7. Validate the resulting `.ijson` with `ftm validate` before adding it to a staging dataset.
8. Publish only reviewed records with visible source citations and coverage notes.

## Review labels

- `unreviewed`: machine or first-pass transcription only.
- `reviewed`: checked against the cited page by a human.
- `corrected`: changed after review, with reason and reviewer recorded in the intake register.
- `unreadable`: source is retained, but a reliable transcription was not possible.

Do not treat OCR confidence as source verification.

## Field handling

- The filing template records report-level summary totals; do not turn those totals into transaction rows.
- The transaction template records the form's source category and source line when available. Preserve categories such as `loan` and `in_kind`; do not recast those as ordinary cash contributions. Confirm classification against the actual form and retain source wording.
- The templates intentionally omit donor and recipient mailing addresses. Keep the original filing in restricted storage; add personal address fields only if there is a documented need and a separate publication review.
- Keep the filing template's checksum, source URI, retrieval metadata, coverage status, and review status attached to the original report.

