"""Evaluate article-filter model output against ground-truth DOI lists.

Metrics computed (positive class = relevant):
  Precision  = TP / (TP + FP)
  Recall     = TP / (TP + FN)
  Accuracy   = (TP + TN) / (TP + FP + TN + FN)
  F1         = 2 * Precision * Recall / (Precision + Recall)

DOIs that appear in the ground truth but in neither model-output file are
treated as *skipped* and excluded from the metric calculation.
DOIs that appear in the model output but not in the ground truth are flagged
as *unknown*.
"""

import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dois(path: Path) -> set[str]:
    """Return a set of non-empty, stripped DOI strings from *path*."""
    with open(path, "r") as f:
        return {line.strip() for line in f if line.strip()}


def compute_metrics(tp: int, fp: int, tn: int, fn: int) -> dict[str, float]:
    """Return precision, recall, accuracy and F1 given a confusion matrix."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    accuracy  = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
    f1        = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {"precision": precision, "recall": recall, "accuracy": accuracy, "f1": f1}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate article-filter model output against ground-truth DOI lists. "
            "Computes precision, recall, accuracy and F1 (positive class = relevant)."
        )
    )
    parser.add_argument(
        "--gt_dir",
        type=Path,
        default=Path(__file__).parent.parent / "test_data" / "input",
        help=(
            "Directory containing ground-truth files "
            "(relevant_dois.txt and not_relevant_dois.txt). "
            "Defaults to <repo_root>/test_data/input."
        ),
    )
    parser.add_argument(
        "--pred_dir",
        type=Path,
        required=True,
        help=(
            "Directory containing model-output files "
            "(relevant.txt and not_relevant.txt). "
            "Evaluation results will also be saved here."
        ),
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Load files
    # ------------------------------------------------------------------
    gt_relevant     = load_dois(args.gt_dir  / "relevant_dois.txt")
    gt_not_relevant = load_dois(args.gt_dir  / "not_relevant_dois.txt")
    pred_relevant     = load_dois(args.pred_dir / "relevant.txt")
    pred_not_relevant = load_dois(args.pred_dir / "not_relevant.txt")

    all_gt   = gt_relevant | gt_not_relevant
    all_pred = pred_relevant | pred_not_relevant

    # DOIs in ground truth but not classified by the model
    skipped = all_gt - all_pred
    # DOIs classified by the model but absent from the ground truth
    unknown = all_pred - all_gt
    # DOIs present in both — these are the ones we can evaluate on
    evaluated = all_gt & all_pred

    # ------------------------------------------------------------------
    # Confusion matrix  (evaluated subset only)
    # ------------------------------------------------------------------
    tp = len(evaluated & pred_relevant     & gt_relevant)
    fp = len(evaluated & pred_relevant     & gt_not_relevant)
    tn = len(evaluated & pred_not_relevant & gt_not_relevant)
    fn = len(evaluated & pred_not_relevant & gt_relevant)

    metrics = compute_metrics(tp, fp, tn, fn)

    # ------------------------------------------------------------------
    # Format report
    # ------------------------------------------------------------------
    sep  = "=" * 42
    dash = "-" * 42

    lines = [
        "Article Filter — Evaluation Results",
        sep,
        f"Ground-truth directory : {args.gt_dir}",
        f"Predictions directory  : {args.pred_dir}",
        "",
        "Dataset summary",
        dash,
        f"  GT relevant              : {len(gt_relevant):>4}",
        f"  GT not relevant          : {len(gt_not_relevant):>4}",
        f"  Predicted relevant       : {len(pred_relevant):>4}",
        f"  Predicted not relevant   : {len(pred_not_relevant):>4}",
        f"  Skipped (GT, unclassified): {len(skipped):>3}",
        f"  Unknown (pred, not in GT) : {len(unknown):>3}",
        f"  Evaluated DOIs           : {len(evaluated):>4}",
        "",
        "Confusion matrix  (positive = relevant)",
        dash,
        f"  TP (correctly relevant)      : {tp:>4}",
        f"  FP (wrongly relevant)        : {fp:>4}",
        f"  TN (correctly not relevant)  : {tn:>4}",
        f"  FN (wrongly not relevant)    : {fn:>4}",
        "",
        "Metrics",
        dash,
        f"  Precision : {metrics['precision']:.4f}",
        f"  Recall    : {metrics['recall']:.4f}",
        f"  Accuracy  : {metrics['accuracy']:.4f}",
        f"  F1 Score  : {metrics['f1']:.4f}",
    ]

    fp_dois = evaluated & pred_relevant     & gt_not_relevant
    fn_dois = evaluated & pred_not_relevant & gt_relevant

    if fp_dois:
        lines += ["", "False Positives (predicted relevant, GT not relevant):"]
        lines += [f"  {d}" for d in sorted(fp_dois)]

    if fn_dois:
        lines += ["", "False Negatives (predicted not relevant, GT relevant):"]
        lines += [f"  {d}" for d in sorted(fn_dois)]

    if skipped:
        lines += ["", "Skipped DOIs (in GT, not classified):"]
        lines += [f"  {d}" for d in sorted(skipped)]

    if unknown:
        lines += ["", "Unknown DOIs (classified, not in GT):"]
        lines += [f"  {d}" for d in sorted(unknown)]

    report = "\n".join(lines)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    print(report)

    result_path = args.pred_dir / "eval_results.txt"
    with open(result_path, "w") as f:
        f.write(report + "\n")

    print(f"\nResults saved to {result_path}")


if __name__ == "__main__":
    main()
