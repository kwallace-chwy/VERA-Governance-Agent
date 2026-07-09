from __future__ import annotations

import argparse
import hashlib
import html
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


warnings.filterwarnings(
    "ignore",
    message="This pattern is interpreted as a regular expression, and has match groups.*",
    category=UserWarning,
)


BUSINESS_UNIT_BY_SITE = {
    "AVP1": "FC",
    "AVP2": "FC",
    "BNA1": "FC",
    "CFC1": "FC",
    "CLT1": "FC",
    "DAY1": "FC",
    "HOU1": "FC",
    "MCI1": "FC",
    "MCO1": "FC",
    "MDT1": "FC",
    "PHX1": "FC",
    "RNO1": "FC",
    "DFW1": "FC",
    "MCO4": "Rx",
    "PHX2": "Rx",
    "AVP4": "Rx",
    "DFW8": "Rx",
    "SDF2": "Rx",
    "SDF4": "Rx",
    "SDF6": "Rx",
}


LEGACY_LEVEL_PATTERNS = [
    (
        "Level 1 Priority",
        r"\b(discriminat\w*|harass\w*|retaliat\w*|hostil\w*|threat\w*|racis\w*|sex\w*|union\w*|organiz\w*|strik\w*|protest\w*|picket\w*|violen\w*|attorney\w*|counsel\w*|illeg\w*|suicide\w*|touch\w*|eeoc|dol|osha|ada|flsa|fmla|law|ceo|sumit|cto|chro|cmo|wrongful\s+term\w*)\b",
    ),
    (
        "Level 2 Priority",
        r"\b(inconsistent\w*|unfair\w*|favorit\w*|unjust\w*|bully\w*|abus\w*|unsaf\w*|risk\w*|danger\w*|inappropriate\w*|intimidate\w*|aggress\w*|assault\w*|drunk\w*|drug\w*|alcohol\w*|marijuana\w*|pot|falsif\w*|hot|temparature|heat|freez\w*|burn\w*|wage\w*|safe\w*|under\s+the\s+influence)\b",
    ),
    (
        "Level 3 Priority",
        r"\b(dispute\w*|conflict\w*|berate\w*|disrespect\w*|demean\w*|hate\w*|violat\w*|steal\w*|theft\w*|toxic\w*|unrespons\w*|disresp\w*|teas\w*)\b",
    ),
]


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def first_present(df: pd.DataFrame, names: list[str]) -> str | None:
    for name in names:
        if name in df.columns:
            return name
    return None


def comment_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def pct(numerator: int | float, denominator: int | float) -> float:
    return 0.0 if not denominator else round(float(numerator) / float(denominator), 4)


def compute_legacy_level(text: str) -> str | None:
    for label, pattern in LEGACY_LEVEL_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            return label
    return None


def load_taxonomy(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize_input(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [column.strip().upper() for column in df.columns]

    text_col = first_present(df, ["PRIMARY_TEXT", "FEEDBACK", "VOC_COMMENT"])
    date_col = first_present(df, ["ROW_DATE", "DATE_POSTED"])
    site_col = first_present(df, ["SITE_CODE", "LOCATION"])
    created_col = first_present(df, ["CREATED", "CREATED_DATE"])
    legacy_col = first_present(df, ["LEGACY_REGEX_ESCALATION", "ESCALTION", "ESCALATION"])

    missing = [
        label
        for label, column in {
            "comment text": text_col,
            "row date": date_col,
            "site/location": site_col,
        }.items()
        if column is None
    ]
    if missing:
        raise ValueError(f"Input is missing required fields: {', '.join(missing)}")

    df["PRIMARY_TEXT"] = df[text_col]
    df["ROW_DATE"] = df[date_col]
    df["SITE_CODE"] = df[site_col].fillna("").astype(str).str.strip().str.upper()
    df["CREATED"] = df[created_col] if created_col else pd.NA
    df["VOICE_MECHANISM"] = df["VOICE_MECHANISM"] if "VOICE_MECHANISM" in df.columns else "VOC Board"
    df["BUSINESS_UNIT"] = (
        df["BUSINESS_UNIT"]
        if "BUSINESS_UNIT" in df.columns
        else df["SITE_CODE"].map(BUSINESS_UNIT_BY_SITE).fillna("Unknown")
    )
    df["CATEGORY"] = df["CATEGORY"] if "CATEGORY" in df.columns else pd.NA
    df["RESOLUTION"] = df["RESOLUTION"] if "RESOLUTION" in df.columns else pd.NA
    df["ADDITIONAL_COMMENTS"] = df["ADDITIONAL_COMMENTS"] if "ADDITIONAL_COMMENTS" in df.columns else pd.NA
    df["OWNER"] = df["OWNER"] if "OWNER" in df.columns else pd.NA
    df["OWNER_ASSIGNED"] = df["OWNER_ASSIGNED"] if "OWNER_ASSIGNED" in df.columns else pd.NA
    df["EMPLOYEE_NAME"] = df["EMPLOYEE_NAME"] if "EMPLOYEE_NAME" in df.columns else pd.NA
    df["CREATED_BY"] = df["CREATED_BY"] if "CREATED_BY" in df.columns else pd.NA
    df["DATE_RESOLVED"] = df["DATE_RESOLVED"] if "DATE_RESOLVED" in df.columns else pd.NA
    df["ACTION_COMPLETED"] = (
        df["ACTION_COMPLETED"]
        if "ACTION_COMPLETED" in df.columns
        else df["RESOLUTION"].map(lambda value: bool(clean_text(value)))
    )
    df["PRIMARY_TEXT_CLEAN"] = df["PRIMARY_TEXT"].map(clean_text)
    df["LEGACY_REGEX_ESCALATION"] = (
        df[legacy_col].astype("object").replace("", pd.NA)
        if legacy_col
        else df["PRIMARY_TEXT_CLEAN"].map(compute_legacy_level)
    )
    missing_legacy = df["LEGACY_REGEX_ESCALATION"].isna()
    if missing_legacy.any():
        df.loc[missing_legacy, "LEGACY_REGEX_ESCALATION"] = df.loc[missing_legacy, "PRIMARY_TEXT_CLEAN"].map(
            compute_legacy_level
        )
    return df


def apply_flags(df: pd.DataFrame, taxonomy: dict[str, Any]) -> pd.DataFrame:
    output = df.copy()
    for key, domain in taxonomy["domains"].items():
        output[f"FLAG_{key.upper()}"] = output["PRIMARY_TEXT_CLEAN"].str.contains(
            domain["pattern"],
            flags=re.IGNORECASE | re.DOTALL,
            regex=True,
            na=False,
        )
    return output


def reason_codes(row: pd.Series, taxonomy: dict[str, Any]) -> str:
    codes = [key for key in taxonomy["domains"] if bool(row.get(f"FLAG_{key.upper()}", False))]
    return ", ".join(codes)


def assign_priority(row: pd.Series) -> str | None:
    if row["FLAG_VIOLENCE_OR_SELF_HARM"] or row["FLAG_SEXUAL_MISCONDUCT_OR_TOUCHING"]:
        return "Priority 1 - Immediate human review"
    if row["FLAG_EXPLICIT_HR_COMPLIANCE"] or (
        row["FLAG_PROTECTED_CLASS_REFERENCE"] and row["FLAG_WORKPLACE_CONDUCT"]
    ):
        return "Priority 1 - HR Compliance review"
    if row["FLAG_LABOR_RELATIONS"]:
        return "Priority 1 - Labor Relations review"
    if row["FLAG_LEGAL_REGULATORY"] or row["FLAG_EXECUTIVE_ESCALATION"]:
        return "Priority 2 - Legal / executive routing review"
    if row["FLAG_SAFETY_EHS"]:
        return "Priority 2 - Safety / EHS routing review"
    if row["FLAG_GENERAL_EMPLOYEE_RELATIONS"] or row["FLAG_WORKPLACE_CONDUCT"]:
        return "Priority 3 - Employee Relations trend review"
    return None


def build_view(df: pd.DataFrame, taxonomy: dict[str, Any], include_raw: bool) -> pd.DataFrame:
    flagged = apply_flags(df, taxonomy)
    flagged["AUDIT_REASON_CODES"] = flagged.apply(lambda row: reason_codes(row, taxonomy), axis=1)
    flagged["AUDIT_PRIORITY"] = flagged.apply(assign_priority, axis=1)
    flagged["FLAG_REVIEW_CANDIDATE"] = flagged["AUDIT_PRIORITY"].notna()
    flagged["COMMENT_HASH"] = flagged["PRIMARY_TEXT_CLEAN"].map(comment_hash)
    flagged["SOURCE_ROW_NUMBER"] = flagged.index + 2
    flagged["AUDIT_METHOD_VERSION"] = taxonomy.get("method_version", "VERA_VOC_REGEX_V0_1")
    flagged["AUDIT_RUN_TS"] = datetime.now().isoformat(timespec="seconds")
    flagged["RESOLUTION_PRESENT"] = flagged["RESOLUTION"].map(lambda value: bool(clean_text(value)))

    base_columns = [
        "SOURCE_ROW_NUMBER",
        "COMMENT_HASH",
        "CREATED",
        "ROW_DATE",
        "SITE_CODE",
        "BUSINESS_UNIT",
        "CATEGORY",
    ]
    raw_columns = [
        "PRIMARY_TEXT",
        "RESOLUTION",
        "ADDITIONAL_COMMENTS",
        "OWNER",
        "OWNER_ASSIGNED",
        "EMPLOYEE_NAME",
        "CREATED_BY",
        "DATE_RESOLVED",
    ]
    audit_columns = [
        "RESOLUTION_PRESENT",
        "ACTION_COMPLETED",
        "LEGACY_REGEX_ESCALATION",
        "AUDIT_PRIORITY",
        "AUDIT_REASON_CODES",
        "FLAG_REVIEW_CANDIDATE",
        *[f"FLAG_{key.upper()}" for key in taxonomy["domains"]],
        "AUDIT_METHOD_VERSION",
        "AUDIT_RUN_TS",
    ]
    columns = [*base_columns, *(raw_columns if include_raw else []), *audit_columns]
    view = flagged[columns].copy()
    return view.sort_values(
        ["FLAG_REVIEW_CANDIDATE", "AUDIT_PRIORITY", "ROW_DATE", "SITE_CODE"],
        ascending=[False, True, False, True],
    )


def summarize(view: pd.DataFrame, taxonomy: dict[str, Any]) -> dict[str, Any]:
    total = len(view)
    flagged = int(view["FLAG_REVIEW_CANDIDATE"].sum())
    domain_rows = []
    for key, domain in taxonomy["domains"].items():
        count = int(view[f"FLAG_{key.upper()}"].sum())
        domain_rows.append(
            {
                "domain": domain["label"],
                "comments": count,
                "share_of_comments": pct(count, total),
            }
        )
    priority_rows = (
        view.assign(AUDIT_PRIORITY=view["AUDIT_PRIORITY"].fillna("Not flagged"))
        .groupby("AUDIT_PRIORITY")
        .size()
        .reset_index(name="comments")
        .sort_values("comments", ascending=False)
    )
    return {
        "total_comments": total,
        "review_candidates": flagged,
        "review_candidate_rate": pct(flagged, total),
        "domain_rows": pd.DataFrame(domain_rows).sort_values("comments", ascending=False),
        "priority_rows": priority_rows,
    }


def write_html(output_path: Path, summary: dict[str, Any], view: pd.DataFrame, include_raw: bool) -> None:
    title = "VERA VOC Board Review - Unredacted" if include_raw else "VERA VOC Board Review"
    notice = (
        "Restricted internal use: contains raw VOC comment and response text."
        if include_raw
        else "Internal review packet: raw comment text is not included."
    )
    candidate_preview = view[view["FLAG_REVIEW_CANDIDATE"]].head(500)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; color: #17233f; }}
    header {{ background: #1C49C2; color: white; padding: 42px 56px; }}
    main {{ padding: 28px 36px 60px; }}
    h1 {{ margin: 0 0 8px; font-size: 48px; }}
    h2 {{ color: #001A70; margin-top: 32px; }}
    .notice {{ background: #DFEAFF; border: 1px solid #A8B8F7; padding: 12px 14px; border-radius: 8px; max-width: 980px; }}
    .cards {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 18px 0; }}
    .card {{ border: 1px solid #c8d7ff; border-radius: 8px; padding: 12px 14px; min-width: 170px; }}
    .value {{ font-size: 26px; font-weight: 700; color: #001A70; }}
    .table-wrap {{ overflow: auto; max-height: 680px; border: 1px solid #c8d7ff; border-radius: 8px; margin: 12px 0 24px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #c8d7ff; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: #DFEAFF; color: #001A70; }}
  </style>
</head>
<body>
  <header>
    <h1>VERA</h1>
    <div>Turning employee voice into earlier support and stronger follow-through.</div>
  </header>
  <main>
    <div class="notice">{html.escape(notice)}</div>
    <section class="cards">
      <div class="card"><div class="value">{summary["total_comments"]:,}</div><div>VOC Board comments</div></div>
      <div class="card"><div class="value">{summary["review_candidates"]:,}</div><div>Review candidates</div></div>
      <div class="card"><div class="value">{summary["review_candidate_rate"]:.1%}</div><div>Candidate rate</div></div>
    </section>
    <h2>Routing priority</h2>
    <div class="table-wrap">{summary["priority_rows"].to_html(index=False, escape=True)}</div>
    <h2>Review domains</h2>
    <div class="table-wrap">{summary["domain_rows"].to_html(index=False, escape=True)}</div>
    <h2>Candidate audit view preview</h2>
    <p>Showing up to 500 candidate rows. Use the CSV or workbook for full output.</p>
    <div class="table-wrap">{candidate_preview.fillna("").to_html(index=False, escape=True)}</div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def run(input_path: Path, output_dir: Path, taxonomy_path: Path, include_raw: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    taxonomy = load_taxonomy(taxonomy_path)
    raw = pd.read_csv(input_path)
    normalized = normalize_input(raw)
    voc = normalized[
        normalized["VOICE_MECHANISM"].fillna("").astype(str).str.upper().eq("VOC BOARD")
        & normalized["PRIMARY_TEXT_CLEAN"].str.len().gt(0)
    ].copy()
    view = build_view(voc, taxonomy, include_raw=include_raw)
    summary = summarize(view, taxonomy)

    suffix = "unredacted" if include_raw else "redacted"
    view_path = output_dir / f"vera_voc_board_audit_view_output_{suffix}.csv"
    candidate_path = output_dir / f"vera_voc_board_audit_view_candidates_{suffix}.csv"
    workbook_path = output_dir / f"vera_voc_review_workbook_{suffix}.xlsx"
    html_path = output_dir / f"vera_voc_board_review_{suffix}.html"

    view.to_csv(view_path, index=False)
    view[view["FLAG_REVIEW_CANDIDATE"]].to_csv(candidate_path, index=False)
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        pd.DataFrame(
            [
                {"Metric": "VOC Board comments analyzed", "Value": summary["total_comments"]},
                {"Metric": "Review candidates surfaced", "Value": summary["review_candidates"]},
                {"Metric": "Review candidate rate", "Value": summary["review_candidate_rate"]},
                {"Metric": "Contains raw comments", "Value": include_raw},
            ]
        ).to_excel(writer, index=False, sheet_name="Summary")
        summary["domain_rows"].to_excel(writer, index=False, sheet_name="Domain mix")
        summary["priority_rows"].to_excel(writer, index=False, sheet_name="Priority routing")
        view[view["FLAG_REVIEW_CANDIDATE"]].to_excel(writer, index=False, sheet_name="Candidates")
        view.to_excel(writer, index=False, sheet_name="Audit view")
    write_html(html_path, summary, view, include_raw=include_raw)

    print(f"Wrote {view_path}")
    print(f"Wrote {candidate_path}")
    print(f"Wrote {workbook_path}")
    print(f"Wrote {html_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VERA VOC Board audit against an exported CSV.")
    parser.add_argument("--input", required=True, type=Path, help="Path to VOC Board CSV export.")
    parser.add_argument("--output-dir", default=Path("outputs"), type=Path, help="Directory for generated outputs.")
    parser.add_argument(
        "--taxonomy",
        default=Path("config/vera_taxonomy.yml"),
        type=Path,
        help="Path to VERA taxonomy YAML.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw comments and responses in outputs. Use only in approved restricted locations.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input, args.output_dir, args.taxonomy, args.include_raw)
