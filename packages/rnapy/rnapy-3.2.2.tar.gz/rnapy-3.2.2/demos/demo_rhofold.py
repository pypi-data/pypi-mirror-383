from rnapy import RNAToolkit

# 1. Prepare input data
sequences = [
    "AUGGCUACCGAACUGGGAUUCGCCAAAGCUUAA",
    "AUGGGACCUACUGGUGAACCGUGCAAGGCUUGA"
]

# 2. Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# 3. Load model
model_path = "./models/RhoFold_pretrained.pt"
toolkit.load_model("rhofold", model_path)

# 4. Predict 3D structure
print("Predicting 3D structure...")
result = toolkit.predict_structure(sequences, structure_type="3d",
                                   model="rhofold",
                                   save_dir=str("./results/rhofold"),
                                   relax_steps=100
                                   )

# 5. Display results
print("Predicted 3D Structure:")
print(
    f"Structure file: {result.get('structure_3d_refined', result.get('structure_3d_unrelaxed', 'No structure file'))}")
print(f"Secondary structure: {result.get('secondary_structure', 'No secondary structure predicted')}")
print(f"Average confidence: {result.get('average_confidence', 'No confidence score available')}")
print(f"Full Result: {result}")
print("Results saved to ./results/rhofold/demo.pdb")
print("Demo completed.")
