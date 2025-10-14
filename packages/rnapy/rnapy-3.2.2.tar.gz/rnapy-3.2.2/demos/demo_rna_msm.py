from rnapy import RNAToolkit

# 1. Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# 2. Load RNA-MSM model
# toolkit.load_model("rna-msm", "models/RNA_MSM_pretrained_weights.pt")
toolkit.load_model("rna-msm")

# 3. Prepare MSA sequences
msa_sequences = [
    "AUGGCGAUUUUAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCAAUUUUAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCGAUUUCAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCGAUUUUAUUUACCGCAGUCGUUACCAGCAUACUCGACUUUAAAUGCC"
]

# 4. Extract embeddings for the first sequence in MSA
embeddings = toolkit.extract_msa_features(
    msa_sequences[0],
    feature_type="embeddings",
    model="rna-msm"
)

# 5. Analyze MSA to get consensus sequence and conservation scores
msa_result = toolkit.analyze_msa(
    msa_sequences,
    model="rna-msm",
    extract_consensus=True,
    extract_conservation=True,
    save_dir="./results/rna_msm"
)

# 6. Display results
print(f"Embeddings Shape: {embeddings.shape}")
print(f"Consensus Sequence: {msa_result.get('consensus_sequence', 'N/A')}")
print(f"Conservation Scores: {msa_result.get('conservation_scores', 'N/A')}")
print(f"Full MSA Result: {msa_result}")
print("Results saved to ./results/rna_msm/")
