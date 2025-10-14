from rnapy.toolkit import RNAToolkit

# Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# Load RhoDesign model
toolkit.load_model("rhodesign", "models/ss_apexp_best.pth")

# Generate sequence from structure
results = toolkit.generate_sequences_from_structure(
    structure_file="input/2zh6_B.pdb",
    secondary_structure_file="input/2zh6_B.npy",
    model="rhodesign",
    save_dir="./results/rhodesign"
)

print(f"Generated sequence: {results['sequences'][0]}")
print(f"Recovery rate: {results['quality_metrics']['sequence_recovery_rate']:.3f}")