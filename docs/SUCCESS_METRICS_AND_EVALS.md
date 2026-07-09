# Success metrics and evaluation framework

## North star

VERA helps leaders support positive employee relations by making sensitive employee voice review faster, more consistent, and easier to follow through on.

## Business success measures

| Measure | Why it matters | Suggested target |
| --- | --- | --- |
| Time to initial review queue | Shows whether teams see potential concerns faster. | Same day as data availability for scheduled runs. |
| Priority 1 review SLA | Ensures high-priority items receive timely human review. | 95% reviewed within approved SLA. |
| Routing accuracy | Confirms surfaced items reach the right functional owner. | 90%+ after gold standard tuning. |
| Follow-through documentation rate | Measures whether surfaced items are tracked through action or closure. | 95%+ of validated items. |
| Manual review time saved | Captures operational value for Compliance/ER/LR. | Baseline during pilot, then reduce cycle time. |
| Trend escalation quality | Measures whether site or topic trends are identified early enough to support action. | Qualitative review in pilot, then define threshold. |

## System quality measures

| Measure | Definition |
| --- | --- |
| Precision | Share of VERA candidates reviewers confirm as relevant to the surfaced domain or route. |
| Recall proxy | Share of sampled non-candidates that reviewers determine should have been surfaced. |
| False-positive rate | Share of candidates reviewers mark as not requiring review. |
| False-negative rate | Share of sampled non-candidates that should have been flagged. |
| Reviewer agreement | Agreement between reviewers on domain, priority, and routing labels. |
| Reason-code coverage | Share of surfaced candidates with at least one reason code. |
| Method repeatability | Same input plus same method version produces same output. |

## Governance and trust measures

| Measure | Definition |
| --- | --- |
| Raw data handling exceptions | Number of raw comment handling incidents or exceptions. |
| Approved-access compliance | Percent of unredacted outputs stored only in approved locations. |
| Version coverage | Percent of outputs with method version and run timestamp. |
| Override rate | Percent of VERA route/priority labels changed by human reviewers. |
| Drift alerts | Number of threshold breaches in data, taxonomy, or model behavior. |

## Gold standard strategy

The gold standard is the controlled reviewer-labeled dataset used to measure VERA quality.

Recommended labels:

- `human_relevant`: yes/no/unclear
- `human_domain`: one or more approved domains
- `human_priority`: approved priority label
- `correct_route`: HR Compliance, ER, LR, Safety/EHS, Legal, site HR, no route, unclear
- `follow_up_needed`: yes/no/unclear
- `flag_quality`: true positive, false positive, false negative, ambiguous
- `reviewer_notes`: concise reviewer rationale
- `reviewer_id`: approved reviewer identifier
- `reviewed_at`: timestamp

Sampling plan:

- Include all Priority 1 rows for the first several runs.
- Stratify Priority 2 and Priority 3 rows by domain and site.
- Include a statistically useful sample of non-candidates.
- Oversample comments with multiple domain flags.
- Oversample short or ambiguous comments.

## Arize monitoring

Use Arize for observability when AI-generated classification, summarization, or explanation is added.

Do not confuse Arize monitoring with Phoenix, which is Chewy's internal chatbot.

Recommended traces:

- Run id.
- Method version.
- Prompt version.
- Model name/version.
- Source field references.
- Output domain.
- Output priority.
- Explanation.
- Confidence, if used.
- Reviewer disposition.
- Latency.
- Cost.
- Error state.

Recommended monitors:

- Classification precision by domain.
- Routing accuracy by owner.
- Hallucination rate in explanations.
- Unsupported legal conclusion attempts.
- Drift in candidate rate by source month/site.
- Increase in "unclear" reviewer labels.
- Prompt or model version regression.
- Input schema changes.

## Hallucination checks

For generated summaries or explanations, reviewers should verify:

- The output only uses source fields provided.
- The output does not invent facts.
- The output does not quote policy unless retrieved from approved sources.
- The output does not label a concern as substantiated.
- The output does not state legal conclusions.
- The output identifies uncertainty where context is limited.

## Launch gate

Before production use of AI-generated outputs:

- Gold standard sample approved.
- Baseline precision/recall measured.
- Reviewer workflow approved.
- Monitoring dashboards configured.
- Raw data handling reviewed.
- Failure and rollback process documented.
- Stakeholder sign-off captured.
