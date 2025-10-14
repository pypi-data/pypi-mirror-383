# RNAToolkit Usage Guide

This guide explains how to use RNAToolkit with the three included demos: RNA‑FM/mRNA‑FM (2D + embeddings), RhoFold (3D), and RiboDiffusion (inverse folding). It covers installation, model loading, quickstart examples, outputs, and troubleshooting.


## Overview
- Entry point: `from rnapy import RNAToolkit`
- Devices: CPU or CUDA (`device="cpu" | "cuda"`)
- Models and aliases:
  - RNA‑FM: "rna-fm", "rna_fm"
  - mRNA‑FM: "mrna-fm", "mrna_fm"
  - RhoFold (3D): "rhofold", "rho-fold", "rhofold+"
  - RiboDiffusion (inverse folding): "ribodiffusion", "ribo-diffusion"
- Typical tasks:
  - 2D structure prediction (dot‑bracket + contact map)
  - 3D structure prediction (PDB)
  - Embedding extraction (raw/mean/BOS)
  - Inverse folding (generate sequences from PDB)


## Install and setup
- Python 3.10+ recommended; install requirements: <br>
```bash
pip install -r requirements.txt
```
- Optional GPU: ensure your PyTorch build matches CUDA; then use `device="cuda"`
- Place checkpoints under `./models/` (as used in demos):
  - RNA‑FM: `./models/RNA-FM_pretrained.pth`
  - mRNA‑FM: `./models/mRNA-FM_pretrained.pth`
  - RhoFold: `./models/RhoFold_pretrained.pt`
  - RiboDiffusion: `./models/exp_inf.pth` (or `exp_inf_large.pth`)

Minimal init:
```
toolkit = RNAToolkit(device="cpu")
toolkit.load_model("mrna-fm", "./models/mRNA-FM_pretrained.pth")
```


## Quickstart

### A) 2D structure + embeddings (RNA‑FM / mRNA‑FM)
Inputs
- `sequences`: string, list of strings, or FASTA path
- `threshold`: contact cutoff (default 0.5)
- `save_dir`: CT/embedding output path or dir

Calls
- 2D structure: `predict_structure(sequences, structure_type="2d", model="mrna-fm", threshold=0.5, save_dir=...)`
- Secondary structure only: `predict_secondary_structure(...)`
- Save CT files: `save_ct_files(...)`
- Contacts: `predict_contacts(...)`
- Embeddings: `extract_embeddings(sequences, model="mrna-fm", layer=12, format="raw"|"mean"|"bos", save_dir=...)`

Returns (per sequence)
- `secondary_structure` (dot‑bracket)
- `contacts` (L×L NumPy array)
- `embeddings` (shape: L×D for raw; D for mean/BOS when requested)
- `sequence`, `sequence_id`, `threshold`, `model_used`

Notes
- Valid nucleotides: A/U/C/G
- FASTA inputs are auto‑parsed with IDs


### B) 3D structure prediction (RhoFold)
Inputs
- `sequences`: string/list/FASTA
- `save_dir`: output dir for PDB/CT/NPZ
- `relax_steps`: Amber relaxation iterations (0 to skip)

Calls
- Load: `toolkit.load_model("rhofold", "./models/RhoFold_pretrained.pt")`
- Predict: `predict_structure(sequences, structure_type="3d", model="rhofold", save_dir=..., relax_steps=100)`

Returns (per sequence)
- `structure_3d_unrelaxed` (PDB path)
- `structure_3d_refined` (PDB path, if relaxation enabled)
- `secondary_structure` (parsed from CT when available)
- `confidence_scores` (per residue), `average_confidence`
- `distogram_file` (NPZ), `output_directory`, `sequence`, `sequence_id`
- `validation` warnings/errors

Notes
- If MSA databases/binaries aren’t configured, single‑sequence mode is used
- Multiple inputs return an aggregated object with `results` and optional `additional_structures`


### C) Inverse folding (RiboDiffusion)
Inputs
- `structure_file`: PDB filepath
- Optional knobs via kwargs: `n_samples`, `sampling_steps`, `cond_scale`, `dynamic_threshold`, `dynamic_thresholding_percentile`
- `save_dir`: base output dir; FASTA saved under `fasta/`

Calls
- Load: `toolkit.load_model("ribodiffusion", "./models/exp_inf.pth")`
- Generate: `generate_sequences_from_structure(structure_file, model="ribodiffusion", n_samples=2, sampling_steps=100, cond_scale=0.5, dynamic_threshold=True, save_dir=...)`

Returns
- `generated_sequences`, `sequence_count`, `pdb_id`, `pdb_file`
- `output_directory`, `fasta_directory`, `fasta_files`
- `quality_metrics` (e.g., `recovery_rates`, `average_recovery_rate`)
- `sequence_statistics`, `composition_analysis`, `validation`

Batch
- `batch_generate_sequences_from_structures([... or dir], model="ribodiffusion", n_samples=..., output_base_dir=...)`


## Unified analysis helpers
- `analyze_sequence(sequences, analysis_type="full"|"embedding"|"structure"|"properties", model="rna-fm")`
- `compare_sequences(seq1, seq2, model="rna-fm", comparison_type="full"|"embedding"|"structure", embedding_format="raw"|"mean"|"bos")`
- `batch_analyze(sequences, analysis_type, model)`


## Model management
- `list_available_models()` / `list_loaded_models()`
- `load_model(name, checkpoint_path, **kwargs)`
- `get_model_info(name=None)`
- `unload_model(name)`
- `set_device("cpu"|"cuda")`


## Outputs and layout
- RNA‑FM/mRNA‑FM: CT files in `save_dir`; contacts/embeddings in memory or saved `.npy`
- RhoFold: PDB (`*-unrelaxed_model.pdb`, `*-relaxed_<steps>_model.pdb`), CT (`*-ss.ct`), NPZ (`*-results.npz`)
- RiboDiffusion: FASTA under `<save_dir>/fasta/` plus JSON‑like metrics


## Troubleshooting
- "Model X is not loaded": call `load_model(...)` first
- Checkpoint not found: ensure model files exist at paths above
- Invalid sequence: only A/U/C/G are allowed
- RiboDiffusion weights: manual download required
- RhoFold MSA: without DB/binaries, it uses single‑sequence fallback


## Demo parity
- RNA‑FM / mRNA‑FM: `demos/demo_rna_fm.py` (2D + embeddings, outputs under `./results/rna_fm/`)
- RhoFold: `demos/demo_rhofold.py` (3D; PDB/CT/NPZ under `./results/rhofold/`)
- RiboDiffusion: `demos/demo_ribodiffusion.py` (inverse folding; FASTA under `./results/ribodiffusion/fasta/`)


## API quick reference
- `predict_structure(sequences, structure_type="2d"|"3d", model=..., threshold=0.5, save_dir=..., **kwargs)`
- `predict_secondary_structure(sequences, threshold=0.5, model="rna-fm", advanced_postprocess=True, allow_noncanonical=True)`
- `predict_contacts(sequences, model="rna-fm", threshold=0.5, return_processed=True, allow_noncanonical=True)`
- `save_ct_files(sequences, output_dir, sequence_ids=None, model="rna-fm", threshold=0.5, advanced_postprocess=True, allow_noncanonical=True)`
- `extract_embeddings(sequences, model="rna-fm", layer=12, format="raw"|"mean"|"bos", save_dir=None)`
- `generate_sequences_from_structure(structure_file, model="ribodiffusion", n_samples=1, save_dir=None, **kwargs)`
- `batch_generate_sequences_from_structures(structure_files, model="ribodiffusion", n_samples=1, output_base_dir=None, **kwargs)`
- `analyze_sequence(...)`, `compare_sequences(...)`, `batch_analyze(...)`

