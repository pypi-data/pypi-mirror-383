from rnapy import RNAToolkit

# 1. Prepare input data
structure_file = "./input/R1107.pdb"

# 2. Initialize toolkit
toolkit = RNAToolkit(device="cpu")

# 3. Load RiboDiffusion model
model_path = "./models/exp_inf.pth"
# toolkit.load_model("ribodiffusion", model_path)
toolkit.load_model("ribodiffusion")

# 4. From 3D structure, generate RNA sequences
print("Generating RNA sequences from 3D structure...")
result = toolkit.generate_sequences_from_structure(
    structure_file=structure_file,
    model="ribodiffusion",
    n_samples=2,
    sampling_steps=100,  # sampling steps
    cond_scale=0.5,  # conditioning scale
    dynamic_threshold=True,  # use dynamic thresholding
    save_dir=str("./results/ribodiffusion"),
)

# 5. Display results
print("Generated Sequences:")
print(f"Sequence count: {result.get('sequence_count', 0)}")
if result.get("generated_sequences"):
    seq0 = result["generated_sequences"][0]
    print(f"First sequence: {seq0[:60]}{'...' if len(seq0) > 60 else ''}")
    print(f"Length: {len(seq0)}")
print(f"PDB ID: {result.get('pdb_id', 'N/A')}")
print(f"Output directory: {result.get('output_directory', 'N/A')}")

qm = result.get("quality_metrics", {})
if qm:
    avg_rec = qm.get("average_recovery_rate")
    if avg_rec is not None:
        print(f"Average recovery rate: {avg_rec:.4f}")

print(f"Full Result: {result}")
print("Results saved to ./results/ribodiffusion/")
print("Demo completed.")
