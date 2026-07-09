# Arize monitoring plan

## Scope

Use Arize to monitor VERA when AI-generated classification, summarization, explanation, or routing support is added.

Phoenix is Chewy's internal chatbot. Do not refer to Arize Phoenix when describing the Chewy Phoenix user experience.

## Trace fields

Capture:

- `run_id`
- `source_window_start`
- `source_window_end`
- `method_version`
- `taxonomy_version`
- `prompt_version`
- `model_name`
- `model_version`
- `input_schema_version`
- `source_row_number`
- `comment_hash`
- `vera_domains`
- `vera_priority`
- `model_domains`
- `model_priority`
- `model_explanation`
- `retrieved_sources`
- `latency_ms`
- `cost`
- `error_state`
- `reviewer_disposition`
- `reviewer_route`
- `reviewer_follow_up_needed`

## Monitors

Quality:

- Precision by domain.
- Routing accuracy by owner.
- Reviewer override rate.
- False-positive rate.
- False-negative rate from sampled non-candidates.

Safety:

- Legal conclusion language.
- Unsupported factual claims.
- Missing caveat.
- Raw text sent to unauthorized output channel.

Drift:

- Candidate rate by month/site.
- Domain mix by month/site.
- Increase in ambiguous reviewer labels.
- Input schema changes.
- Model output distribution changes.

Operations:

- Run failures.
- Latency.
- Cost.
- Missing outputs.
- Missing method version.

## Alert thresholds

Initial pilot thresholds should be conservative:

- Any legal conclusion language: alert.
- Any raw-data routing exception: alert.
- Precision drop of 10 percentage points from baseline: alert.
- Candidate rate shift above agreed control limit: review.
- Schema change: block run until validated.

## Review cadence

- Weekly during pilot.
- Monthly after stable launch.
- Immediate review for safety alerts.

## Required dashboard views

- Overall quality trend.
- Domain-level quality trend.
- Route-level quality trend.
- Drift by site and month.
- Reviewer override trend.
- Safety alert log.
