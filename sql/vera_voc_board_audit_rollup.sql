-- VERA VOC Board audit rollup
-- Run after sql/vera_voc_board_audit_view.sql.
-- Produces a single tidy output table for reporting and QA.

WITH v AS (
    SELECT *
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.VERA_VOC_BOARD_AUDIT_VW
),
denominator AS (
    SELECT COUNT(*) AS total_comments
    FROM v
),
domain_rows AS (
    SELECT 'domain' AS section, 'Explicit HR compliance language' AS metric, NULL AS dimension_1, NULL AS dimension_2, COUNT_IF(FLAG_EXPLICIT_HR_COMPLIANCE) AS comments FROM v
    UNION ALL SELECT 'domain', 'Protected-class reference', NULL, NULL, COUNT_IF(FLAG_PROTECTED_CLASS_REFERENCE) FROM v
    UNION ALL SELECT 'domain', 'Workplace conduct or treatment', NULL, NULL, COUNT_IF(FLAG_WORKPLACE_CONDUCT) FROM v
    UNION ALL SELECT 'domain', 'Sexual misconduct or touching', NULL, NULL, COUNT_IF(FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING) FROM v
    UNION ALL SELECT 'domain', 'Violence, threat, or self-harm', NULL, NULL, COUNT_IF(FLAG_VIOLENCE_OR_SELF_HARM) FROM v
    UNION ALL SELECT 'domain', 'Labor relations or protected activity', NULL, NULL, COUNT_IF(FLAG_LABOR_RELATIONS) FROM v
    UNION ALL SELECT 'domain', 'Safety or EHS', NULL, NULL, COUNT_IF(FLAG_SAFETY_EHS) FROM v
    UNION ALL SELECT 'domain', 'Legal or regulatory reference', NULL, NULL, COUNT_IF(FLAG_LEGAL_REGULATORY) FROM v
    UNION ALL SELECT 'domain', 'Executive escalation reference', NULL, NULL, COUNT_IF(FLAG_EXECUTIVE_ESCALATION) FROM v
    UNION ALL SELECT 'domain', 'General employee relations', NULL, NULL, COUNT_IF(FLAG_GENERAL_EMPLOYEE_RELATIONS) FROM v
),
priority_rows AS (
    SELECT
        'priority' AS section,
        COALESCE(AUDIT_PRIORITY, 'Not flagged') AS metric,
        NULL AS dimension_1,
        NULL AS dimension_2,
        COUNT(*) AS comments
    FROM v
    GROUP BY COALESCE(AUDIT_PRIORITY, 'Not flagged')
),
site_rows AS (
    SELECT
        'site' AS section,
        SITE_CODE AS metric,
        BUSINESS_UNIT AS dimension_1,
        'review_candidates' AS dimension_2,
        COUNT_IF(FLAG_REVIEW_CANDIDATE) AS comments
    FROM v
    GROUP BY SITE_CODE, BUSINESS_UNIT
),
month_rows AS (
    SELECT
        'month' AS section,
        TO_VARCHAR(DATE_TRUNC('month', ROW_DATE), 'YYYY-MM') AS metric,
        'review_candidates' AS dimension_1,
        NULL AS dimension_2,
        COUNT_IF(FLAG_REVIEW_CANDIDATE) AS comments
    FROM v
    GROUP BY DATE_TRUNC('month', ROW_DATE)
),
summary_rows AS (
    SELECT 'summary' AS section, 'VOC Board comments analyzed' AS metric, NULL AS dimension_1, NULL AS dimension_2, COUNT(*) AS comments FROM v
    UNION ALL
    SELECT 'summary', 'VERA review candidates', NULL, NULL, COUNT_IF(FLAG_REVIEW_CANDIDATE) FROM v
)
SELECT
    section,
    metric,
    dimension_1,
    dimension_2,
    comments,
    d.total_comments,
    ROUND(comments / NULLIF(d.total_comments, 0), 4) AS share_of_comments,
    CURRENT_TIMESTAMP() AS rollup_run_ts
FROM (
    SELECT * FROM summary_rows
    UNION ALL SELECT * FROM domain_rows
    UNION ALL SELECT * FROM priority_rows
    UNION ALL SELECT * FROM site_rows
    UNION ALL SELECT * FROM month_rows
) r
CROSS JOIN denominator d
ORDER BY
    section,
    comments DESC,
    metric;
