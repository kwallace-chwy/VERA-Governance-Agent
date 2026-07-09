-- VERA VOC Board audit view
-- Purpose: surface governed VOC Board review candidates for human review.
-- This view supports routing and prevalence measurement. It does not make legal conclusions.
-- Default scope: 2026 YTD, excluding BOS4 and SDF1 to match the current VOC Board source query.

CREATE OR REPLACE VIEW EDLDB.PEOPLE_ANALYTICS_SANDBOX.VERA_VOC_BOARD_AUDIT_VW AS
WITH base AS (
    SELECT
        CREATED_DATE AS CREATED,
        DATE_POSTED::DATE AS ROW_DATE,
        FEEDBACK AS PRIMARY_TEXT,
        RESOLUTION,
        CATEGORY,
        OWNER,
        OWNER_ASSIGNED,
        EMPLOYEE_NAME,
        CREATED_BY,
        DATE_RESOLVED,
        ADDITIONAL_COMMENTS,
        LOCATION AS SITE_CODE,
        CASE LOCATION
            WHEN 'AVP1' THEN 'FC'
            WHEN 'AVP2' THEN 'FC'
            WHEN 'BNA1' THEN 'FC'
            WHEN 'CFC1' THEN 'FC'
            WHEN 'CLT1' THEN 'FC'
            WHEN 'DAY1' THEN 'FC'
            WHEN 'HOU1' THEN 'FC'
            WHEN 'MCI1' THEN 'FC'
            WHEN 'MCO1' THEN 'FC'
            WHEN 'MDT1' THEN 'FC'
            WHEN 'PHX1' THEN 'FC'
            WHEN 'RNO1' THEN 'FC'
            WHEN 'DFW1' THEN 'FC'
            WHEN 'MCO4' THEN 'Rx'
            WHEN 'PHX2' THEN 'Rx'
            WHEN 'AVP4' THEN 'Rx'
            WHEN 'DFW8' THEN 'Rx'
            WHEN 'SDF2' THEN 'Rx'
            WHEN 'SDF4' THEN 'Rx'
            WHEN 'SDF6' THEN 'Rx'
            ELSE 'Unknown'
        END AS BUSINESS_UNIT,
        REGEXP_REPLACE(COALESCE(FEEDBACK, ''), '\\s+', ' ') AS AUDIT_TEXT
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.VOC_BOARD
    WHERE DATE_POSTED >= '2026-01-01'
      AND DATE_POSTED <= CURRENT_DATE()
      AND LOCATION NOT IN ('BOS4', 'SDF1')
      AND FEEDBACK IS NOT NULL
      AND TRIM(FEEDBACK) <> ''
),
flags AS (
    SELECT
        *,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(discriminat\\w*|harass\\w*|retaliat\\w*|hostil\\w*|wrongful\\s+term\\w*|eeoc)\\b.*', 'is') AS FLAG_EXPLICIT_HR_COMPLIANCE,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(race|racial|racis\\w*|religion|religious|gender|sexism|sexist|pregnan\\w*|maternity|disab\\w*|ada|national\\s+origin|ethnic\\w*|black|white|hispanic|latino|latina|asian|gay|lesbian|lgbtq\\w*|transgender|trans|veteran|older|age)\\b.*', 'is') AS FLAG_PROTECTED_CLASS_REFERENCE,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(unfair\\w*|favorit\\w*|unjust\\w*|bully\\w*|abus\\w*|demean\\w*|slur\\w*|inappropriate\\w*|intimidat\\w*|aggress\\w*|disrespect\\w*|conflict\\w*|berat\\w*|toxic\\w*|target\\w*|exclude\\w*|teas\\w*)\\b.*', 'is') AS FLAG_WORKPLACE_CONDUCT,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(sexual\\w*|sex\\s+harass\\w*|touch\\w*|assault\\w*|inappropriate\\s+(comment|touch|advance|behavior|conduct))\\b.*', 'is') AS FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(threat\\w*|violen\\w*|suicide\\w*|self\\s*harm|kill\\s+myself|hurt\\s+myself|hurt\\s+someone)\\b.*', 'is') AS FLAG_VIOLENCE_OR_SELF_HARM,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(union\\w*|organiz\\w*|strik\\w*|protest\\w*|picket\\w*|nlrb|concerted\\s+activit\\w*|unfair\\s+labor\\s+practice|collective\\s+bargain\\w*)\\b.*', 'is') AS FLAG_LABOR_RELATIONS,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(osha|unsaf\\w*|danger\\w*|risk\\w*|injur\\w*|hot|heat|temperature|temparature|freez\\w*|burn\\w*|drug\\w*|alcohol\\w*|drunk\\w*|marijuana\\w*|under\\s+the\\s+influence)\\b.*', 'is') AS FLAG_SAFETY_EHS,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(attorney\\w*|counsel\\w*|lawsuit\\w*|legal\\w*|illegal\\w*|law|laws|dol|flsa|fmla)\\b.*', 'is') AS FLAG_LEGAL_REGULATORY,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(ceo|cto|chro|cmo|sumit)\\b.*', 'is') AS FLAG_EXECUTIVE_ESCALATION,
        REGEXP_LIKE(AUDIT_TEXT, '.*\\b(inconsistent\\w*|unfair\\w*|favorit\\w*|unjust\\w*|bully\\w*|abus\\w*|conflict\\w*|berat\\w*|disrespect\\w*|demean\\w*|hate\\w*|violat\\w*|toxic\\w*|unrespons\\w*|steal\\w*|theft\\w*)\\b.*', 'is') AS FLAG_GENERAL_EMPLOYEE_RELATIONS
    FROM base
),
priority AS (
    SELECT
        *,
        CASE
            WHEN FLAG_VIOLENCE_OR_SELF_HARM OR FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING
                THEN 'Priority 1 - Immediate human review'
            WHEN FLAG_EXPLICIT_HR_COMPLIANCE OR (FLAG_PROTECTED_CLASS_REFERENCE AND FLAG_WORKPLACE_CONDUCT)
                THEN 'Priority 1 - HR Compliance review'
            WHEN FLAG_LABOR_RELATIONS
                THEN 'Priority 1 - Labor Relations review'
            WHEN FLAG_LEGAL_REGULATORY OR FLAG_EXECUTIVE_ESCALATION
                THEN 'Priority 2 - Legal / executive routing review'
            WHEN FLAG_SAFETY_EHS
                THEN 'Priority 2 - Safety / EHS routing review'
            WHEN FLAG_GENERAL_EMPLOYEE_RELATIONS OR FLAG_WORKPLACE_CONDUCT
                THEN 'Priority 3 - Employee Relations trend review'
            ELSE NULL
        END AS AUDIT_PRIORITY
    FROM flags
)
SELECT
    CREATED,
    ROW_DATE,
    SITE_CODE,
    BUSINESS_UNIT,
    CATEGORY,
    OWNER,
    OWNER_ASSIGNED,
    EMPLOYEE_NAME,
    CREATED_BY,
    DATE_RESOLVED,
    PRIMARY_TEXT,
    RESOLUTION,
    ADDITIONAL_COMMENTS,
    IFF(RESOLUTION IS NOT NULL AND TRIM(RESOLUTION) <> '', TRUE, FALSE) AS RESOLUTION_PRESENT,
    AUDIT_PRIORITY,
    ARRAY_TO_STRING(
        ARRAY_CONSTRUCT_COMPACT(
            IFF(FLAG_EXPLICIT_HR_COMPLIANCE, 'explicit_hr_compliance', NULL),
            IFF(FLAG_PROTECTED_CLASS_REFERENCE, 'protected_class_reference', NULL),
            IFF(FLAG_WORKPLACE_CONDUCT, 'workplace_conduct', NULL),
            IFF(FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING, 'sexual_misconduct_or_touching', NULL),
            IFF(FLAG_VIOLENCE_OR_SELF_HARM, 'violence_or_self_harm', NULL),
            IFF(FLAG_LABOR_RELATIONS, 'labor_relations', NULL),
            IFF(FLAG_SAFETY_EHS, 'safety_ehs', NULL),
            IFF(FLAG_LEGAL_REGULATORY, 'legal_regulatory', NULL),
            IFF(FLAG_EXECUTIVE_ESCALATION, 'executive_escalation', NULL),
            IFF(FLAG_GENERAL_EMPLOYEE_RELATIONS, 'general_employee_relations', NULL)
        ),
        ', '
    ) AS AUDIT_REASON_CODES,
    IFF(AUDIT_PRIORITY IS NOT NULL, TRUE, FALSE) AS FLAG_REVIEW_CANDIDATE,
    FLAG_EXPLICIT_HR_COMPLIANCE,
    FLAG_PROTECTED_CLASS_REFERENCE,
    FLAG_WORKPLACE_CONDUCT,
    FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING,
    FLAG_VIOLENCE_OR_SELF_HARM,
    FLAG_LABOR_RELATIONS,
    FLAG_SAFETY_EHS,
    FLAG_LEGAL_REGULATORY,
    FLAG_EXECUTIVE_ESCALATION,
    FLAG_GENERAL_EMPLOYEE_RELATIONS,
    CURRENT_TIMESTAMP() AS AUDIT_RUN_TS,
    'VERA_VOC_REGEX_V0_1' AS AUDIT_METHOD_VERSION
FROM priority;
