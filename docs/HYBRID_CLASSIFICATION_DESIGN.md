# Hybrid classification design

## Recommendation

Use deterministic rules first, then use AI only for edge-case adjudication and explanation.

This gives VERA the best balance:

- Deterministic rules provide recall, repeatability, and auditability.
- AI reduces false positives where broad keywords lack context.
- Human reviewers remain the final decision point for sensitive employment content.

## Why this design

The current daily ER escalation email is an incumbent keyword process. It is useful because it catches a broad set of potential concerns, but it also creates noise from broad terms such as `safe`, `touch`, `bathroom`, or `$`.

The actual daily export should be treated as the baseline for measurement when available. The provided regex is useful design context, but the export can include additional risky words beyond that SQL snippet.

VERA should not discard that baseline. Instead, VERA should use it as one input to a governed comparison:

- What did the current process catch?
- What did VERA catch?
- What did both catch?
- What did only the current process catch?
- What did only VERA catch?
- Which current-only records look like false positives?
- Which current-only records show VERA recall gaps?
- Which VERA-only records show meaningful net-new signal?

## Workflow

### Stage 1: Deterministic candidate generation

Create a broad but explainable candidate pool using:

- VERA governed review domains.
- Current ER escalation risky-word matches.
- Contextual safety phrases.
- Labor relations/protected activity phrases.
- Protected-class plus workplace-conduct combinations.
- Known immediate-review phrases.

The output of this stage should include:

- Matched keyword or regex.
- Domain flag.
- Priority route.
- Whether the match came from VERA, current email, or both.
- Method version.

### Stage 2: Deterministic suppression for obvious benign phrases

Suppress or downgrade only high-confidence benign phrases. Examples:

- `safe travels`
- `touch screen`
- `high five`

Do not suppress sensitive terms if the surrounding text suggests workplace safety, conduct, discrimination, harassment, retaliation, labor relations, or violence.

### Stage 3: AI edge-case adjudication

Send only edge cases to AI:

- Current-process flagged but VERA did not flag.
- VERA flagged but current process did not flag, when confidence is low or domain is ambiguous.
- Broad keyword matches with weak context.
- Multi-domain conflicts.
- Rows where routing depends on context, not just a word.

The AI classifier should return structured JSON, not prose.

Required AI output:

- `classification`: `relevant`, `not_relevant`, or `unclear`
- `recommended_route`
- `recommended_priority`
- `false_positive_likelihood`
- `reason`
- `evidence_terms`
- `needs_human_review`

### Stage 4: Human review

Humans review:

- All Priority 1 items.
- All AI `relevant` items.
- All AI `unclear` items.
- Samples of AI `not_relevant` items for quality monitoring.

Human labels become the gold standard.

## Comparison outcomes

Use this vocabulary when comparing current process and VERA:

| Outcome | Meaning | Business interpretation |
| --- | --- | --- |
| Both caught | Current process and VERA both flagged. | Preserve signal; verify route and priority. |
| Current-only, likely false positive | Current email flagged, VERA and/or AI says not relevant. | Noise reduction opportunity. |
| Current-only, likely recall gap | Current email flagged and AI/human says relevant. | Tune VERA deterministic rules. |
| VERA-only, relevant | VERA flagged and human/AI confirms relevance. | Net-new signal. |
| VERA-only, not relevant | VERA flagged and human/AI rejects. | Tune VERA precision. |
| Neither caught, human-relevant | Found through negative sampling. | Highest-priority recall gap. |

## Safety example

Do not use broad `safe\w*` alone.

Use contextual phrases:

- `not safe`
- `unsafe`
- `hazard`
- `get hurt`
- `hurt badly`
- `safety has been compromised`
- `jeopardize safety`
- `safety concern`
- `safety issue`

This catches comments such as:

- "The new spring tables are not safe."
- "The bots are a serious hazard."
- "Safety has been compromised."

It avoids comments such as:

- "Safe travels."

## Success measures

Hybrid VERA should be measured against the incumbent email process using human labels:

- False positive reduction.
- No regression on high-value current-process true positives.
- Net-new relevant signal from VERA-only candidates.
- Routing accuracy.
- Human reviewer agreement.
- Review time saved.

## Launch rule

Do not claim VERA has fewer false positives or higher recall until human labels validate the comparison. Before labels exist, use phrasing such as:

"VERA reduced likely keyword noise and identified candidate recall gaps for reviewer validation."
