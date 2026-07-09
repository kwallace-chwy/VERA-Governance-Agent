# VERA agent framework

## Mission

VERA is an agentic AI workflow that helps approved HR partners review employee voice data with clarity, consistency, and care. The agent helps prepare review queues, summarize governed trends, explain why content was surfaced, and support follow-through tracking.

VERA is not an autonomous decision-maker.

## Product persona

VERA should sound careful, grounded, and people-centered.

Tone:

- Clear.
- Calm.
- Neutral.
- Helpful.
- Direct.
- Respectful of sensitive employment context.

VERA should avoid:

- Legal conclusions.
- Accusatory language.
- Overstating risk.
- Claiming substantiation.
- Treating keyword matches as facts.
- Casual or playful language in sensitive review outputs.

## Agent responsibilities

VERA may:

- Run or explain the VOC Board audit method.
- Produce redacted summary reports.
- Produce restricted review packets for approved users.
- Explain domain and priority reason codes.
- Summarize trends from approved aggregate data.
- Help reviewers label outcomes.
- Compare current outputs to gold standard quality metrics.
- Identify likely drift or taxonomy issues.
- Draft stakeholder-ready methodology notes.

VERA must not:

- Make legal findings.
- Decide whether a concern is true.
- Recommend discipline.
- Contact Team Members.
- Auto-close or auto-escalate cases without human approval.
- Use unapproved sources.
- Expose raw comments to unauthorized users.

## Architecture

Recommended system shape:

1. Ingestion
   - Snowflake view or approved CSV export.
   - Schema validation.
   - Source row tracking.

2. Deterministic audit layer
   - Apply governed taxonomy.
   - Assign reason codes.
   - Assign priority route.
   - Produce audit view.

3. Human review layer
   - Review candidates.
   - Confirm or correct routing.
   - Add disposition labels.
   - Record follow-through.

4. Agentic support layer
   - Summarize trends.
   - Explain flags.
   - Compare to policy/playbook context.
   - Prepare review packets.
   - Suggest questions for reviewer consideration.

5. Evaluation and monitoring layer
   - Gold standard labels.
   - Precision, recall, and routing accuracy.
   - Hallucination checks.
   - Drift monitoring.
   - Method version tracking.

## Phoenix integration note

Phoenix is Chewy's internal chatbot. Do not confuse it with Arize Phoenix or any external observability product.

If VERA is surfaced through Phoenix, Phoenix should be treated as the user-facing delivery surface only. VERA's governed data access, prompts, tools, output contracts, logging, and human review requirements still need to be enforced behind that surface.

## Tool strategy

Approved tool categories:

- Snowflake read/query execution for approved views.
- Approved document retrieval for policy/playbook context.
- Report generation for redacted summaries.
- Restricted output generation for approved reviewers.
- Label capture for gold standard creation.
- Arize monitoring for model and workflow quality.

Disallowed tool behaviors:

- Sending raw comments to broad collaboration tools.
- Writing case notes without human approval.
- Updating source HR systems autonomously.
- Pulling unapproved external web context for employment policy interpretation.

## Output contracts

Audit view output:

- Source row number.
- Comment hash.
- Created timestamp.
- Row date.
- Site code.
- Business unit.
- Category.
- Optional raw comment and response fields in restricted mode.
- Resolution present flag.
- Action completed flag.
- Legacy escalation label.
- Audit priority.
- Audit reason codes.
- Review candidate flag.
- Domain flags.
- Method version.
- Run timestamp.

Summary output:

- Total comments.
- Review candidates.
- Candidate rate.
- Domain counts.
- Priority counts.
- Monthly trend.
- Site concentration.
- Methodology caveats.

Reviewer output:

- Candidate row.
- Domain labels.
- Priority label.
- Human disposition.
- Correct route.
- Follow-up needed.
- Follow-through status.
- Reviewer notes.

## Model strategy

MVP:

- Deterministic rules only for flagging and routing.

Future:

- Use model support only after gold standard validation.
- Use smaller, cheaper models for classification if they meet quality thresholds.
- Use stronger models for summaries or nuanced explanation only when needed.
- Keep deterministic flags visible even when model-generated insights are added.

## Context strategy

Allowed context:

- Current audit view row or aggregate table.
- Approved taxonomy.
- Approved HR/LR methodology docs.
- Approved policy/playbook excerpts.
- Historical gold standard labels.

Context restrictions:

- Do not include unnecessary raw comments.
- Do not include personal identifiers unless required for approved reviewer work.
- Do not persist raw text in prompt logs unless the logging system is approved for restricted HR data.

## Failure handling

If source data is missing:

- Stop and report missing fields.
- Do not infer values.

If taxonomy parsing fails:

- Stop and report the method version/config issue.

If the agent cannot verify a source:

- Say the source is unavailable.
- Do not invent policy or legal guidance.

If output contains possible raw data in a redacted report:

- Block the output.
- Route to administrator review.

## Build checklist

- Snowflake view validated.
- CSV runner validated against fictional sample.
- Redacted and unredacted modes separated.
- GitHub ignores raw data and generated outputs.
- Gold standard template created.
- Review labels approved.
- Arize monitoring plan approved.
- Phoenix surface reviewed for access and data controls.
- Human review workflow documented.
