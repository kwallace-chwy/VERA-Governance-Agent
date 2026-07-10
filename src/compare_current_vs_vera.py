from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BENIGN_CONTEXT_PATTERN = re.compile(
    r"\b(safe\s+travel\w*|travel\s+safe\w*|touch\s*screen\w*|touchscreen\w*|high\s+five\w*)\b",
    flags=re.IGNORECASE | re.DOTALL,
)

CONTEXTUAL_SAFETY_PATTERN = re.compile(
    r"\b(unsafe|not\s+safe|hazard\w*|get\s+hurt|hurt\s+badly|"
    r"safety\s+(has\s+been\s+)?compromis\w*|jeopardiz\w*\s+safety|"
    r"safety\s+(concern|concerns|issue|issues|risk|risks))\b",
    flags=re.IGNORECASE | re.DOTALL,
)


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).strip()


def normalize_text_for_match(value: object) -> str:
    return clean_text(value).casefold()


def normalize_text_for_fuzzy_match(value: object) -> str:
    text = normalize_text_for_match(value)
    # Normalize common display/export differences without changing the meaning.
    text = text.replace("brakeroom", "breakroom")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def text_hash(value: object) -> str:
    normalized = normalize_text_for_match(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def canonical_column_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def find_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    lookup = {canonical_column_name(column): column for column in df.columns}
    for candidate in candidates:
        found = lookup.get(canonical_column_name(candidate))
        if found:
            return found
    if required:
        raise ValueError(f"Missing required column. Expected one of: {', '.join(candidates)}")
    return None


def read_current_export(path: Path) -> pd.DataFrame:
    attempts = [
        {"encoding": "utf-16", "sep": "\t"},
        {"encoding": "utf-8-sig", "sep": ","},
        {"encoding": "utf-8-sig", "sep": "\t"},
        {"encoding": "cp1252", "sep": ","},
    ]
    last_error: Exception | None = None
    for options in attempts:
        try:
            df = pd.read_csv(path, **options)
            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
            if df.shape[1] > 1:
                return df
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise ValueError(f"Could not read current export {path}") from last_error


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().casefold() in {"true", "t", "1", "yes", "y"}


def add_match_keys(df: pd.DataFrame, site_col: str, date_col: str, text_col: str) -> pd.DataFrame:
    keyed = df.copy()
    keyed["_ROW_ID"] = range(len(keyed))
    keyed["_MATCH_SITE"] = keyed[site_col].fillna("").astype(str).str.strip().str.upper()
    keyed["_MATCH_DATE"] = pd.to_datetime(keyed[date_col], errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    keyed["_MATCH_TEXT_HASH"] = keyed[text_col].map(text_hash)
    keyed["_FUZZY_TEXT"] = keyed[text_col].map(normalize_text_for_fuzzy_match)
    keyed["_MATCH_KEY"] = keyed["_MATCH_SITE"] + "|" + keyed["_MATCH_DATE"] + "|" + keyed["_MATCH_TEXT_HASH"]
    keyed["_MATCH_OCCURRENCE"] = keyed.groupby("_MATCH_KEY", dropna=False).cumcount()
    return keyed


def find_fuzzy_matches(
    left: pd.DataFrame,
    right: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    matches = []
    used_right_ids: set[int] = set()

    for _, left_row in left.sort_values(["_MATCH_DATE", "_MATCH_SITE", "_ROW_ID"]).iterrows():
        candidates = right[
            (right["_MATCH_SITE"] == left_row["_MATCH_SITE"])
            & (right["_MATCH_DATE"] == left_row["_MATCH_DATE"])
            & (~right["_ROW_ID"].isin(used_right_ids))
        ]
        if candidates.empty:
            continue

        best_score = 0.0
        best_row: pd.Series | None = None
        left_text = str(left_row["_FUZZY_TEXT"])
        for _, right_row in candidates.iterrows():
            score = difflib.SequenceMatcher(None, left_text, str(right_row["_FUZZY_TEXT"])).ratio()
            if score > best_score:
                best_score = score
                best_row = right_row

        if best_row is not None and best_score >= threshold:
            used_right_ids.add(int(best_row["_ROW_ID"]))
            matches.append(
                {
                    "current_row_id": int(left_row["_ROW_ID"]),
                    "vera_row_id": int(best_row["_ROW_ID"]),
                    "match_similarity": round(best_score, 4),
                }
            )

    return pd.DataFrame(matches)


def find_dashboard_semantic_matches(
    vera_rows: pd.DataFrame,
    current_rows: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    matches = []

    for _, vera_row in vera_rows.sort_values(["_MATCH_DATE", "_MATCH_SITE", "_ROW_ID"]).iterrows():
        candidates = current_rows[
            (current_rows["_MATCH_SITE"] == vera_row["_MATCH_SITE"])
            & (current_rows["_MATCH_DATE"] == vera_row["_MATCH_DATE"])
        ]
        if candidates.empty:
            continue

        best_score = 0.0
        best_row: pd.Series | None = None
        vera_text = str(vera_row["_FUZZY_TEXT"])
        for _, current_row in candidates.iterrows():
            score = difflib.SequenceMatcher(None, vera_text, str(current_row["_FUZZY_TEXT"])).ratio()
            if score > best_score:
                best_score = score
                best_row = current_row

        if best_row is not None and best_score >= threshold:
            matches.append(
                {
                    "vera_row_id": int(vera_row["_ROW_ID"]),
                    "current_row_id": int(best_row["_ROW_ID"]),
                    "match_similarity": round(best_score, 4),
                }
            )

    return pd.DataFrame(matches)


def split_risky_words(value: object) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [clean_text(word).casefold() for word in parsed if clean_text(word)]
    except json.JSONDecodeError:
        pass
    text = re.sub(r"[\[\]\"]", "", text)
    return [word.strip().casefold() for word in re.split(r"[,;|]", text) if word.strip()]


def classify_current_only(row: pd.Series, feedback_col: str) -> str:
    text = clean_text(row.get(feedback_col, ""))
    if not bool(row.get("CURRENT_MATCHED_TO_VERA_SOURCE", False)):
        return "current_export_row_not_in_vera_source"
    if BENIGN_CONTEXT_PATTERN.search(text):
        return "possible_current_false_positive_benign_context"
    if CONTEXTUAL_SAFETY_PATTERN.search(text):
        return "possible_vera_recall_gap_contextual_safety"
    return "current_only_broad_keyword_review"


def comparison_bucket(row: pd.Series) -> str:
    matched = bool(row.get("CURRENT_MATCHED_TO_VERA_SOURCE", False))
    vera_flagged = bool(row.get("VERA_FLAG_REVIEW_CANDIDATE", False))
    if not matched:
        return "current_unmatched_to_vera_source"
    if vera_flagged:
        return "both_caught"
    return "current_only_vera_not_flagged"


def safe_to_html(df: pd.DataFrame, include_raw_html: bool, preview_rows: int) -> str:
    preview = df.head(preview_rows).copy()
    if not include_raw_html:
        raw_like = [
            column
            for column in preview.columns
            if column.casefold() in {"feedback", "comment", "primary_text", "response", "resolution"}
        ]
        preview = preview.drop(columns=raw_like, errors="ignore")
    return preview.fillna("").to_html(index=False, escape=True)


def build_report_html(
    output_path: Path,
    summary: pd.DataFrame,
    top_risky: pd.DataFrame,
    current_only: pd.DataFrame,
    vera_only: pd.DataFrame,
    edge_queue: pd.DataFrame,
    include_raw_html: bool,
    preview_rows: int,
) -> None:
    raw_notice = (
        "Restricted internal use: this report includes raw feedback text."
        if include_raw_html
        else "Raw feedback text is excluded from this HTML preview."
    )
    generated = datetime.now().isoformat(timespec="seconds")
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VERA Current Process Comparison</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; color: #17233f; }}
    header {{ background: #1C49C2; color: white; padding: 36px 52px; }}
    main {{ padding: 28px 36px 60px; }}
    h1 {{ margin: 0 0 8px; font-size: 42px; }}
    h2 {{ color: #001A70; margin-top: 30px; }}
    .notice {{ background: #DFEAFF; border: 1px solid #A8B8F7; padding: 12px 14px; border-radius: 8px; max-width: 1080px; }}
    .table-wrap {{ overflow: auto; max-height: 620px; border: 1px solid #c8d7ff; border-radius: 8px; margin: 12px 0 24px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #c8d7ff; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: #DFEAFF; color: #001A70; }}
  </style>
</head>
<body>
  <header>
    <h1>VERA Current Process Comparison</h1>
    <div>Deterministic capture first, AI edge-case review second.</div>
  </header>
  <main>
    <div class="notice">{html.escape(raw_notice)} Generated {html.escape(generated)}.</div>
    <h2>Summary</h2>
    <div class="table-wrap">{summary.to_html(index=False, escape=True)}</div>
    <h2>Top current-process risky words</h2>
    <div class="table-wrap">{top_risky.to_html(index=False, escape=True)}</div>
    <h2>Current-only: flagged by current email, not flagged by VERA</h2>
    <div class="table-wrap">{safe_to_html(current_only, include_raw_html, preview_rows)}</div>
    <h2>VERA-only: flagged by VERA, absent from current export</h2>
    <div class="table-wrap">{safe_to_html(vera_only, include_raw_html, preview_rows)}</div>
    <h2>AI edge review queue</h2>
    <div class="table-wrap">{safe_to_html(edge_queue, include_raw_html, preview_rows)}</div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def compare(current_export: Path, vera_output: Path, output_dir: Path, include_raw_html: bool, preview_rows: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    current = read_current_export(current_export)
    vera = pd.read_csv(vera_output)

    current_date_col = find_column(current, ["Date_Posted", "Date Posted"])
    current_site_col = find_column(current, ["Site", "Fulfillment_Center", "Fulfillment Center"])
    current_priority_col = find_column(current, ["Er Priority Level", "ER_Priority_Level"])
    current_risky_col = find_column(current, ["RISKY_W_LS", "risky_words", "Risky Words"], required=False)
    current_feedback_col = find_column(current, ["Feedback", "__________Feedback__________"])
    current_response_col = find_column(current, ["Resolution", "__________Resolution__________"], required=False)

    vera_date_col = find_column(vera, ["ROW_DATE", "Date_Posted"])
    vera_site_col = find_column(vera, ["SITE_CODE", "Site", "Location"])
    vera_feedback_col = find_column(vera, ["PRIMARY_TEXT", "VOC_COMMENT", "Feedback"])

    current_dates = pd.to_datetime(current[current_date_col], errors="coerce").dropna()
    current_min_date = current_dates.min().normalize() if not current_dates.empty else None
    current_max_date = current_dates.max().normalize() if not current_dates.empty else None
    if current_min_date is not None and current_max_date is not None:
        vera_dates = pd.to_datetime(vera[vera_date_col], errors="coerce")
        vera = vera[(vera_dates >= current_min_date) & (vera_dates <= current_max_date)].copy()

    current_keyed = add_match_keys(current, current_site_col, current_date_col, current_feedback_col)
    vera_keyed = add_match_keys(vera, vera_site_col, vera_date_col, vera_feedback_col)

    vera_keyed["VERA_FLAG_REVIEW_CANDIDATE"] = vera_keyed["FLAG_REVIEW_CANDIDATE"].map(parse_bool)
    vera_match_cols = [
        "_MATCH_KEY",
        "_MATCH_OCCURRENCE",
        "_ROW_ID",
        "COMMENT_HASH",
        "AUDIT_PRIORITY",
        "AUDIT_REASON_CODES",
        "VERA_FLAG_REVIEW_CANDIDATE",
        "AUDIT_METHOD_VERSION",
    ]
    optional_match_cols = ["DETERMINISTIC_SOURCE", "NEEDS_AI_EDGE_REVIEW", "AI_EDGE_REVIEW_REASON"]
    vera_match_cols.extend([column for column in optional_match_cols if column in vera_keyed.columns])
    vera_match = vera_keyed[vera_match_cols].rename(
        columns={
            "_ROW_ID": "VERA_ROW_ID",
            "COMMENT_HASH": "VERA_COMMENT_HASH",
            "AUDIT_PRIORITY": "VERA_AUDIT_PRIORITY",
            "AUDIT_REASON_CODES": "VERA_AUDIT_REASON_CODES",
            "AUDIT_METHOD_VERSION": "VERA_AUDIT_METHOD_VERSION",
        }
    )

    current_comp = current_keyed.merge(
        vera_match,
        how="left",
        on=["_MATCH_KEY", "_MATCH_OCCURRENCE"],
    )
    current_comp["DASHBOARD_MATCH_METHOD"] = current_comp["VERA_COMMENT_HASH"].notna().map(
        {True: "exact_text_hash", False: ""}
    )
    current_comp["DASHBOARD_MATCH_SIMILARITY"] = pd.NA

    exact_matched_vera_ids = set(
        current_comp["VERA_ROW_ID"].dropna().astype(int).tolist()
        if "VERA_ROW_ID" in current_comp.columns
        else []
    )
    unmatched_current_for_fuzzy = current_keyed[
        current_keyed["_ROW_ID"].isin(current_comp[current_comp["VERA_COMMENT_HASH"].isna()]["_ROW_ID"])
    ].copy()
    unmatched_vera_for_fuzzy = vera_keyed[~vera_keyed["_ROW_ID"].isin(exact_matched_vera_ids)].copy()
    fuzzy_matches = find_fuzzy_matches(unmatched_current_for_fuzzy, unmatched_vera_for_fuzzy, threshold=0.92)

    if not fuzzy_matches.empty:
        fuzzy_vera = vera_keyed[
            [
                "_ROW_ID",
                "COMMENT_HASH",
                "AUDIT_PRIORITY",
                "AUDIT_REASON_CODES",
                "VERA_FLAG_REVIEW_CANDIDATE",
                "AUDIT_METHOD_VERSION",
            ]
        ].rename(
            columns={
                "_ROW_ID": "vera_row_id",
                "COMMENT_HASH": "VERA_COMMENT_HASH",
                "AUDIT_PRIORITY": "VERA_AUDIT_PRIORITY",
                "AUDIT_REASON_CODES": "VERA_AUDIT_REASON_CODES",
                "AUDIT_METHOD_VERSION": "VERA_AUDIT_METHOD_VERSION",
            }
        )
        for column in optional_match_cols:
            if column in vera_keyed.columns:
                fuzzy_vera[column] = vera_keyed[column]

        fuzzy_enriched = fuzzy_matches.merge(fuzzy_vera, how="left", on="vera_row_id")
        fuzzy_by_current = fuzzy_enriched.set_index("current_row_id")
        for current_row_id, fuzzy_row in fuzzy_by_current.iterrows():
            mask = current_comp["_ROW_ID"].eq(current_row_id)
            current_comp.loc[mask, "VERA_ROW_ID"] = fuzzy_row["vera_row_id"]
            current_comp.loc[mask, "VERA_COMMENT_HASH"] = fuzzy_row["VERA_COMMENT_HASH"]
            current_comp.loc[mask, "VERA_AUDIT_PRIORITY"] = fuzzy_row["VERA_AUDIT_PRIORITY"]
            current_comp.loc[mask, "VERA_AUDIT_REASON_CODES"] = fuzzy_row["VERA_AUDIT_REASON_CODES"]
            current_comp.loc[mask, "VERA_FLAG_REVIEW_CANDIDATE"] = fuzzy_row["VERA_FLAG_REVIEW_CANDIDATE"]
            current_comp.loc[mask, "VERA_AUDIT_METHOD_VERSION"] = fuzzy_row["VERA_AUDIT_METHOD_VERSION"]
            current_comp.loc[mask, "DASHBOARD_MATCH_METHOD"] = "same_site_date_fuzzy_text"
            current_comp.loc[mask, "DASHBOARD_MATCH_SIMILARITY"] = fuzzy_row["match_similarity"]
            for column in optional_match_cols:
                if column in fuzzy_row:
                    current_comp.loc[mask, column] = fuzzy_row[column]

    current_comp["CURRENT_MATCHED_TO_VERA_SOURCE"] = current_comp["VERA_COMMENT_HASH"].notna()
    current_comp["VERA_FLAG_REVIEW_CANDIDATE"] = current_comp["VERA_FLAG_REVIEW_CANDIDATE"].map(parse_bool)
    current_comp["COMPARISON_BUCKET"] = current_comp.apply(comparison_bucket, axis=1)
    current_comp["AI_EDGE_REVIEW_RECOMMENDED"] = current_comp["COMPARISON_BUCKET"].isin(
        ["current_only_vera_not_flagged", "current_unmatched_to_vera_source"]
    )
    current_comp["AI_EDGE_REVIEW_REASON"] = current_comp.apply(
        lambda row: classify_current_only(row, current_feedback_col)
        if bool(row["AI_EDGE_REVIEW_RECOMMENDED"])
        else None,
        axis=1,
    )

    matched_vera_row_ids = set(current_comp["VERA_ROW_ID"].dropna().astype(int).tolist())
    vera_candidates = vera_keyed[vera_keyed["VERA_FLAG_REVIEW_CANDIDATE"]].copy()
    vera_only = vera_candidates[~vera_candidates["_ROW_ID"].isin(matched_vera_row_ids)].copy()
    dashboard_semantic_matches = find_dashboard_semantic_matches(vera_only, current_keyed, threshold=0.92)
    if not dashboard_semantic_matches.empty:
        dashboard_semantic_vera_ids = set(dashboard_semantic_matches["vera_row_id"].astype(int).tolist())
        dashboard_semantic_export = dashboard_semantic_matches.merge(
            vera_only,
            how="left",
            left_on="vera_row_id",
            right_on="_ROW_ID",
        ).merge(
            current_keyed[
                [
                    "_ROW_ID",
                    current_date_col,
                    current_site_col,
                    current_priority_col,
                    current_feedback_col,
                    *([current_risky_col] if current_risky_col else []),
                ]
            ],
            how="left",
            left_on="current_row_id",
            right_on="_ROW_ID",
            suffixes=("_vera", "_dashboard"),
        )
        vera_only = vera_only[~vera_only["_ROW_ID"].isin(dashboard_semantic_vera_ids)].copy()
    else:
        dashboard_semantic_export = pd.DataFrame()

    vera_only["_CURRENT_EXPORT_PRESENT"] = False
    vera_only["COMPARISON_BUCKET"] = "vera_only_candidate"
    vera_only["AI_EDGE_REVIEW_RECOMMENDED"] = True
    vera_only["AI_EDGE_REVIEW_REASON"] = "vera_only_net_new_signal_review"

    current_only = current_comp[current_comp["COMPARISON_BUCKET"].eq("current_only_vera_not_flagged")].copy()
    current_unmatched = current_comp[current_comp["COMPARISON_BUCKET"].eq("current_unmatched_to_vera_source")].copy()

    current_edge_cols = [
        current_date_col,
        current_site_col,
        current_priority_col,
        current_feedback_col,
        "CURRENT_MATCHED_TO_VERA_SOURCE",
        "COMPARISON_BUCKET",
        "VERA_AUDIT_PRIORITY",
        "VERA_AUDIT_REASON_CODES",
        "DASHBOARD_MATCH_METHOD",
        "DASHBOARD_MATCH_SIMILARITY",
        "AI_EDGE_REVIEW_RECOMMENDED",
        "AI_EDGE_REVIEW_REASON",
    ]
    if current_risky_col:
        current_edge_cols.insert(3, current_risky_col)
    if current_response_col:
        current_edge_cols.insert(5 if current_risky_col else 4, current_response_col)

    current_edge = pd.concat([current_only, current_unmatched], ignore_index=True)[current_edge_cols].copy()
    current_edge.insert(0, "SOURCE_SYSTEM", "current_process")

    vera_edge_cols = [
        vera_date_col,
        vera_site_col,
        vera_feedback_col,
        "AUDIT_PRIORITY",
        "AUDIT_REASON_CODES",
        "COMPARISON_BUCKET",
        "AI_EDGE_REVIEW_RECOMMENDED",
        "AI_EDGE_REVIEW_REASON",
    ]
    if "RESOLUTION" in vera_only.columns:
        vera_edge_cols.insert(3, "RESOLUTION")
    vera_edge = vera_only[vera_edge_cols].copy()
    vera_edge.insert(0, "SOURCE_SYSTEM", "vera")

    edge_queue = pd.concat([current_edge, vera_edge], ignore_index=True, sort=False)

    risky_words = []
    if current_risky_col:
        for value in current[current_risky_col]:
            risky_words.extend(split_risky_words(value))
    top_risky = (
        pd.Series(risky_words, name="risky_word")
        .value_counts()
        .head(25)
        .rename_axis("risky_word")
        .reset_index(name="current_process_rows")
        if risky_words
        else pd.DataFrame(columns=["risky_word", "current_process_rows"])
    )

    summary_rows: list[dict[str, Any]] = [
        {"metric": "comparison_date_window_start", "value": current_min_date.strftime("%Y-%m-%d") if current_min_date is not None else ""},
        {"metric": "comparison_date_window_end", "value": current_max_date.strftime("%Y-%m-%d") if current_max_date is not None else ""},
        {"metric": "current_process_rows", "value": len(current_comp)},
        {"metric": "current_rows_exact_matched_to_vera_source", "value": int(current_comp["DASHBOARD_MATCH_METHOD"].eq("exact_text_hash").sum())},
        {"metric": "current_rows_fuzzy_matched_to_vera_source", "value": int(current_comp["DASHBOARD_MATCH_METHOD"].eq("same_site_date_fuzzy_text").sum())},
        {"metric": "current_rows_matched_to_vera_source", "value": int(current_comp["CURRENT_MATCHED_TO_VERA_SOURCE"].sum())},
        {"metric": "current_rows_unmatched_to_vera_source", "value": int((~current_comp["CURRENT_MATCHED_TO_VERA_SOURCE"]).sum())},
        {"metric": "current_rows_flagged_by_vera", "value": int(current_comp["VERA_FLAG_REVIEW_CANDIDATE"].sum())},
        {"metric": "current_rows_not_flagged_by_vera", "value": int(len(current_only))},
        {"metric": "vera_total_rows", "value": len(vera_keyed)},
        {"metric": "vera_review_candidates", "value": int(vera_keyed["VERA_FLAG_REVIEW_CANDIDATE"].sum())},
        {"metric": "vera_candidate_semantic_matches_in_current_export", "value": len(dashboard_semantic_matches)},
        {"metric": "vera_only_candidates", "value": len(vera_only)},
        {"metric": "ai_edge_review_queue_rows", "value": len(edge_queue)},
    ]
    if not current_only.empty:
        summary_rows.append(
            {
                "metric": "current_only_possible_benign_context",
                "value": int(current_only[current_only["AI_EDGE_REVIEW_REASON"].eq("possible_current_false_positive_benign_context")].shape[0]),
            }
        )
        summary_rows.append(
            {
                "metric": "current_only_possible_safety_recall_gap",
                "value": int(current_only[current_only["AI_EDGE_REVIEW_REASON"].eq("possible_vera_recall_gap_contextual_safety")].shape[0]),
            }
        )
    summary = pd.DataFrame(summary_rows)

    summary.to_csv(output_dir / "current_vs_vera_summary.csv", index=False)
    top_risky.to_csv(output_dir / "current_process_top_risky_words.csv", index=False)
    current_comp.to_csv(output_dir / "current_rows_with_vera_match.csv", index=False)
    current_only.to_csv(output_dir / "current_only_vera_not_flagged.csv", index=False)
    current_unmatched.to_csv(output_dir / "current_unmatched_to_vera_source.csv", index=False)
    vera_only.to_csv(output_dir / "vera_only_candidates.csv", index=False)
    fuzzy_matches.to_csv(output_dir / "fuzzy_dashboard_vera_matches.csv", index=False)
    dashboard_semantic_export.to_csv(output_dir / "dashboard_semantic_matches.csv", index=False)
    edge_queue.to_csv(output_dir / "ai_edge_review_queue.csv", index=False)
    build_report_html(
        output_dir / "current_vs_vera_comparison_report.html",
        summary,
        top_risky,
        current_only,
        vera_only,
        edge_queue,
        include_raw_html=include_raw_html,
        preview_rows=preview_rows,
    )

    print(f"Wrote outputs to {output_dir}")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare the current ER escalation export to VERA output.")
    parser.add_argument("--current-export", required=True, type=Path, help="Path to current ER escalation CSV export.")
    parser.add_argument("--vera-output", required=True, type=Path, help="Path to VERA unredacted audit-view CSV.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for comparison outputs.")
    parser.add_argument(
        "--include-raw-html",
        action="store_true",
        help="Include raw feedback text in the HTML preview. Use only in restricted locations.",
    )
    parser.add_argument("--preview-rows", type=int, default=250, help="Rows to show in the HTML preview tables.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    compare(args.current_export, args.vera_output, args.output_dir, args.include_raw_html, args.preview_rows)
