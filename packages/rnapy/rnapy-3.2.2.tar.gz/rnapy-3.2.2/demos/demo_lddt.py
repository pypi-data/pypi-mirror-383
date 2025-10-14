from pathlib import Path

from rnapy.toolkit import RNAToolkit


# Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# Prepare demo inputs
demo_dir = Path(__file__).resolve().parent
reference_structure = demo_dir / "input" / "2zh6_B.pdb"
predicted_structure = demo_dir / "input" / "R1107.pdb"

# Run LDDT calculation
result = toolkit.calculate_lddt(
	reference_structure=str(reference_structure),
	predicted_structure=str(predicted_structure),
	radius=15.0,
	distance_thresholds=(0.5, 1.0, 2.0, 4.0),
	return_column_scores=True,
)

print(f"Reference structure: {reference_structure}")
print(f"Predicted structure: {predicted_structure}")
print(f"Global LDDT score: {result['lddt']:.4f}")

columns = result.get("columns", [])
if columns:
	print("\nTop 5 residues by LDDT score:")
	for column in columns[:5]:
		print(
			f"{column['index']:>4} {column['residue']:>3} "
			f"preserved={column['nr_preserved']:>3} "
			f"considered={column['nr_considered']:>3} "
			f"score={column['score']:.4f}"
		)
