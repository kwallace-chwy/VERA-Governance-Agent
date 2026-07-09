# Runbook

## Prerequisites

- Approved access to the VOC Board source table or approved CSV export.
- Python 3.10+ for local CSV runs.
- Snowflake role with read access to the source table.
- Approved storage location for outputs.

## Snowflake run

1. Open a Snowflake worksheet.
2. Run:

`sql/vera_voc_board_audit_view.sql`

3. Validate row counts:

```sql
SELECT
    COUNT(*) AS total_comments,
    COUNT_IF(FLAG_REVIEW_CANDIDATE) AS review_candidates,
    ROUND(COUNT_IF(FLAG_REVIEW_CANDIDATE) / NULLIF(COUNT(*), 0), 4) AS candidate_rate
FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.VERA_VOC_BOARD_AUDIT_VW;
```

4. Run:

`sql/vera_voc_board_audit_rollup.sql`

5. For approved reviewers only, run:

`sql/vera_voc_board_candidate_export.sql`

## Local CSV run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run redacted output:

```powershell
python src/vera_voc_analysis.py --input C:\path\to\VOC.csv --output-dir local_outputs
```

Run restricted unredacted output:

```powershell
python src/vera_voc_analysis.py --input C:\path\to\VOC.csv --output-dir restricted_outputs --include-raw
```

## Current-process comparison run

Use this when comparing VERA to the current daily ER escalation email export.

```powershell
python src/compare_current_vs_vera.py --current-export C:\path\to\ER_Risk.csv --vera-output C:\path\to\vera_voc_board_audit_view_output_unredacted.csv --output-dir restricted_comparison_outputs --include-raw-html
```

The comparison runner aligns VERA to the current export date window by default. It produces:

- `current_vs_vera_summary.csv`
- `current_rows_with_vera_match.csv`
- `current_only_vera_not_flagged.csv`
- `current_unmatched_to_vera_source.csv`
- `vera_only_candidates.csv`
- `ai_edge_review_queue.csv`
- `current_vs_vera_comparison_report.html`

Use the actual ER export as the measurement baseline when available. The provided SQL regex is useful for design, but the export may include additional risky words.

## Expected outputs

Redacted mode:

- `vera_voc_board_audit_view_output_redacted.csv`
- `vera_voc_board_audit_view_candidates_redacted.csv`
- `vera_voc_review_workbook_redacted.xlsx`
- `vera_voc_board_review_redacted.html`

Restricted unredacted mode:

- `vera_voc_board_audit_view_output_unredacted.csv`
- `vera_voc_board_audit_view_candidates_unredacted.csv`
- `vera_voc_review_workbook_unredacted.xlsx`
- `vera_voc_board_review_unredacted.html`

## Validation checklist

- Total row count matches expected source filter.
- Candidate count matches summary.
- Candidate flag sum equals candidate-only row count.
- All outputs include method version.
- All outputs include run timestamp.
- Redacted outputs do not include raw comment text.
- Unredacted outputs are stored only in approved restricted locations.
- Reviewer packet contains comments and responses when needed.

## Common issues

Missing source fields:

- Confirm the CSV export includes `LOCATION`, `DATE_POSTED`, and `FEEDBACK`.

Unexpected candidate count:

- Confirm the method version and taxonomy file.
- Confirm date window and excluded locations.
- Confirm the source file is VOC Board only or includes a `VOICE_MECHANISM` field.

Raw text appearing in redacted output:

- Stop distribution.
- Delete the output from broad-access storage.
- Rerun without `--include-raw`.
- Notify the product owner and data owner.

## Release checklist

Before sharing outputs:

- Confirm audience.
- Confirm redacted vs unredacted need.
- Confirm storage location.
- Confirm method version.
- Confirm run date and source window.
- Confirm caveat language is present.
- For current-process comparisons, confirm date-window alignment and whether raw text is included in the HTML report.
