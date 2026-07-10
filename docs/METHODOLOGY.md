# VERA methodology

## Purpose

VERA evaluates VOC Board comments for the presence or absence of themes that may warrant human review by HR Compliance, Employee Relations, Labor Relations, Safety/EHS, Legal, or site HR partners.

The method is designed to support consistent review and trend measurement. It does not decide whether a report is actionable, substantiated, legally valid, or policy-valid.

## Source data

Primary source:

`EDLDB.PEOPLE_ANALYTICS_SANDBOX.VOC_BOARD`

Current default filter:

- `DATE_POSTED >= '2026-01-01'`
- `DATE_POSTED <= CURRENT_DATE()`
- `LOCATION NOT IN ('BOS4', 'SDF1')`
- nonblank `FEEDBACK`

Expected fields:

- `LOCATION`
- `DATE_POSTED`
- `FEEDBACK`
- `RESOLUTION`
- `CATEGORY`
- `OWNER`
- `OWNER_ASSIGNED`
- `EMPLOYEE_NAME`
- `CREATED_BY`
- `DATE_RESOLVED`
- `ADDITIONAL_COMMENTS`
- `CREATED_DATE`

## Review domains

VERA separates the current escalation keyword approach into review domains so the routing basis is visible.

| Domain | What it captures | Primary owner |
| --- | --- | --- |
| Explicit HR compliance language | Direct references to harassment, discrimination, retaliation, hostile treatment, wrongful termination, or EEOC. | HR Compliance |
| Protected-class reference | References to race, religion, gender, disability, ADA, age, pregnancy, national origin, and related terms. | HR Compliance |
| Workplace conduct or treatment | Unfairness, favoritism, bullying, abusive conduct, intimidation, toxic behavior, and similar treatment terms. | ER / HR Compliance depending on context |
| Sexual misconduct or touching | Sexual language, sexual harassment phrasing, touching, assault, or inappropriate conduct references. | HR Compliance / ER |
| Violence, threat, or self-harm | Threats, violence, suicide, self-harm, or harm to others. | Immediate human review |
| Labor relations or protected activity | Union, organizing, strike, protest, picketing, NLRB, protected/concerted activity terms. | Labor Relations |
| Safety or EHS | OSHA, unsafe, danger, injury, temperature, heat, substances, and related safety terms. | Safety/EHS |
| Legal or regulatory reference | Attorney, lawsuit, legal, illegal, DOL, FLSA, FMLA, and related terms. | Legal / HR Compliance |
| Executive escalation reference | CEO, CTO, CHRO, CMO, Sumit, and similar executive references. | Executive / HR routing |
| General employee relations | Conflict, disrespect, demean, hate, theft, toxic, unresponsive, and related ER trend terms. | ER / Site HR |

## Priority routing

Priority is assigned in a deterministic order.

1. Priority 1 - Immediate human review
   - Violence/threat/self-harm or sexual misconduct/touching.
2. Priority 1 - HR Compliance review
   - Explicit HR compliance language, or protected-class reference plus workplace conduct.
3. Priority 1 - Labor Relations review
   - Labor relations or protected activity language.
4. Priority 2 - Legal / executive routing review
   - Legal/regulatory or executive escalation language.
5. Priority 2 - Safety / EHS routing review
   - Safety/EHS terms.
6. Priority 3 - Employee Relations trend review
   - General ER or workplace conduct language.

## Why this split matters

The current keyword search is useful as a broad first screen, but it mixes several review purposes:

- HR Compliance
- Labor Relations
- Safety/EHS
- Legal/regulatory
- Executive escalation
- General ER

VERA preserves the recall value of keyword review while making the domain and routing rationale easier to inspect.

## Hybrid classification workflow

VERA uses deterministic logic before AI.

1. Deterministic keyword and regex rules create an explainable candidate pool.
2. Deterministic benign-context checks identify high-confidence false-positive patterns such as `safe travels`.
3. Rows where VERA and the current process disagree are placed into an AI edge-case review queue.
4. AI classification, when enabled, returns structured labels only. It does not make legal conclusions or final employment determinations.
5. Human reviewers validate relevant, unclear, and sampled not-relevant rows. Those labels become the gold standard.

There are two comparison baselines:

- Provided current-process regex: the SQL CASE expression provided during design.
- Actual ER escalation export: the daily email output file. This should be treated as the measurement baseline because it may include additional risky words beyond the provided regex.
- VOC Escalation Email attachments: daily CSV/XLSX attachments should be reconciled before calling any VERA candidate net-new to the current process.

Safety/EHS matching is intentionally contextual. Broad terms such as `hot`, `heat`, `freezer`, `alcohol`, or `drunk` should not create a Safety/EHS candidate by themselves. Examples such as hot dogs, hot chocolate, coffee machines, breakroom freezers, freezer dethawing, or someone "drunk" a beverage should be treated as amenity or keyword-noise contexts unless the comment also describes a workplace safety, health, exposure, OSHA, injury, hazard, or similar concern.

## Measurement approach

Core measures:

- Total VOC Board comments.
- Count and rate of review candidates.
- Count and rate by review domain.
- Count and rate by priority.
- Site concentration by candidate volume and candidate rate.
- Monthly trend by domain and priority.
- Legacy regex comparison.
- Current ER escalation export comparison.

Quality measures:

- Precision by domain and priority.
- False-negative rate from sampled non-candidates.
- Reviewer agreement by domain and priority.
- Routing accuracy to functional owner.
- Repeatability across runs with the same method version.

## Gold standard creation

VERA needs human-labeled examples before AI-assisted classification can be trusted.

Recommended sample:

- 100% of Priority 1 candidates.
- Stratified sample of Priority 2 and Priority 3 candidates.
- Stratified sample of non-candidates by site, month, and category.
- Oversample short comments, ambiguous comments, and comments with multiple domains.

Reviewer labels should capture:

- Human-confirmed domain.
- Human-confirmed priority.
- Correct routing owner.
- Whether follow-up is needed.
- Whether raw text contains enough context for review.
- Notes on false positive, false negative, or ambiguous wording.

## Known limitations

- Regex can miss indirect wording and euphemisms.
- Regex can over-flag generic words such as "hot", "safe", "law", or "age" when context is benign.
- VOC Board comments may reflect site operations topics more often than confidential reporting.
- Counts do not indicate substantiation or legal actionability.
- Site comparisons should consider site size, participation rates, reporting culture, and month completeness.

## Method versioning

Current version:

`VERA_VOC_HYBRID_V0_3`

Any change to domains, patterns, priority rules, filters, or source fields should increment the method version and be documented in a release note.
