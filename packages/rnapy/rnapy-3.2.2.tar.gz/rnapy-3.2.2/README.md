# RNAPy — Unified RNA Analysis Toolkit

RNAPy is a unified Python toolkit that wraps several powerful RNA models with a consistent, easy-to-use API. It currently integrates:

- RNA-FM for sequence embeddings and 2D secondary structure prediction
- RhoFold for 3D structure prediction
- RiboDiffusion for inverse folding (sequence generation from structure)
- RhoDesign for inverse folding (structure-to-sequence, optional 2D guidance)
- RNA-MSM for MSA-based embeddings, attention, consensus, and conservation


## Key Features

- Consistent high-level API via `RNAToolkit`
- Extract sequence embeddings (RNA-FM, mRNA-FM)
- 2D structure prediction (RNA-FM)
- 3D structure prediction (RhoFold)
- Inverse folding (RiboDiffusion, RhoDesign)
- MSA analysis and features (RNA-MSM: embeddings, attention, consensus, conservation)


## Project Structure

```
RNAPy
├── rnapy/                    # Library source
│   ├── core/                 # Base classes, factory, config, exceptions
│   ├── providers/            # Model providers (rna_fm/mrna_fm, rhofold, RiboDiffusion, rhodesign, rna_msm)
│   ├── interfaces/           # Public interfaces
│   └── utils/                # Utilities
├── configs/                  # Global and model configs (YAML)
├── demos/                    # Ready-to-run examples
│   ├── models/               # Put pretrained weights here
│   ├── results/              # Default output location for demos
│   └── demo_*.py             # Demo scripts
├── requirements.txt
├── setup.py
└── README.md
```


## Installation

Recommended: Python 3.12+ and a recent PyTorch build compatible with your CPU/GPU.

```
pip install rnapy --extra-index-url  https://download.pytorch.org/whl/cpu 
```


## Documentation

- Toolkit usage guide: `docs/RNAToolkit_Usage_Guide.md`


## Model Weights

- You can download pretrained weights from the original repositories which will be mentioned in the Acknowledgements section.
- Or you can find weights used in RNAPy on Hugging Face:
https://huggingface.co/Linorman616/rnapy_models/
- Actually if you don't provide `model-path` when loading a model, RNAPy will try to download the weights from this repo automatically.


## Quick Start

### 1) RNA-FM (2D structure + embeddings)

```python
from rnapy import RNAToolkit

sequence = "AGAUAGUCGUGGGUUCCCUUUCUGGAGGGAGAGGGAAUUCCACGUUGACCGGGGGAACCGGCCAGGCCCGGAAGGGAGCAACCGUGCCCGGCUAUC"

# Initialize
toolkit = RNAToolkit(device="cpu")

# Load model (choose one)
toolkit.load_model("rna-fm", "./models/RNA-FM_pretrained.pth")

# 2D structure prediction
result = toolkit.predict_structure(
    sequence,
    structure_type="2d",
    model="rna-fm",
    save_dir="./results/rna_fm/demo.ct",
)

# Embeddings
embeddings = toolkit.extract_embeddings(
    sequence,
    model="rna-fm",
    save_dir="./results/rna_fm/embeddings.npy",
)

print(result.get("secondary_structure"))
print(result.get("confidence_scores"))
```

### 2) RhoFold (3D structure prediction)

```python
from rnapy import RNAToolkit

sequence = "GGAUCCCGCGCCCCUUUCUCCCCGGUGAUCCCGCGAGCCCCGGUAAGGCCGGGUCC"

toolkit = RNAToolkit(device="cpu")

# Load RhoFold
toolkit.load_model("rhofold", "./models/RhoFold_pretrained.pt")

# Predict 3D
result = toolkit.predict_structure(
    sequence,
    structure_type="3d",
    model="rhofold",
    save_dir="./results/rhofold",
    relax_steps=500,
)

pdb_file = result.get("structure_3d_refined", result.get("structure_3d_unrelaxed"))
print("3D structure:", pdb_file)
```

### 3) RiboDiffusion (inverse folding from PDB)

```python
from rnapy import RNAToolkit

structure_file = "./input/R1107.pdb"

toolkit = RNAToolkit(device="cpu")

# Load RiboDiffusion
toolkit.load_model("ribodiffusion", "./models/exp_inf.pth")

# Generate sequences from structure
result = toolkit.generate_sequences_from_structure(
    structure_file=structure_file,
    model="ribodiffusion",
    n_samples=2,
    sampling_steps=100,
    cond_scale=0.5,
    dynamic_threshold=True,
    save_dir="./results/ribodiffusion",
)

print("Generated count:", result.get("sequence_count", 0))
print("Output dir:", result.get("output_directory"))
```

### 4) RhoDesign (inverse folding with optional 2D guidance)

```python
from rnapy import RNAToolkit

pdb_path = "./input/2zh6_B.pdb"
ss_path = "./input/2zh6_B.npy"  # optional numpy file with secondary-structure/contact info

toolkit = RNAToolkit(device="cpu")

# Load RhoDesign (with-2D variant checkpoint)
toolkit.load_model("rhodesign", "./models/ss_apexp_best.pth")

# Generate one sequence from structure (RhoDesign samples one sequence per call)
res = toolkit.generate_sequences_from_structure(
    structure_file=pdb_path,
    model="rhodesign",
    secondary_structure_file=ss_path,  # omit or set None to run without 2D guidance
    save_dir="./results/rhodesign"
)

print("Predicted sequence:", res["sequences"][0])
print("Recovery rate:", res.get("quality_metrics", {}).get("sequence_recovery_rate"))
print("FASTA:", res.get("files", {}).get("fasta_files", [None])[0])
```

### 5) RNA-MSM (MSA features, consensus, conservation)

```python
from rnapy import RNAToolkit

# Initialize
toolkit = RNAToolkit(device="cpu")

# Load RNA-MSM
toolkit.load_model("rna-msm", "./models/RNA_MSM_pretrained_weights.pt")

# Prepare an example MSA (aligned sequences)
msa_sequences = [
    "AUGGCGAUUUUAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCAAUUUUAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCGAUUUCAUUUACCGCAGUCGUUACCAACAUACUCGACUUUAAAUGCC",
    "AUGGCGAUUUUAUUUACCGCAGUCGUUACCAGCAUACUCGACUUUAAAUGCC",
]

# Extract embeddings (per-position, last layer by default)
features = toolkit.extract_msa_features(
    msa_sequences,
    feature_type="embeddings",
    model="rna-msm",
    save_dir="./results/rna_msm",
)

# Analyze MSA for consensus and conservation
msa_result = toolkit.analyze_msa(
    msa_sequences,
    model="rna-msm",
    extract_consensus=True,
    extract_conservation=True,
    save_dir="./results/rna_msm",
)

print("Consensus:", msa_result.get("consensus_sequence"))
print("Conservation (first 10):", (msa_result.get("conservation_scores") or [])[:10])
```


## Evaluation Metrics

RNAPy ships with common structural evaluation metrics, available via both the Python API and the CLI.

### LDDT (Local Distance Difference Test)

- Python:

```python
from rnapy.toolkit import RNAToolkit

toolkit = RNAToolkit(device="cpu")
res = toolkit.calculate_lddt(
    reference_structure="./demos/input/2zh6_B.pdb",
    predicted_structure="./demos/input/R1107.pdb",
    radius=15.0,
    distance_thresholds=(0.5, 1.0, 2.0, 4.0),
    return_column_scores=True,
)
print(res["lddt"])            # Global LDDT
print(res.get("columns", [])[:5])  # Optional: first 5 per-residue column scores
```

- CLI:

```bash
rnapy metric lddt \
  --reference ./demos/input/2zh6_B.pdb \
  --predicted ./demos/input/R1107.pdb \
  --radius 15.0 \
  --thresholds 0.5,1.0,2.0,4.0 \
  --return-column-scores
```

Example script: `demos/demo_lddt.py`

### RMSD (Root Mean Square Deviation)

- Python:

```python
from rnapy.toolkit import RNAToolkit

toolkit = RNAToolkit()
rmsd = toolkit.calculate_rmsd(
    "./demos/input/rmsd_tests/resources/ci2_1.pdb",
    "./demos/input/rmsd_tests/resources/ci2_2.pdb",
    file_format="pdb",
)
print("RMSD:", rmsd)
```

- CLI (common flags only; see `rnapy metric rmsd --help` for details):

```bash
rnapy metric rmsd \
  --file1 ./demos/input/rmsd_tests/resources/ci2_1.pdb \
  --file2 ./demos/input/rmsd_tests/resources/ci2_2.pdb \
  --file-format pdb \
  --rotation kabsch
```

Other options include: `--reorder`, `--reorder-method inertia-hungarian`, `--use-reflections`, `--only-alpha-carbons`, `--ignore-hydrogen`, `--output-aligned-structure`, `--print-only-rmsd-atoms`, `--gzip-format`, etc.

Example script: `demos/demo_rmsd.py`

### TM-score

- Python:

```python
from rnapy.toolkit import RNAToolkit

toolkit = RNAToolkit(device="cpu")
result = toolkit.calculate_tm_score(
    structure_1="./demos/input/2zh6_B.pdb",
    structure_2="./demos/input/R1107.pdb",
    mol="rna",
)
print(result["raw_output"])     # Raw TM-score tool output
print(result["tm_score_1"])     # TM-score normalized by length 1
print(result["tm_score_2"])     # TM-score normalized by length 2
```

- CLI:

```bash
rnapy metric tm-score \
  --struct1 ./demos/input/2zh6_B.pdb \
  --struct2 ./demos/input/R1107.pdb \
  --mol rna
```

Example script: `demos/demo_tm_score.py`


## Sequence Recovery & Structure F1

Sequence recovery and secondary-structure F1 are common quality metrics for design and prediction.

- Python:

```python
from rnapy import RNAToolkit

toolkit = RNAToolkit()

# Structure F1 (dot-bracket)
f1 = toolkit.calculate_structure_f1("(((...)))", "(((.....)))")
print(f1)  # {precision, recall, f1_score}

# Sequence recovery rate
recovery = toolkit.calculate_sequence_recovery("AUGCUAGCUAGC", "AUGCUAGCUUGC")
print(recovery["overall_recovery"])  # overall recovery
```

- CLI:

```bash
# Structure F1
rnapy struct f1 \
  --struct1 "(((...)))" \
  --struct2 "(((.....)))"

# Sequence recovery
rnapy seq recovery \
  --native  AUGCUAGCUAGC \
  --designed AUGCUAGCUUGC
```

Example script: `demos/demo_f1_recovery.py`


## Command Line Interface (CLI)

The package installs a console script named `rnapy` (via setup entry point). After installation, you can run `rnapy` from your shell.

- Show top-level help:
  - `rnapy --help`
- Show help for a subcommand:
  - `rnapy seq embed --help`

### Global options

These options are shared by all subcommands:

- `--device {cpu,cuda}`: Computing device (default: `cpu`)
- `--model {rna-fm,mrna-fm,rhofold,ribodiffusion,rhodesign,rna-msm}`: Model provider (required)
- `--model-path PATH`: Path to the model checkpoint (required)
- `--config-dir PATH`: Configuration directory (default: `configs`)
- `--provider-config PATH`: Optional provider-specific config file
- `--seed INT`: Random seed
- `--save-dir DIR`: Output directory
- `--verbose` or `-v`: Verbose logs and full tracebacks on errors

Input conventions:

- Use exactly one of `--seq` or `--fasta`
  - `--seq` accepts a single RNA sequence or multiple sequences separated by commas
  - `--fasta` accepts a `.fasta/.fa/.fas` file path

### Subcommands

1) Sequence embeddings

Extract embeddings from RNA-FM/mRNA-FM:

```bash
rnapy seq embed \
  --model rna-fm \
  --model-path ./models/RNA-FM_pretrained.pth \
  --seq "AGAUAGUCGUGGGU...UCGGCUAUC" \
  --layer -1 \
  --format mean \
  --save-dir ./results/rna_fm
```

- `--layer`: which layer to use (default: `-1`, i.e., last layer)
- `--format {raw,mean,bos}`: output format (default: `mean`)
- You can also pass `--fasta path/to/input.fasta` instead of `--seq`

2) Structure prediction

Predict 2D RNA-FM or 3D (RhoFold) structure:

```bash
# 2D with mRNA-FM
rnapy struct predict \
  --model rna-fm \
  --model-path ./models/RNA-FM_pretrained.pth \
  --seq "AGAUAGUCGUGGGU...UCGGCUAUC" \
  --structure-type 2d \
  --save-dir ./results/rna_fm_struct

# 3D with RhoFold (structure-type will auto-infer to 3d)
rnapy struct predict \
  --model rhofold \
  --model-path ./models/RhoFold_pretrained.pt \
  --seq "GGAUCCCGCGCCC...GCCGGGUCC" \
  --save-dir ./results/rhofold_3d
```

- If `--structure-type` is omitted: `rhofold` -> `3d`; `rna-fm`/`mrna-fm` -> `2d`

3) Inverse folding (generate sequences from structure)

RiboDiffusion and RhoDesign take a PDB as input:

```bash
# RiboDiffusion: generate multiple sequences
rnapy invfold gen \
  --model ribodiffusion \
  --model-path ./models/exp_inf.pth \
  --pdb ./input/R1107.pdb \
  --n-samples 2 \
  --save-dir ./results/ribodiffusion

# RhoDesign: optional 2D guidance via NPY
rnapy invfold gen \
  --model rhodesign \
  --model-path ./models/ss_apexp_best.pth \
  --pdb ./input/2zh6_B.pdb \
  --ss-npy ./input/2zh6_B.npy \
  --save-dir ./results/rhodesign
```

- `--pdb`: required
- `--ss-npy`: optional; only used by RhoDesign (2D guidance)
- `--n-samples`: number of sequences to sample (RhoDesign samples one per call; RiboDiffusion supports many)

4) MSA features (RNA-MSM)

Extract embeddings/attention from an aligned MSA:

```bash
rnapy msa features \
  --model rna-msm \
  --model-path ./models/RNA_MSM_pretrained_weights.pt \
  --fasta ./input/example_msa.fasta \
  --feature-type embeddings \
  --layer -1 \
  --save-dir ./results/rna_msm_features
```

- `--feature-type {embeddings,attention,both}` (default: `embeddings`)
- `--layer`: which layer to extract (default: `-1`)

5) MSA analysis (RNA-MSM)

Compute consensus and/or conservation from an MSA:

```bash
rnapy msa analyze \
  --model rna-msm \
  --model-path ./models/RNA_MSM_pretrained_weights.pt \
  --fasta ./input/example_msa.fasta \
  --extract-consensus \
  --extract-conservation \
  --save-dir ./results/rna_msm_analyze
```

- If you pass a single `--seq` (not multiple), this subcommand will error because it requires multiple sequences or a FASTA file

6) Metrics (structure evaluation)

- LDDT: see examples above, or run `rnapy metric lddt --help`
- RMSD: see examples above, or run `rnapy metric rmsd --help`
- TM-score: see examples above, or run `rnapy metric tm-score --help`

7) Sequence utilities

- Structure F1: `rnapy struct f1 --struct1 ... --struct2 ...`
- Sequence recovery: `rnapy seq recovery --native ... --designed ...`

### Outputs and logging

- When `--save-dir` is provided, results are written under that directory. The exact filenames depend on the provider/task (e.g., `.npy` for embeddings, `.ct` for 2D, `.pdb`/folder for 3D, `.json` for analysis summaries). The CLI prints a brief summary and (when applicable) a path hint.
- Exit codes: `0` on success; non-zero on errors. Add `-v/--verbose` for full tracebacks.

### Common pitfalls

- Do not pass both `--seq` and `--fasta` at the same time.
- Ensure the `--model-path` points to the correct checkpoint for the chosen `--model`.
- `rhofold` defaults to 3D; RNA-FM/mRNA-FM default to 2D if `--structure-type` is omitted.
- `msa analyze` requires multiple sequences (comma-separated via `--seq`) or a FASTA file.


## Run the Demos

From the repository root:

```powershell
# mRNA-FM / RNA-FM demo
cd .\demos
python .\demo_rna_fm.py

# RhoFold demo
python .\demo_rhofold.py

# RiboDiffusion demo
python .\demo_ribodiffusion.py

# RhoDesign demo
python .\demo_rhodesign.py

# RNA-MSM demo
python .\demo_rna_msm.py

# LDDT demo
python .\demo_lddt.py

# RMSD demo
python .\demo_rmsd.py

# TM-score demo
python .\demo_tm_score.py

# Sequence recovery & Structure F1 demo
python .\demo_f1_recovery.py
```

Additional examples may be available: `rna_fm_demo.py`, `rhofold_demo.py`, `ribodiffusion_demo.py`.

## Datasets

You can download example datasets via API or CLI (e.g., Rfam, RNA Puzzles, CASP15, etc.).

- Available dataset names: `Rfam`, `Rfam_original`, `RNA_Puzzles`, `CASP15`, `RNAsolo2`

- CLI:

```bash
# List available datasets
rnapy dataset list

# Download Rfam (from the HF mirror) with parallel workers
rnapy dataset download --dataset Rfam --max-workers 8
```

- Python：

```python
from rnapy.toolkit import RNAToolkit

toolkit = RNAToolkit()
print(toolkit.list_available_datasets())
toolkit.download_dataset("Rfam", max_workers=8)
```

## Configuration

YAML configs are provided under `./configs/` and `./demos/configs/`. You can:

- Pass `config_dir` to `RNAToolkit` to use custom defaults
- Override per-call parameters in `load_model(...)` and task methods

## License

MIT License


## Acknowledgements

- RNA-FM: https://github.com/ml4bio/RNA-FM
- RhoFold: https://github.com/ml4bio/RhoFold
- RiboDiffusion: https://github.com/ml4bio/RiboDiffusion
- RhoDesign: https://github.com/ml4bio/RhoDesign
- RNA-MSM: https://github.com/yikunpku/RNA-MSM
