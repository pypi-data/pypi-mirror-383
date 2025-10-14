from rnapy import RNAToolkit

# 1. Prepare input data
sequences = [
    "AUGGCUACCGAACUGGGAUUCGCCAAAGCUUAA",
    "AUGGGACCUACUGGUGAACCGUGCAAGGCUUGA"
]

# 2. Initialize toolkit
# toolkit = RNAToolkit(device="cpu", config_dir="./configs")
toolkit = RNAToolkit(device="cpu")

# 3. Load model
model_path = "./models/RNA-FM_pretrained.pth"
# model_path = "./models/mRNA-FM_pretrained.pth"  # mRNA model
# toolkit.load_model("rna-fm", model_path)
# toolkit.load_model("mrna-fm", model_path)
toolkit.load_model("rna-fm")

# 4. Predict structure
print("Predicting structure...")
results = toolkit.predict_structure(sequences, structure_type="2d", model="rna-fm", save_dir="./results/rna_fm/")

# 5. Extract embeddings
embeddings = toolkit.extract_embeddings(sequences, model="rna-fm", save_dir="./results/rna_fm/")
# embeddings = toolkit.extract_embeddings(sequences, model="mrna-fm", save_dir="./results/rna_fm/")

# 6. Display results, if it's a list of sequences, show them all
print("Predicted Structures:")
for i, result in enumerate(results if isinstance(results, list) else [results]):
    print(f"Sequence {i+1}:")
    print(f"Predicted Structure: {result.get('secondary_structure', 'No structure predicted')}")
    print(f"Confidence Scores: {result.get('confidence_scores', 'No scores available')}")
    print(f"Full Result: {result}")
