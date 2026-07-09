# Reviewer labeling guide

## Purpose

Reviewer labels create the gold standard used to evaluate VERA quality over time.

Labels should capture what a trained reviewer determines after reading the source comment and response. Labels are not legal conclusions.

## Required fields

`human_relevant`

- `yes`: the row is relevant to a governed review domain.
- `no`: the row does not require review for the surfaced domain.
- `unclear`: there is not enough context.

`human_domains`

- One or more VERA domains that apply.
- Use `none` if no domain applies.

`human_priority`

- Reviewer-confirmed priority.
- Use VERA priority labels where possible.

`correct_route`

- HR Compliance
- Employee Relations
- Labor Relations
- Safety/EHS
- Legal
- Site HR
- No route
- Unclear

`follow_up_needed`

- `yes`
- `no`
- `unclear`

`flag_quality`

- `true_positive`
- `false_positive`
- `false_negative`
- `ambiguous`

## Reviewer principles

- Label the row based on the text and approved context.
- Do not infer facts that are not present.
- Do not make legal conclusions.
- Keep notes concise and professional.
- If a row includes multiple themes, preserve all relevant domains.
- If the route is sensitive, use the more protective review path.

## Adjudication

When reviewers disagree:

1. Compare domain label.
2. Compare priority label.
3. Compare route.
4. Decide whether the disagreement reflects taxonomy ambiguity, reviewer interpretation, or insufficient context.
5. Update taxonomy or guidance only after governance review.
