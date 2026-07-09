# Governance and security methodology

## Governance position

VERA is a governed review workflow for sensitive employee voice data. It is designed to help approved HR partners find comments that may need human attention sooner and with more consistent documentation.

VERA does not:

- Make legal conclusions.
- Determine whether a complaint is substantiated.
- Recommend discipline.
- Replace HR Compliance, Employee Relations, Labor Relations, Legal, or Safety/EHS review.
- Automatically notify leaders or Team Members.

## Data classification

VOC Board comments may include sensitive employment concerns, protected-class references, safety issues, protected activity, names, locations, or other identifying details.

Treat raw VOC comments and unredacted outputs as restricted HR data.

## Repository data rule

This repository should contain:

- Product documentation.
- Governance methodology.
- SQL.
- Runner code.
- Prompt templates.
- Evaluation templates.
- Fictional sample data.

This repository should not contain by default:

- Raw VOC Board exports.
- Unredacted comments.
- Employee identifiers.
- Full review packets with raw text.
- Reviewer notes from live investigations.
- Files that could reveal confidential HR matters.

## Access model

Recommended access tiers:

| Tier | Audience | Allowed content |
| --- | --- | --- |
| Broad stakeholder | HR leadership, ORBIT, HREPA, site HR leadership | Aggregate counts, trends, methodology, redacted outputs. |
| Reviewer | HR Compliance, ER, LR, Legal, Safety/EHS as approved | Candidate rows with raw comments and responses. |
| Administrator | Product owner, data owner, assigned engineer | Source SQL, execution logs, taxonomy, version control, controlled outputs. |
| Auditor | Data Governance, Legal, Security, HR Compliance leadership | Run history, labels, QA, access records, retention checks. |

## Raw data handling

Raw comment text should remain in approved systems:

- Snowflake governed tables or views.
- Restricted SharePoint or equivalent controlled folders.
- Approved ER/Compliance case management systems, if applicable.

Raw text should not be copied into:

- Public channels.
- Broad Slack channels.
- Unrestricted documents.
- GitHub repos unless specifically approved.
- Model prompts outside approved enterprise AI paths.

## Human-in-the-loop controls

All Priority 1 candidates require human review before action.

All AI-generated summaries, explanations, or routing suggestions must be reviewer-confirmed before use.

Reviewers must be able to mark:

- Correct flag.
- Incorrect flag.
- Correct route.
- Incorrect route.
- Needs follow-up.
- No follow-up needed.
- Insufficient context.
- Escalated.
- Closed.

## Security controls

Minimum controls for production:

- Role-based access to Snowflake views.
- Separate redacted and unredacted output paths.
- Audit logging for runs and exports.
- Restricted file storage for unredacted packets.
- No raw text in standard logs.
- No raw text in GitHub issues, PR descriptions, or commit messages.
- Method versioning for every taxonomy change.
- Pull request review for SQL, taxonomy, and prompt changes.

## AI governance controls

Before enabling generative or agentic outputs:

- Define prompt version and model version.
- Use approved retrieval sources only.
- Require citations or source references for policy/playbook claims.
- Block legal conclusions and substantiation language.
- Log prompt, model, run id, input references, output, and reviewer disposition.
- Monitor hallucination, drift, prompt regressions, and routing degradation.
- Keep reviewer override available at all times.

## Retention

Recommended retention model:

- Aggregate run summaries: retain for trend history.
- Redacted output: retain according to analytics/reporting retention policy.
- Unredacted candidate packets: retain only in approved HR/Legal storage according to records policy.
- Gold standard labels: retain as governed evaluation data with access restrictions.

## Review and approval gates

Changes requiring approval:

- New review domain.
- Regex expansion that materially increases review scope.
- Priority rule changes.
- New output destination.
- New AI-generated field.
- New source system.
- New user group with raw data access.

Approval partners:

- HR Compliance
- Employee Relations
- Labor Relations
- Legal
- Data Governance
- Security
- Product owner
