from rnapy import RNAToolkit

# Initialize RNAToolkit
toolkit = RNAToolkit()
sequences = [
    "AUGGCUACCGAACUGGGAUUCGCCAAAGCUUAA",
    "AUGGGACCUACUGGUGAACCGUGCAAGGCUUGA"
]

# Calculate similarity between sequences
similarity_result = toolkit.compare_sequences(sequences[0], sequences[1])
print("Sequence Similarity Results:")
print(f"Sequence 1: {sequences[0]}")
print(f"Sequence 2: {sequences[1]}")
print(f"Similarity Score: {similarity_result['sequence_similarity']:.4f}")

# dot-bracket structures
structures = [
    "(((..(((...)))..)))",
    "(((..((....))..)))"
]
# Calculate similarity between structures
structure_similarity_result = toolkit.compare_structures(structures[0], structures[1])
print("\nStructure Similarity Results:")
print(f"Structure 1: {structures[0]}")
print(f"Structure 2: {structures[1]}")
print(f"Similarity Score: {structure_similarity_result['structure_similarity']:.4f}")