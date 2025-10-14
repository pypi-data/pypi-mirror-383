import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


def get_tm_score_binary(use_multithreading: bool = False) -> str:
    """Get appropriate TM-score binary for current platform.
    
    Args:
        use_multithreading: Whether to use multi-threading version (TMscoreCmt-linux-x86)
    
    Returns:
        Path to TM-score binary
        
    Raises:
        RuntimeError: If no compatible binary is found
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    bin_dir = Path(__file__).parent / "bin"
    
    # Determine binary name based on system and architecture
    if system == "linux":
        if machine in ["x86_64", "amd64"]:
            base_name = "TMscoreCmt-linux-x86" if use_multithreading else "TMscoreC-linux-x86"
        elif machine in ["aarch64", "arm64"]:
            base_name = "TMscoreCmt-linux-x86" if use_multithreading else "TMscoreC-linux-x86"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}")
    elif system == "windows":
        if machine in ["x86", "i386", "i686", "x86_64", "amd64"]:
            base_name = "TMscoreCmt-win-x86.exe" if use_multithreading else "TMscoreC-win-x86.exe"
        else:
            raise RuntimeError(f"Unsupported Windows architecture: {machine}")
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")
    
    binary_path = bin_dir / base_name
    if not binary_path.exists():
        raise RuntimeError(f"TM-score binary not found: {binary_path}")
    
    # Make binary executable on Unix systems
    if system != "windows":
        os.chmod(binary_path, 0o755)
    
    return str(binary_path)


def parse_tm_score_output(output: str) -> Dict[str, Any]:
    """Parse TM-score output (classic and complex formats) to extract key metrics.

    Args:
        output: Raw TM-score output string.

    Returns:
        Dictionary containing parsed TM-score metrics and auxiliary information.
    """

    result: Dict[str, Any] = {
        "tm_score_1": None,
        "tm_score_2": None,
        "rmsd": None,
        "length_1": None,
        "length_2": None,
        "aligned_length": None,
        "sequence_identity": None,
        "raw_output": output,
        "tm_score_pairs": [],
        "rtm_scores": {},
        "final_tm_score": None,
        "final_rtm_score": None,
        "final_itm_score": None,
        "elapsed_time": None,
    }

    lines = output.splitlines()
    current_structure: Optional[int] = None

    def _safe_float(value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned or cleaned.lower() in {"n/a", "na", "nan"}:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _update_length(length_value: Optional[int], structure_hint: Optional[int] = None) -> None:
        if length_value is None:
            return
        if structure_hint in (1, 2):
            result[f"length_{structure_hint}"] = length_value
            return
        for key in ("length_1", "length_2"):
            if result[key] is None:
                result[key] = length_value
                return

    def _update_tm_scores(score: Optional[float]) -> None:
        if score is None:
            return
        if result["tm_score_1"] is None:
            result["tm_score_1"] = score
        elif result["tm_score_2"] is None:
            result["tm_score_2"] = score

    in_final_metrics_section = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        lower_line = line.lower()

        # Track whether we are in the final metrics section of the report
        if lower_line.startswith("final metrics"):
            in_final_metrics_section = True
            continue

        structure_match = re.match(r"information of structure\s+(\d+)", lower_line)
        if structure_match:
            current_structure = int(structure_match.group(1))
            continue

        if current_structure in (1, 2):
            length_match = re.search(r"nucle?tide number:\s*(\d+)", line, re.IGNORECASE)
            if length_match:
                _update_length(int(length_match.group(1)), current_structure)

        # Handle TM-score pairs between mapped molecules
        if "tm-score" in lower_line and "between" in lower_line:
            pair_match = re.search(r"tm-score[^:]*:\s*([0-9.+\-Ee]+)", line, re.IGNORECASE)
            if pair_match:
                score = _safe_float(pair_match.group(1))
                if score is not None:
                    result["tm_score_pairs"].append(score)
                    _update_tm_scores(score)
            continue

        # Handle detailed rTM-score lines such as "rTM-score(1): 0.098052"
        rtm_match = re.search(r"rTM-score\(([^)]+)\):\s*([0-9.+\-Ee]+|n/?a)", line, re.IGNORECASE)
        if rtm_match:
            key = rtm_match.group(1).strip()
            score = _safe_float(rtm_match.group(2))
            result["rtm_scores"][key] = score
            continue

        # Handle the summary TM-score / rTM-score / iTM-score line
        candidate_line = line.lstrip("> ")
        candidate_lower = candidate_line.lower()
        if "tm-score:" in candidate_lower and "between" not in candidate_lower:
            tm_match = re.search(r"tm-score:\s*([0-9.+\-Ee]+|n/?a)", candidate_line, re.IGNORECASE)
            if tm_match:
                final_tm = _safe_float(tm_match.group(1))
                result["final_tm_score"] = final_tm
                _update_tm_scores(final_tm)

            rtm_summary_match = re.search(r"rtm-score:\s*([0-9.+\-Ee]+|n/?a)", candidate_line, re.IGNORECASE)
            if rtm_summary_match:
                result["final_rtm_score"] = _safe_float(rtm_summary_match.group(1))

            itm_match = re.search(r"itm-score:\s*([0-9.+\-Ee]+|n/?a)", candidate_line, re.IGNORECASE)
            if itm_match:
                result["final_itm_score"] = _safe_float(itm_match.group(1))

            if in_final_metrics_section:
                in_final_metrics_section = False
            continue

        # Extract TM-scores and residue lengths from legacy output format
        if "tm-score=" in line:
            for match in re.finditer(r"TM-score=\s*([0-9.+\-Ee]+)", line):
                _update_tm_scores(_safe_float(match.group(1)))

        if "length=" in line:
            for match in re.finditer(r"Length=\s*(\d+)", line):
                _update_length(int(match.group(1)))

        if "rmsd of the common residues=" in lower_line:
            rmsd_match = re.search(r"rmsd of the common residues=\s*([0-9.+\-Ee]+)", line, re.IGNORECASE)
            if rmsd_match:
                result["rmsd"] = _safe_float(rmsd_match.group(1))

        if "number of residues in common=" in lower_line:
            aligned_match = re.search(r"number of residues in common=\s*(\d+)", line, re.IGNORECASE)
            if aligned_match:
                result["aligned_length"] = int(aligned_match.group(1))

        if "sequence identity=" in lower_line:
            seq_id_match = re.search(r"sequence identity=\s*([0-9.+\-Ee]+)", line, re.IGNORECASE)
            if seq_id_match:
                result["sequence_identity"] = _safe_float(seq_id_match.group(1))

        if lower_line.startswith("taking ") and "seconds" in lower_line:
            elapsed_match = re.search(r"taking\s+([0-9.+\-Ee]+)\s+seconds", line, re.IGNORECASE)
            if elapsed_match:
                result["elapsed_time"] = _safe_float(elapsed_match.group(1))

    return result


def calculate_tm_score(
    structure_1: str,
    structure_2: str,
    mol: str = "all",
    score_type: str = "t",
    use_multithreading: bool = False,
    ncpu: Optional[int] = None,
    d0: Optional[float] = None,
    da: str = "n",
    ia: Optional[str] = None,
    ri: str = "n",
    sid: float = 0.7,
    wt: str = "n",
    odis: str = "n",
    mode: str = "normal",
    atom_nuc: str = " C3'",
    atom_res: str = " CA ",
    nit: int = 20,
    nLinit: int = 6,
    clig: str = "y",
    output_aligned: Optional[str] = None,
    save_rotation_matrix: Optional[str] = None,
    save_superposition: Optional[str] = None
) -> Dict[str, Any]:
    """Calculate TM-score between two structures.
    
    Args:
        structure_1: Path to first structure (reference)
        structure_2: Path to second structure (prediction)
        mol: Molecule types to superimpose (all, prt, dna, rna, lig, etc.)
        score_type: Use TM-score ('t') or rTM-score ('r')
        use_multithreading: Use multi-threading version
        ncpu: Number of CPU threads
        d0: Custom d0 value for TM-score scaling
        da: Use molecule order from files ('y') or auto-generate ('n')
        ia: Path to molecule mapping file
        ri: Use matched residue/nucleotide indexes ('y' or 'n')
        sid: Global sequence identity cutoff (0-1)
        wt: Load water molecules ('y' or 'n')
        odis: Output distance details ('y' or 'n')
        mode: Computation mode ('fast' or 'normal')
        atom_nuc: Atom name for nucleotides (default " C3'")
        atom_res: Atom name for residues (default " CA ")
        nit: Maximum iteration number
        nLinit: Maximum L_init number
        clig: Re-map ligand atoms ('y' or 'n')
        output_aligned: Path to save aligned structure
        save_rotation_matrix: Path to save rotation matrix
        save_superposition: Path to save superposition info
        
    Returns:
        Dictionary containing TM-score results
        
    Raises:
        FileNotFoundError: If structure files don't exist
        RuntimeError: If TM-score calculation fails
    """
    # Validate input files
    if not Path(structure_1).exists():
        raise FileNotFoundError(f"Structure file not found: {structure_1}")
    if not Path(structure_2).exists():
        raise FileNotFoundError(f"Structure file not found: {structure_2}")
    
    # Get appropriate binary
    binary_path = get_tm_score_binary(use_multithreading)
    
    # Build command
    cmd = [binary_path, structure_1, structure_2]
    
    # Add options
    if mol != "all":
        cmd.extend(["-mol", mol])
    if score_type != "t":
        cmd.extend(["-s", score_type])
    if use_multithreading and ncpu:
        cmd.extend(["-ncpu", str(ncpu)])
    if d0:
        cmd.extend(["-d0", str(d0)])
    if da != "n":
        cmd.extend(["-da", da])
    if ia:
        cmd.extend(["-ia", ia])
    if ri != "n":
        cmd.extend(["-ri", ri])
    if sid != 0.7:
        cmd.extend(["-sid", str(sid)])
    if wt != "n":
        cmd.extend(["-wt", wt])
    if odis != "n":
        cmd.extend(["-odis", odis])
    if mode != "normal":
        cmd.extend(["-mode", mode])
    if atom_nuc != " C3'":
        cmd.extend(["-atom-nuc", atom_nuc])
    if atom_res != " CA ":
        cmd.extend(["-atom-res", atom_res])
    if nit != 20:
        cmd.extend(["-nit", str(nit)])
    if nLinit != 6:
        cmd.extend(["-nLinit", str(nLinit)])
    if clig != "y":
        cmd.extend(["-clig", clig])
    if output_aligned:
        cmd.extend(["-o", output_aligned])
    if save_rotation_matrix:
        cmd.extend(["-srm", save_rotation_matrix])
    if save_superposition:
        cmd.extend(["-ssp", save_superposition])
    
    try:
        # Execute TM-score
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout
        )
        
        # Parse output
        parsed_result = parse_tm_score_output(result.stdout)
        
        # Add command info
        parsed_result["command"] = " ".join(cmd)
        parsed_result["success"] = True
        
        return parsed_result
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"TM-score calculation failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("TM-score calculation timed out")
    except Exception as e:
        raise RuntimeError(f"TM-score calculation error: {str(e)}")


def convert_cif_to_pdb(cif_file: str, pdb_file: str, use_multithreading: bool = False) -> bool:
    """Convert CIF file to PDB format using TM-score tool.
    
    Args:
        cif_file: Input CIF file path
        pdb_file: Output PDB file path
        use_multithreading: Use multi-threading version
        
    Returns:
        True if conversion successful
        
    Raises:
        FileNotFoundError: If CIF file doesn't exist
        RuntimeError: If conversion fails
    """
    if not Path(cif_file).exists():
        raise FileNotFoundError(f"CIF file not found: {cif_file}")
    
    # Get appropriate binary
    binary_path = get_tm_score_binary(use_multithreading)
    
    # Build command for CIF to PDB conversion
    cmd = [binary_path, "-cif2pdb", cif_file, pdb_file]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        
        return Path(pdb_file).exists()
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"CIF to PDB conversion failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("CIF to PDB conversion timed out")
    except Exception as e:
        raise RuntimeError(f"CIF to PDB conversion error: {str(e)}") 