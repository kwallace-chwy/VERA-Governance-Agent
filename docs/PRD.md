# Product requirements document: VERA

## Title

VERA: A governed agentic AI workflow for employee voice review

## Product statement

VERA helps HR Compliance, Employee Relations, and Labor Relations understand what Team Members are raising through VOC Board feedback and where sites may need additional support. By organizing open-ended comments into governed review categories and surfacing emerging themes for human review, VERA helps teams route the right partners, monitor follow-through, and distinguish isolated concerns from broader trends.

## Problem

HR Compliance currently reviews employee voice channels for content that may need follow-up, including harassment, discrimination, retaliation, protected activity, safety, and other sensitive employee relations themes. The VOC Board creates a different review challenge than structured surveys:

- Inputs are open-ended and not prompted around specific compliance topics.
- Anonymity is stronger, though users can still include identifying information.
- The product encourages Team Members to voice what they want known, not necessarily what they expect to remain confidential.
- Review criteria exist, but the current process is still largely keyword-driven and manual.

If nothing changes, teams may continue to spend significant time reviewing large comment populations while having limited ability to measure coverage, explain routing, compare trends across sites, or demonstrate that the review method is consistent.

## Users

Primary users:

- HR Compliance
- Employee Relations
- Labor Relations

Secondary users:

- Site HR leaders
- Operations HR leadership
- Legal
- Safety/EHS
- People Analytics / HREPA
- ORBIT product and engineering partners
- Data Governance and Security

Workflow context:

- A VOC Board data pull is created for a review window.
- Sensitive or actionable themes need to be surfaced for human review.
- Reviewers need to understand why an item was flagged.
- Stakeholders need a repeatable way to measure issue mix, site concentration, routing volume, and follow-through.

## Proposed solution

VERA creates a governed review layer over VOC Board comments.

The first version uses deterministic review domains and routing logic:

- Explicit HR compliance language
- Protected-class references
- Workplace conduct or treatment
- Sexual misconduct or touching
- Violence, threat, or self-harm
- Labor relations or protected activity
- Safety or EHS
- Legal or regulatory references
- Executive escalation references
- General employee relations

The system produces:

- A Snowflake audit view.
- A candidate review queue.
- Redacted summary outputs for broad stakeholder review.
- Restricted unredacted exports for approved reviewers.
- Gold standard labeling templates.
- Monitoring and evaluation plans for future agentic review.

## Why AI

The initial implementation intentionally uses deterministic logic because routing and governance need to be explainable before automation expands. AI becomes valuable in later phases for:

- Summarizing clusters of related comments without replacing reviewer judgment.
- Explaining why a comment may need review in plain language.
- Comparing new comments to labeled gold standard examples.
- Helping reviewers identify emerging themes and follow-up patterns.
- Drafting review packets with citations to approved source fields.

AI should not replace deterministic audit flags where exact matching is sufficient. The product direction is governed agentic support, not unsupervised decision-making.

## Use cases

Primary use case:

- HR Compliance, ER, and Labor Relations run VERA on a VOC Board feedback window and receive a routed review queue plus summary readout.

High-value supporting use cases:

- Site trend review by domain, site, business unit, month, and priority.
- Labor Relations review of protected activity signals separated from general HR Compliance topics.
- Human reviewer labeling for precision, recall, and routing quality.
- Follow-through monitoring for surfaced items and recurring themes.
- Executive-ready readout that excludes raw comments.

Explicit non-goals:

- VERA does not make legal conclusions.
- VERA does not determine substantiation.
- VERA does not create disciplinary recommendations.
- VERA does not automatically contact Team Members or leaders.
- VERA does not expose raw comments outside approved reviewer access.

## Functional requirements

1. Ingest VOC Board data from Snowflake or a CSV export with equivalent fields.
2. Normalize source columns into a stable audit schema.
3. Apply governed review-domain flags.
4. Assign one routing priority per row.
5. Preserve reason codes for explainability.
6. Produce a full audit view for all rows.
7. Produce a candidate-only review queue.
8. Support redacted outputs for broader review.
9. Support restricted unredacted outputs for approved reviewers.
10. Produce domain, priority, site, and monthly rollups.
11. Track method version and run timestamp.
12. Provide templates for human reviewer labels and gold standard creation.

## Non-functional requirements

- Explainable: every surfaced item must show reason codes.
- Repeatable: the same input and taxonomy version should produce the same flags.
- Auditable: method version, run timestamp, source row, and comment hash should be preserved.
- Governed: raw comments must be restricted to approved users and approved storage.
- Measurable: precision, recall, false negatives, routing accuracy, and reviewer agreement must be tracked.
- Extensible: future AI summarization/classification must sit behind evaluation and monitoring gates.

## Safety and compliance requirements

- Human review is mandatory for all surfaced sensitive content.
- VERA outputs must state that priority labels are routing aids, not legal findings.
- Raw comment text and identifiable details must not be committed to GitHub by default.
- Access to unredacted outputs must be limited to approved HR/Legal users.
- Any agentic workflow must log inputs, outputs, tool calls, prompt version, model version, and reviewer disposition.
- Labor relations/protected activity references must be routed to the right partners and not mixed into discrimination/harassment prevalence claims.

## Success metrics

Business outcome metrics:

- Time from data availability to initial review queue.
- Share of Priority 1 candidates reviewed within SLA.
- Share of surfaced items routed to the correct functional owner.
- Follow-through completion rate for validated items.
- Reduction in manual review time for Compliance/ER/LR.
- Increase in consistent documentation of review rationale.

Quality metrics:

- Precision by priority and domain.
- False-negative rate from sampled regex-negative comments.
- Reviewer agreement on domain and priority labels.
- Routing accuracy by owner.
- Trend stability by site/month after volume normalization.

Trust and governance metrics:

- Percentage of outputs with reason codes.
- Percentage of runs with method version and run timestamp.
- Number of raw-data handling exceptions.
- Number of model or prompt drift alerts.

## MVP scope

MVP includes:

- Snowflake audit view.
- Local CSV runner.
- Redacted and restricted output modes.
- Governed taxonomy file.
- PRD, methodology, governance, runbook, and operating model.
- Gold standard labeling template.
- Arize monitoring plan.

MVP excludes:

- Autonomous decisions.
- Automated case creation.
- Direct Slack/email notification.
- Team Member outreach.
- Model-generated legal analysis.

## Phased roadmap

Phase 1: Deterministic audit foundation

- Build Snowflake view and local runner.
- Validate counts and routing with HR Compliance, ER, and LR.
- Create gold standard labels.

Phase 2: Reviewer workflow

- Add reviewer disposition capture.
- Track owner, status, action taken, and follow-through date.
- Add recurring trend readouts.

Phase 3: Agentic support

- Add governed summarization and explanation for candidates.
- Add retrieval from approved policy/playbook sources.
- Add Phoenix delivery path if approved.

Phase 4: Monitoring and scale

- Monitor with Arize for hallucination, drift, routing degradation, and schema changes.
- Expand to other employee voice channels only after validation.

## Open questions

- What is the approved storage location for unredacted reviewer packets?
- What teams are allowed to view raw VOC comments and employee identifiers?
- What SLA should apply to each priority lane?
- What reviewer disposition labels should be mandatory?
- Should validated items flow into an existing ER case system or remain in a review tracker?
- What threshold should trigger site-level support or leadership review?
