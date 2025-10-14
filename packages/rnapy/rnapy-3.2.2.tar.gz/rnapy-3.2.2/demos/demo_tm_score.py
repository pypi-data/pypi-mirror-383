from pathlib import Path

from rnapy.toolkit import RNAToolkit


# Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# Prepare demo inputs
demo_dir = Path(__file__).resolve().parent
reference_structure = demo_dir / "input" / "2zh6_B.pdb"
predicted_structure = demo_dir / "input" / "R1107.pdb"

print("RNAToolkit TM-score Demo")
print(f"Reference structure: {reference_structure}")
print(f"Predicted structure: {predicted_structure}")
print("-" * 50)

# Run TM-score calculation with default parameters
result = toolkit.calculate_tm_score(
    structure_1=str(reference_structure),
    structure_2=str(predicted_structure),
    mol="rna"  # Focus on RNA molecules
)

print("TM-score Results:")
# print original output for reference
# print("\nRaw TM-score output:")
print(result["raw_output"])
print(f"TM-score (normalized by length 1): {result['tm_score_1']:.4f}")
print(f"TM-score (normalized by length 2): {result['tm_score_2']:.4f}")

# Example with different molecule types
print("\n" + "-" * 50)
print("Comparison with different molecule selections:")
