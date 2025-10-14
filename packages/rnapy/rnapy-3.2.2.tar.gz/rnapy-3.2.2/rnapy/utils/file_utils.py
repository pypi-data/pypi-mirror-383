from typing import Any, List, Union, Tuple
import os
import pickle

import numpy as np

from rnapy.utils.data_utils import construct_data_single


def read_fasta_file(file_path: str) -> List[Tuple[str, str]]:
    """Read FASTA file and return sequence labels and strings
    
    Args:
        file_path: Path to FASTA file
        
    Returns:
        List of (label, sequence) tuples
    """
    sequences = []
    current_label = None
    current_seq = []
    
    with open(file_path, 'r') as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence
                if current_label is not None:
                    sequences.append((current_label, ''.join(current_seq)))
                
                # Start new sequence
                current_label = line[1:] if len(line) > 1 else f"seq_{line_idx}"
                current_seq = []
            else:
                current_seq.append(line.upper().replace('T', 'U'))
        
        # Save last sequence
        if current_label is not None:
            sequences.append((current_label, ''.join(current_seq)))
    
    return sequences

def process_sequence_input(input_data: Union[str, List[str]]) -> Tuple[List[str], List[str]]:
    """Process sequence input - either file path or direct sequences
    
    Args:
        input_data: FASTA file path or sequence string(s)
        
    Returns:
        Tuple of (sequence_ids, sequences)
    """
    if isinstance(input_data, str):
        # Check if it's a file path
        if os.path.isfile(input_data) and input_data.endswith(('.fasta', '.fa', '.fas')):
            fasta_data = read_fasta_file(input_data)
            sequence_ids = [label for label, _ in fasta_data]
            sequences = [seq for _, seq in fasta_data]
            return sequence_ids, sequences
        else:
            # Direct sequence string
            return ['seq_0'], [input_data]
    elif isinstance(input_data, list):
        # List of sequences
        return [f'seq_{i}' for i in range(len(input_data))], input_data
    else:
        raise ValueError("Input must be a string (sequence or file path) or list of sequences")

def save_ct_file(file_path: str, sequence: str, structure: Any) -> None:
    """Save CT file format for RNA secondary structure
    
    Args:
        file_path: Output file path
        sequence: RNA sequence
        structure: Secondary structure in dot-bracket notation
    """

    def _matrix_to_ct(contact_matrix: np.ndarray,
                      sequence: str) -> str:
        """Convert contact matrix to CT file format"""
        seq_len = len(sequence)
        structure = np.where(contact_matrix)

        # Create pairing dictionary
        pair_dict = {i: -1 for i in range(seq_len)}
        for i in range(len(structure[0])):
            pair_dict[structure[0][i]] = structure[1][i]

        # Prepare CT file columns
        first_col = list(range(1, seq_len + 1))  # 1-indexed position
        second_col = list(sequence)  # nucleotide
        third_col = list(range(seq_len))  # 0-indexed position
        fourth_col = list(range(2, seq_len + 2))  # next position (1-indexed)
        fifth_col = [pair_dict[i] + 1 if pair_dict[i] != -1 else 0 for i in
                     range(seq_len)]  # paired position (1-indexed, 0 for unpaired)
        last_col = list(range(1, seq_len + 1))  # position again

        ct_str = ""
        for i in range(seq_len):
            ct_str += f"{first_col[i]}\t{second_col[i]}\t{third_col[i]}\t{fourth_col[i]}\t{fifth_col[i]}\t{last_col[i]}\n"

        return ct_str

    ct_str = _matrix_to_ct(contact_matrix=structure, sequence=sequence)
    # mkdir if not exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(f"{len(sequence)}\n")
        f.write(ct_str)

def save_npy_file(data: Any, file_path: str) -> None:
    import numpy as np
    np.save(file_path, data)

def save_npz_file(data_dict: dict, file_path: str) -> None:
    import numpy as np
    np.savez(file_path, **data_dict)


NUM_TO_LETTER = np.array(['A', 'G', 'C', 'U'])

# read PDB files directly; modify from ESM
def parse_pdb_direct(pdb_path, temp_save_path=None, chain=None):
    if temp_save_path is not None:
        try:
            if os.path.exists(temp_save_path):
                with open(temp_save_path, 'rb') as f:
                    seq, xyz, mask = pickle.load(f)
                return seq, xyz, mask
        except:
            # pass
            print(f"Error in reading {temp_save_path}, re-generate it.")

    xyz, seq, doubles, min_resn, max_resn = {}, {}, {}, np.inf, -np.inf
    with open(pdb_path, "rb") as f:
        for line in f:
            line = line.decode("utf-8", "ignore").rstrip()

            if line[:6] == "HETATM" and line[17:17 + 3] == "MSE":
                line = line.replace("HETATM", "ATOM  ")
                line = line.replace("MSE", "MET")

            if line[:4] == "ATOM":
                ch = line[21:22]
                if ch == chain or chain is None:
                    atom = line[12:12 + 4].strip()
                    resi = line[17:17 + 3]
                    resi_extended = line[16:17 + 3].strip()
                    resn = line[22:22 + 5].strip()
                    x, y, z = [float(line[i:(i + 8)]) for i in [30, 38, 46]]

                    if resn[-1].isalpha():
                        resa, resn = resn[-1], int(resn[:-1]) - 1
                    else:
                        resa, resn = "", int(resn) - 1
                    if resn < min_resn: min_resn = resn
                    if resn > max_resn: max_resn = resn
                    if resn not in xyz: xyz[resn] = {}
                    if resa not in xyz[resn]: xyz[resn][resa] = {}
                    if resn not in seq: seq[resn] = {}
                    if resa not in seq[resn]:
                        seq[resn][resa] = resi
                    elif seq[resn][resa] != resi_extended:
                        # doubles mark locations in the pdb file where multi residue entries are
                        # present. There's a known bug in TmAlign binary that doesn't read / skip
                        # these entries, so we mark them to create a sequence that is aligned with
                        # gap tokens in such locations.
                        doubles[resn] = True

                    if atom not in xyz[resn][resa]:
                        xyz[resn][resa][atom] = np.array([x, y, z])

    # convert to numpy arrays, fill in missing values
    seq_, xyz_, mask = [], [], []
    for resn in range(min_resn, max_resn + 1):
        ## residue name as seq
        if resn in seq:
            for k in sorted(seq[resn]):
                # seq_.append(aa_3_N.get(seq[resn][k], 20))
                seq_.append(seq[resn][k].strip())
        else:
            # seq_.append(20)
            continue
        ## xyz coordinates [L, 3, 3]
        coords_tmp = np.zeros((3, 3))
        if resn in xyz:
            for k in sorted(xyz[resn]):
                res_name = seq[resn][k].strip()
                if "C4'" in xyz[resn][k]: coords_tmp[0] = xyz[resn][k]["C4'"]
                if "C1'" in xyz[resn][k]: coords_tmp[1] = xyz[resn][k]["C1'"]
                if res_name in ['A', 'G'] and "N9" in xyz[resn][k]: coords_tmp[2] = xyz[resn][k]["N9"]
                if res_name in ['C', 'U'] and "N1" in xyz[resn][k]: coords_tmp[2] = xyz[resn][k]["N1"]
        xyz_.append(coords_tmp)
        mask.append(np.all(coords_tmp != 0.))

    seq_ = ''.join(seq_)
    assert len(seq_) == len(xyz_)
    xyz_ = np.array(xyz_, dtype=np.float32)
    mask = np.array(mask)

    if temp_save_path is not None:
        pickle.dump((seq_, xyz_, mask), open(temp_save_path, 'wb'))
    return seq_, xyz_, mask

def PDBtoData(pdb_path, num_posenc, num_rbf, knn_num):
    seq, coords, mask = parse_pdb_direct(pdb_path)
    return construct_data_single(
        coords,
        seq,
        mask,
        num_posenc=num_posenc,
        num_rbf=num_rbf,
        knn_num=knn_num,
    )

def sample_to_fasta(sample, pdb_name, fasta_path):
    seq = ''.join(list(NUM_TO_LETTER[sample.cpu().numpy()]))
    with open(fasta_path, 'w') as f:
        f.write(f'>{pdb_name}\n')
        f.write(f'{seq}\n')


def clean_fasta(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        current_header = None
        current_sequence = []

        for line in infile:
            line = line.strip()

            if not line:
                continue

            if line.startswith('>'):
                if current_header is not None:
                    full_sequence = ''.join(current_sequence)
                    full_sequence = full_sequence.upper()
                    full_sequence = full_sequence.replace('T', 'U')
                    outfile.write(f"{current_header}\n")
                    outfile.write(f"{full_sequence}\n")

                current_header = line
                current_sequence = []
            else:
                current_sequence.append(line)

        if current_header is not None:
            full_sequence = ''.join(current_sequence)
            full_sequence = full_sequence.upper()
            full_sequence = full_sequence.replace('T', 'U')
            outfile.write(f"{current_header}\n")
            outfile.write(f"{full_sequence}\n")

