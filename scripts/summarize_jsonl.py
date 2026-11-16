"""Optional retrospective counts from EXISTING LLM JSONL output.

This does not reconstruct historical manual-review counts or historical candidate-selection rules.
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl_path", help="Path to saved deepseek_results.jsonl")
    args = parser.parse_args()
    path = Path(args.jsonl_path)
    stats = Counter()
    doc_ids = set()
    positive_words = {"有", "是", "yes", "true"}
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            stats["saved_records"] += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats["invalid_jsonl_lines"] += 1
                continue
            doc_id = str(record.get("doc_id", ""))
            if doc_id:
                doc_ids.add(doc_id)
            response = record.get("response")
            if not isinstance(response, dict):
                stats["non_dict_response"] += 1
                continue
            node = response.get("serendipity_innovation", {})
            if not isinstance(node, dict):
                stats["missing_schema_root"] += 1
                continue
            stats["parsed_root_records"] += 1
            indication = node.get("迹象", {})
            if isinstance(indication, dict) and str(indication.get("结果", "")).strip().lower() in positive_words:
                stats["positive_overall_signal_rule_only"] += 1
    print(f"File: {path}")
    for key in ("saved_records", "invalid_jsonl_lines", "non_dict_response", "missing_schema_root", "parsed_root_records", "positive_overall_signal_rule_only"):
        print(f"{key}: {stats[key]}")
    print(f"distinct_nonempty_doc_ids: {len(doc_ids)}")
    print("WARNING: 'positive_overall_signal_rule_only' is a NEW explicit retrospective extraction rule.")
    print("It is not an original candidate count, human review count, or validated exaptation count.")


if __name__ == "__main__":
    main()
