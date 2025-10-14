#!/usr/bin/python3

import argparse
import sys
from types import SimpleNamespace
from typing import Any, Dict, Sequence, Tuple, Union

from .ms import create_scorer

Usage = (
    "Calculate LDDT for a model structure by comparison with a reference structure"
)


def _normalize_thresholds(distance_thresholds: Union[str, Sequence[float]]) -> Tuple[float, ...]:
    if isinstance(distance_thresholds, str):
        parts = [part.strip() for part in distance_thresholds.split(",") if part.strip()]
        if not parts:
            raise ValueError("distance_thresholds must not be empty")
        return tuple(float(part) for part in parts)
    thresholds = tuple(float(part) for part in distance_thresholds)
    if not thresholds:
        raise ValueError("distance_thresholds must not be empty")
    return thresholds


def calculate_lddt(
    reference_structure: str,
    predicted_structure: str,
    radius: float = 15.0,
    distance_thresholds: Union[str, Sequence[float]] = (0.5, 1.0, 2.0, 4.0),
    symmetry: str = "first",
    return_column_scores: bool = False,
) -> Dict[str, Any]:
    thresholds = _normalize_thresholds(distance_thresholds)
    args = SimpleNamespace(
        radius=radius,
        symmetry=symmetry,
        dists=",".join(f"{value:g}" for value in thresholds),
    )
    scorer = create_scorer(args)
    seq_ref, x_ref, y_ref, z_ref = scorer.read_pdb(reference_structure)
    seq_model, x_model, y_model, z_model = scorer.read_pdb(predicted_structure)
    if len(seq_ref) != len(seq_model):
        raise ValueError("Reference and model sequences must have identical lengths")
    positions_ref = list(range(len(seq_ref)))
    positions_model = list(range(len(seq_model)))
    lddt_value = scorer.lddt_score(
        seq_ref,
        positions_ref,
        x_ref,
        y_ref,
        z_ref,
        seq_model,
        positions_model,
        x_model,
        y_model,
        z_model,
    )
    result: Dict[str, Any] = {"lddt": float(lddt_value)}
    if return_column_scores:
        result["columns"] = [
            {
                "index": index,
                "residue": residue,
                "nr_preserved": int(preserved),
                "nr_considered": int(considered),
                "score": float(score),
            }
            for index, (residue, preserved, considered, score) in enumerate(
                zip(seq_ref, scorer.nr_preserveds, scorer.nr_considereds, scorer.col_scores)
            )
        ]
    return result


def _main() -> None:
    parser = argparse.ArgumentParser(description=Usage)
    parser.add_argument("--ref", required=True, help="PDB file of reference structure")
    parser.add_argument("--model", required=True, help="PDB file of predicted structure")
    parser.add_argument(
        "--radius",
        required=False,
        type=float,
        default=15.0,
        help="Inclusion radius (R0 parameter, default 15)",
    )
    parser.add_argument(
        "--dists",
        required=False,
        default="0.5,1,2,4",
        help="Distance thresholds, comma-separated (default 0.5,1,2,4)",
    )
    parser.add_argument(
        "--cols",
        required=False,
        default="no",
        choices=["yes", "no"],
        help="Report column scores yes/no (default no)",
    )
    args = parser.parse_args()
    try:
        result = calculate_lddt(
            reference_structure=args.ref,
            predicted_structure=args.model,
            radius=args.radius,
            distance_thresholds=args.dists,
            return_column_scores=args.cols == "yes",
        )
    except ValueError as exc:
        sys.stderr.write(f"\n===ERROR=== {exc}\n")
        sys.exit(1)
    if args.cols == "yes":
        print("col\taa\tnr_pres\tnr_cons\tscore")
        for column in result.get("columns", []):
            print(
                "{}\t{}\t{}\t{}\t{:.4f}".format(
                    column["index"],
                    column["residue"],
                    column["nr_preserved"],
                    column["nr_considered"],
                    column["score"],
                )
            )
    print(f"LDDT_model\t{result['lddt']:.4f}")


if __name__ == "__main__":
    _main()

