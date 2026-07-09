# Operating model

## Review cadence

Recommended cadence:

- Scheduled VOC Board review after each feedback pull.
- Weekly review of new Priority 1 and Priority 2 candidates during pilot.
- Monthly trend review by site, domain, and business unit.
- Quarterly governance review of taxonomy, labels, and quality metrics.

## RACI

| Activity | HR Compliance | ER | LR | Legal | Safety/EHS | HREPA | ORBIT/Product | Data Governance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Define HR compliance domains | A/R | C | C | C | I | C | I | C |
| Define labor relations domains | C | C | A/R | C | I | C | I | C |
| Define safety route | I | C | I | C | A/R | C | I | C |
| Maintain Snowflake source | I | I | I | I | I | A/R | C | C |
| Maintain VERA taxonomy | A/R | R | R | C | C | R | R | C |
| Run audit | C | C | C | I | I | A/R | R | I |
| Review Priority 1 candidates | A/R | R | R | C | C | I | I | I |
| Review trends | A/R | A/R | A/R | C | C | R | C | I |
| Approve raw data access | C | C | C | C | I | I | I | A/R |
| Monitor AI quality | C | C | C | C | I | R | A/R | C |

A = accountable, R = responsible, C = consulted, I = informed.

## Human review workflow

1. Generate VERA audit output.
2. Review Priority 1 candidates first.
3. Assign functional route.
4. Reviewer confirms or corrects domain and priority.
5. Reviewer records whether follow-up is needed.
6. Validated items move to the appropriate follow-through process.
7. Closed items retain disposition labels for evaluation.
8. Non-candidate sample is reviewed for false negatives.

## Priority handling

Priority 1:

- Immediate human review lane.
- Includes HR Compliance, Labor Relations, or urgent safety/sexual/violence/self-harm indicators depending on reason code.
- Requires reviewer disposition.

Priority 2:

- Functional routing review.
- Includes Legal/executive and Safety/EHS lanes.
- Reviewed for routing and trend implications.

Priority 3:

- ER trend lane.
- Useful for site support, leadership coaching, and broader employee experience trend review.

## Follow-through statuses

Suggested statuses:

- New.
- In review.
- Routed.
- Follow-up needed.
- Follow-up complete.
- Monitoring only.
- No action needed.
- Insufficient context.
- Closed.

## Reviewer disposition labels

Minimum labels:

- Correct flag.
- Incorrect flag.
- Correct route.
- Incorrect route.
- Correct priority.
- Incorrect priority.
- Needs follow-up.
- No follow-up needed.
- Ambiguous.

## Governance forum

Recommended recurring governance attendees:

- HR Compliance owner.
- ER director or delegate.
- Labor Relations owner.
- HREPA data owner.
- ORBIT product owner.
- Legal partner.
- Data Governance partner.
- Security partner as needed.

Agenda:

- Review quality metrics.
- Review false positives and false negatives.
- Approve taxonomy updates.
- Review access and retention.
- Review AI monitoring alerts.
- Approve next rollout phase.
