from rnapy import RNAToolkit

# 1. Initialize toolkit
toolkit = RNAToolkit()

# 2. Structure F1 Score Calculation
print("=" * 50)
print("Structure F1 Score Calculation")
print("=" * 50)

structure1 = "(((...)))"
structure2 = "(((.....)))"

print(f"Structure 1: {structure1}")
print(f"Structure 2: {structure2}")

f1_result = toolkit.calculate_structure_f1(structure1, structure2)

print(f"\nPrecision: {f1_result['precision']:.4f}")
print(f"Recall:    {f1_result['recall']:.4f}")
print(f"F1 Score:  {f1_result['f1_score']:.4f}")

# 3. Sequence Recovery Rate Calculation
print("\n" + "=" * 50)
print("Sequence Recovery Rate Calculation")
print("=" * 50)

native_seq = "AUGCUAGCUAGC"
designed_seq = "AUGCUAGCUUGC"

print(f"Native sequence:   {native_seq}")
print(f"Designed sequence: {designed_seq}")

recovery_result = toolkit.calculate_sequence_recovery(native_seq, designed_seq)

print(f"\nOverall Recovery: {recovery_result['overall_recovery']:.4f}")
print(f"Total Matches: {recovery_result['total_matches']}/{recovery_result['total_positions']}")
print("\nPer-Nucleotide Recovery:")
for base in ['A', 'U', 'G', 'C']:
    rate = recovery_result['per_nucleotide_recovery'][base]
    count = recovery_result['nucleotide_counts'][base]
    print(f"  {base}: {rate:.4f} ({count} positions)")
