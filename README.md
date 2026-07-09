# VERA Governance Agent

**A governed agentic AI workflow for employee voice review**

**Turning employee voice into earlier support and stronger follow-through.**

VERA helps HR Compliance, Employee Relations, and Labor Relations understand what Team Members are raising through VOC Board feedback and where sites may need additional support. By organizing open-ended comments into governed review categories and surfacing emerging themes for human review, VERA helps teams route the right partners, monitor follow-through, and distinguish isolated concerns from broader trends.

The result is faster visibility, clearer ownership, and a more consistent way to support positive employee relations while keeping the employee experience at the center of the work.

## What VERA does

VERA is not a legal decision-maker and does not determine whether a concern is substantiated. It is a governed review workflow that:

- Applies deterministic review domains to VOC Board comments.
- Separates HR Compliance, Labor Relations, Safety/EHS, Legal, executive escalation, and broader ER trend signals.
- Produces a review queue with reason codes, priority routing, and audit metadata.
- Supports human review, reviewer labeling, follow-through monitoring, and model/prompt governance.
- Creates a gold standard dataset for future agent evaluation and drift monitoring.

## Why this matters

The current review process relies heavily on keyword searching and manual review. That is valuable, but it can be hard to explain, hard to measure, and hard to scale across every feedback cycle.

VERA adds business value by making the review process more consistent and measurable:

- Earlier visibility into issues that may need site or functional support.
- Clearer routing for Compliance, ER, Labor Relations, Safety/EHS, Legal, and site HR partners.
- Better distinction between isolated comments and recurring site or topic trends.
- More consistent documentation of why an item was surfaced.
- A foundation for human-labeled evaluation, precision/recall monitoring, and controlled future agent automation.

## Repository map

| Path | Purpose |
| --- | --- |
| `docs/PRD.md` | Product requirements, business problem, stakeholder value, scope, and roadmap. |
| `docs/METHODOLOGY.md` | VOC audit methodology, review domains, priority rules, and measurement approach. |
| `docs/GOVERNANCE_SECURITY.md` | Governance, access, privacy, retention, human review, and security controls. |
| `docs/AGENT_FRAMEWORK.md` | Agent architecture, workflow, tools, output contracts, and Phoenix integration notes. |
| `docs/SUCCESS_METRICS_AND_EVALS.md` | Success measures, gold standard strategy, and monitoring plan. |
| `docs/OPERATING_MODEL.md` | Roles, responsibilities, RACI, and review cadence. |
| `docs/STAKEHOLDER_BRIEF.md` | Stakeholder-facing summary for HR, Compliance, ER, LR, Legal, and HR leadership. |
| `docs/RUNBOOK.md` | Step-by-step run instructions for Snowflake and local CSV review. |
| `docs/BUILD_CHECKLIST.md` | Implementation checklist from foundation through launch. |
| `sql/` | Snowflake view and aggregate report SQL. |
| `src/` | Local audit runner for exported CSVs. |
| `config/vera_taxonomy.yml` | Governed review domains, regex patterns, and priority rules. |
| `prompts/` | Agent persona and system prompt scaffold. |
| `evals/` | Gold standard template, labeling guide, and Arize monitoring plan. |
| `examples/` | Fictional sample input and expected output for testing. |
| `outputs/` | Placeholder only. Real outputs should not be committed unless explicitly approved. |
| `data/` | Placeholder only. Raw VOC exports should not be committed. |

## Quick start

### Snowflake view

Run the view in:

`sql/vera_voc_board_audit_view.sql`

Then use:

`sql/vera_voc_board_audit_rollup.sql`

to produce domain, routing, site, and monthly rollups.

### Local CSV run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run a redacted review package:

```powershell
python src/vera_voc_analysis.py --input path\to\VOC.csv --output-dir local_outputs
```

Run a restricted unredacted review package:

```powershell
python src/vera_voc_analysis.py --input path\to\VOC.csv --output-dir restricted_outputs --include-raw
```

## Data handling position

Do not commit raw VOC comments, unredacted review queues, or identifiable employee details to this repository without explicit approval from the appropriate data owner, HR Compliance, Legal, and repository administrators.

This repo is designed to hold the product, governance, method, SQL, prompts, eval templates, and fictional examples. Production outputs should live in approved Snowflake locations, controlled SharePoint folders, or another approved restricted-access system.

## Current baseline

The July 9, 2026 Snowflake CSV run produced:

- 6,085 VOC Board comments analyzed.
- 423 VERA review candidates.
- 69 Priority 1 candidates.
- 238 Priority 2 candidates.
- 116 Priority 3 candidates.

Those counts are included here as historical run context only. The repo does not include the unredacted comments from that run.

## Guardrail

VERA supports human review. It does not make legal conclusions, employment decisions, disciplinary decisions, or findings of substantiation.
