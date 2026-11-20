# FTMJ GCP architecture — proposed first phase

**Project:** `ftmj-515313`  
**Status:** Design only. No GCP resources were created by this plan.

## Recommendation

Start with two data services, and defer the application runtime:

1. **Cloud Storage** holds the original campaign-finance filings and reviewed exports. Keep the bucket private, enable uniform bucket-level access, and prevent public access. Preserve each original unchanged and record its SHA-256 digest, retrieval date, source office, and review status in the intake register.
2. **BigQuery** holds the structured, reviewable records used for analysis. Keep separate staging and curated datasets. Load only human-reviewed transactions into curated tables. Export FollowTheMoney `.ijson` streams for interchange and validation; treat the normalized tables as the analytical representation.
3. **Cloud Run** is deferred. The current CLI can support the first intake workflow without a hosted service. Add Cloud Run only when FTMJ needs a review API or web interface.

Cloud SQL is not needed for this first phase. It would add a separate database service before the project has demonstrated a transactional application need.

## Initial logical tables

| Table | Purpose | Important fields |
|---|---|---|
| `filings` | Filing-level source register | `report_id`, office, filer/committee, reporting period, source URI, retrieval time, SHA-256, reviewer, review status |
| `parties` | People and organizations from filings | stable internal ID, FtM schema (`Person` or `Organization`), source name, reviewed type, optional curated cross-report key |
| `payments` | Itemized receipts and expenditures | transaction ID, date, exact amount, payer ID, beneficiary ID, purpose, filing ID, source page, review status |
| `review_events` | Auditable transcription corrections | record ID, field, prior value, corrected value, reason, reviewer, timestamp, source page |

The first FtM mapping remains `Person`, `Organization`, and `Payment`. Add `Position` and `Occupancy` for elected offices and terms after the initial filing sources and officeholder records are collected and reviewed. Do not merge people by name alone.

## Access plan for `ftmj-codex`

The Workload Identity User grant only permits the Codex identity to impersonate the service account. It does not itself grant access to project data or resources. Add resource permissions only for the stage being performed.

| Stage | Least-privilege access to consider |
|---|---|
| Inspect project and APIs | Project-level `roles/serviceusage.serviceUsageViewer` only if API inventory is needed |
| Read source filings | Bucket-level `roles/storage.objectViewer` |
| Upload source or reviewed files | Bucket-level `roles/storage.objectCreator`; add viewer only if the workflow must list/read objects |
| Query BigQuery tables | Dataset-level `roles/bigquery.dataViewer` plus project-level `roles/bigquery.jobUser` |
| Create or update tables during ingestion | Dataset-level `roles/bigquery.dataEditor` plus project-level `roles/bigquery.jobUser` |
| Deploy a later Cloud Run service | Grant deployment and runtime-service-account permissions only when that service is approved and defined |

Avoid project-wide `Editor`, `Owner`, or broad storage administration for routine ingestion. Keep the raw source bucket private even when the underlying filings are public; publish reviewed records separately with source citations and coverage notes.

## Cost and change controls

- Use BigQuery on-demand analysis for the small initial dataset, with a maximum-bytes-billed setting and query quotas or billing alerts before routine use.
- Avoid a BigQuery capacity reservation until measured usage justifies one.
- Defer Cloud Run, Cloud SQL, OCR services, scheduled jobs, and public hosting until a specific workflow requires them.
- Before provisioning, confirm the billing account, region, retention period, bucket name, and whether the public-facing data will be hosted separately.

## Next steps

1. Review and refine the data fields against actual Jackson Municipal Clerk filing forms.
2. Acquire a small sample of source filings and register their provenance.
3. Transcribe and review a small batch; refine the CSV and FtM mapping from evidence.
4. Decide the final BigQuery schema and dataset permissions from the reviewed sample.
5. Provision only the selected resources after the design is approved.

## Google Cloud references

- [Cloud Storage IAM access control](https://cloud.google.com/storage/docs/access-control)
- [BigQuery cost controls](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [BigQuery IAM roles](https://cloud.google.com/bigquery/docs/access-control)
- [Cloud Run overview](https://cloud.google.com/run/docs/overview/what-is-cloud-run)
- [Workload Identity Federation service-account access](https://cloud.google.com/iam/docs/workload-identity-federation-with-other-providers)
