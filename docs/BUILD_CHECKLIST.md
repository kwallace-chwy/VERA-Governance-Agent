# VERA build checklist

## 1. Foundation

- [x] Name and positioning approved: VERA.
- [x] Product tagline drafted.
- [x] Initial business problem documented.
- [x] Current keyword process translated into governed domains.
- [x] Snowflake view drafted.
- [x] Local CSV runner drafted.
- [x] Redacted and restricted output modes separated.
- [x] Repository guardrails added to prevent raw data commits.

## 2. Data and SQL

- [ ] Confirm source-of-truth VOC Board table and owner.
- [ ] Confirm included/excluded locations.
- [ ] Confirm date-window policy.
- [ ] Validate Snowflake view syntax in production worksheet.
- [ ] Validate row counts against source query.
- [ ] Validate domain and priority counts against local run.
- [ ] Create approved production schema/view naming.
- [ ] Decide whether unredacted candidate export is a view, query, or controlled file export.

## 3. Reviewer workflow

- [ ] Confirm Priority 1 SLA.
- [ ] Confirm Priority 2 and Priority 3 review cadence.
- [ ] Confirm reviewer disposition labels.
- [ ] Confirm correct routing owner list.
- [ ] Define follow-through statuses.
- [ ] Define where dispositions are stored.
- [ ] Define escalation path for urgent content.
- [ ] Define process for comments with insufficient context.

## 4. Governance

- [ ] Confirm raw data access list.
- [ ] Confirm approved storage for unredacted outputs.
- [ ] Confirm retention policy.
- [ ] Confirm data classification.
- [ ] Confirm GitHub repo access.
- [ ] Confirm PR approval requirements for taxonomy, SQL, and prompt changes.
- [ ] Confirm method versioning standard.
- [ ] Confirm release note process.

## 5. Gold standard

- [ ] Build initial labeled sample.
- [ ] Include all Priority 1 rows during pilot.
- [ ] Sample Priority 2 and Priority 3 rows by domain and site.
- [ ] Sample non-candidates to estimate false negatives.
- [ ] Measure reviewer agreement.
- [ ] Adjudicate disagreements.
- [ ] Establish baseline precision and recall proxy.

## 6. Agentic layer

- [ ] Approve VERA system prompt.
- [ ] Define approved tools.
- [ ] Define approved retrieval sources.
- [ ] Define output contracts.
- [ ] Define blocked language and safety checks.
- [ ] Define Phoenix delivery surface requirements.
- [ ] Confirm Phoenix access and raw data controls.
- [ ] Confirm no autonomous employment actions.

## 7. Monitoring

- [ ] Configure Arize traces.
- [ ] Configure hallucination checks.
- [ ] Configure routing accuracy monitoring.
- [ ] Configure domain drift monitoring.
- [ ] Configure candidate-rate drift monitoring.
- [ ] Configure schema-change alert.
- [ ] Define alert owners.
- [ ] Define rollback path for prompt/model/taxonomy changes.

## 8. Launch

- [ ] Run pilot with HR Compliance, ER, and LR.
- [ ] Review pilot false positives and false negatives.
- [ ] Tune taxonomy through governance.
- [ ] Confirm stakeholder readout format.
- [ ] Confirm operating cadence.
- [ ] Approve MVP launch.
- [ ] Document lessons learned.
- [ ] Decide next channel or workflow expansion.
