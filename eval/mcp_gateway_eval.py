"""Eval harness for the MCP tool-call boundary.

Feeds every labeled case in eval/dataset.py through the same decision
function the live middleware uses (app.mcp.middleware.decide), compares
predicted vs. labeled outcome, and reports precision/recall/false-positive
rate plus a confusion matrix.

Run: python eval/mcp_gateway_eval.py
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.mcp.middleware import decide  # noqa: E402
from eval.dataset import CASES  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def predicted_label(decision: str) -> str:
    # A "review" outcome is held + logged, not silently allowed - it counts
    # as "caught" for eval purposes, same as a hard block.
    return "malicious" if decision in ("block", "review") else "benign"


def run_eval(cases):
    rows = []
    for case in cases:
        decision, reason, _args_obj = decide(case["tool"], case["args"])
        predicted = predicted_label(decision)
        rows.append(
            {
                "id": case["id"],
                "tool": case["tool"],
                "attack_class": case["attack_class"],
                "label": case["label"],
                "decision": decision,
                "reason": reason,
                "predicted": predicted,
                "correct": predicted == case["label"],
            }
        )
    return rows


def confusion_matrix(rows):
    tp = sum(1 for r in rows if r["label"] == "malicious" and r["predicted"] == "malicious")
    fn = sum(1 for r in rows if r["label"] == "malicious" and r["predicted"] == "benign")
    fp = sum(1 for r in rows if r["label"] == "benign" and r["predicted"] == "malicious")
    tn = sum(1 for r in rows if r["label"] == "benign" and r["predicted"] == "benign")
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn}


def compute_metrics(cm):
    tp, fn, fp, tn = cm["tp"], cm["fn"], cm["fp"], cm["tn"]
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    fpr = fp / (fp + tn) if (fp + tn) > 0 else None
    return {"precision": precision, "recall": recall, "false_positive_rate": fpr}


def per_attack_class_breakdown(rows):
    breakdown = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in rows:
        key = r["attack_class"]
        breakdown[key]["total"] += 1
        if r["correct"]:
            breakdown[key]["correct"] += 1
    return dict(breakdown)


def _fmt(value):
    return f"{value:.3f}" if value is not None else "n/a"


def print_report(rows, cm, metrics, breakdown):
    print(f"MCP gateway eval — {len(rows)} cases\n")

    print("Confusion matrix (predicted malicious = block or review):")
    print("                 predicted_benign  predicted_malicious")
    print(f"  actual_benign  {cm['tn']:>16} {cm['fp']:>20}")
    print(f"  actual_malicious {cm['fn']:>14} {cm['tp']:>20}")
    print()

    print(f"precision:            {_fmt(metrics['precision'])}")
    print(f"recall:               {_fmt(metrics['recall'])}")
    print(f"false_positive_rate:  {_fmt(metrics['false_positive_rate'])}")
    print()

    print("Per-attack-class breakdown:")
    for attack_class, stats in sorted(breakdown.items()):
        print(f"  {attack_class:20s} {stats['correct']}/{stats['total']} correct")
    print()

    incorrect = [r for r in rows if not r["correct"]]
    if incorrect:
        print(f"Incorrect predictions ({len(incorrect)}):")
        for r in incorrect:
            print(
                f"  {r['id']}: label={r['label']} predicted={r['predicted']} reason={r['reason']}"
            )
    else:
        print("No incorrect predictions.")


def write_artifacts(rows, cm, metrics, breakdown):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = RESULTS_DIR / "mcp_gateway_eval_results.json"
    json_path.write_text(
        json.dumps(
            {"cases": rows, "confusion_matrix": cm, "metrics": metrics, "breakdown": breakdown},
            indent=2,
        )
    )

    csv_path = RESULTS_DIR / "mcp_gateway_eval_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "tool",
                "attack_class",
                "label",
                "decision",
                "reason",
                "predicted",
                "correct",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return json_path, csv_path


def main():
    rows = run_eval(CASES)
    cm = confusion_matrix(rows)
    metrics = compute_metrics(cm)
    breakdown = per_attack_class_breakdown(rows)

    print_report(rows, cm, metrics, breakdown)

    json_path, csv_path = write_artifacts(rows, cm, metrics, breakdown)
    print(f"\nWrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
