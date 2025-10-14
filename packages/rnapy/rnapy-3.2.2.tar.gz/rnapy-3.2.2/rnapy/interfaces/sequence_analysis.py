import os
import time
from typing import Dict, Any, List, Union

import networkx as nx
import numpy as np
from Bio import pairwise2
from networkx.algorithms.similarity import optimize_graph_edit_distance

from ..core.exceptions import ModelNotFoundError, PredictionError
from ..core.factory import ModelFactory
from ..utils.file_utils import save_npy_file, process_sequence_input


class SequenceAnalysisInterface:
    def __init__(self, model_factory: ModelFactory, loaded_models: Dict[str, Any] = None):
        self.factory = model_factory
        self.loaded_models = loaded_models or {}

    def update_loaded_models(self, loaded_models: Dict[str, Any]):
        self.loaded_models = loaded_models

    def analyze_sequence(self, sequences: Union[str, List[str]],
                         analysis_type: str = "full",
                         model: str = "rna-fm",
                         **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Comprehensive sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type ("full", "properties", "embedding", "structure")
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Analysis results - single dict for single sequence, list for multiple
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_sequence = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
            
            results_list = []
            for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
                results = {
                    'sequence': sequence,
                    'sequence_id': seq_id,
                    'length': len(sequence),
                    'analysis_type': analysis_type
                }

                if analysis_type in ["full", "properties"]:
                    results.update(self._analyze_basic_properties(sequence))

                # Extract embeddings
                if analysis_type in ["full", "embedding"]:
                    embeddings = model_instance.extract_embeddings([sequence])
                    results['embeddings'] = embeddings[0]
                    results['embedding_stats'] = {
                        'shape': embeddings[0].shape,
                        'mean': float(np.mean(embeddings[0])),
                        'std': float(np.std(embeddings[0]))
                    }

                # Predict structure
                if analysis_type in ["full", "structure"]:
                    structure_results = model_instance.predict(
                        sequence,
                        return_embeddings=False,
                        return_contacts=True,
                        return_attention=False
                    )

                    if 'secondary_structure' in structure_results and structure_results['secondary_structure']:
                        structure = structure_results['secondary_structure'][0]
                        results['secondary_structure'] = structure
                        results['structure_info'] = self._analyze_structure(structure)

                    if 'contacts' in structure_results:
                        results['contacts'] = structure_results['contacts'][0]

                results_list.append(results)
            
            return results_list[0] if is_single_sequence else results_list

        except Exception as e:
            raise PredictionError(f"Sequence analysis failed: {str(e)}")

    def extract_embeddings(self, sequences: Union[str, List[str]],
                           model: str = "rna-fm",
                           layer: int = 12,
                           format: str = "raw",
                           save_dir: str = None,
                           **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Extract embeddings for sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name
            layer: Layer number for extraction
            format: Format ("raw", "mean", "bos")
            save_dir: File path to save embeddings
            **kwargs: Additional parameters
            
        Returns:
            Embeddings array or list of arrays
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))

            embeddings = model_instance.extract_embeddings(sequence_list, layer, format)
            
            # Handle save file
            for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
                if save_dir:
                    filename = f"{seq_id}_embeddings.npy" if is_single_input else f"{seq_id}_embeddings.npy"
                    filepath = os.path.join(save_dir, filename) if os.path.isdir(save_dir) else save_dir
                    save_npy_file(embeddings[i], filepath)

            return embeddings[0] if is_single_input else embeddings

        except Exception as e:
            raise PredictionError(f"Embedding extraction failed: {str(e)}")

    def compare_sequences(self, seq1: Union[str, List[str]], seq2: Union[str, List[str]],
                          model: str = "rna-fm",
                          comparison_type: str = "sequence",
                          embedding_format: str = "raw",
                          **kwargs) -> Dict[str, Any]:
        """Compare two sequences or sequence sets
        
        Args:
            seq1: First sequence(s) or FASTA file
            seq2: Second sequence(s) or FASTA file
            model: Model name
            comparison_type: Comparison type ("full", "sequence", "embedding", "structure")
            embedding_format: Format ("raw", "mean", "bos")
            **kwargs: Additional parameters
            
        Returns:
            Comparison results
        """
        try:
            # Process both inputs
            ids1, seqs1 = process_sequence_input(seq1)
            ids2, seqs2 = process_sequence_input(seq2)
            
            # For simplicity, compare first sequences if multiple provided
            seq1_str = seqs1[0]
            seq2_str = seqs2[0]
            
            results = {'sequence1': seq1_str, 'sequence2': seq2_str, 'sequence1_id': ids1[0], 'sequence2_id': ids2[0],
                       'lengths': [len(seq1_str), len(seq2_str)], 'comparison_type': comparison_type,
                       'embedding_format': embedding_format,
                       'sequence_similarity': self._calculate_sequence_similarity(seq1_str, seq2_str)}

            # Embedding similarity
            if comparison_type in ["full", "embedding"]:
                emb1 = self.extract_embeddings(seq1_str, model, format=embedding_format, **kwargs)
                emb2 = self.extract_embeddings(seq2_str, model, format=embedding_format, **kwargs)
                results['embedding_similarity'] = self._calculate_embedding_similarity(emb1, emb2)

            # Structure similarity
            if comparison_type in ["full", "structure"]:
                if model not in self.loaded_models:
                    raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

                model_instance = self.loaded_models[model]

                struct1 = model_instance.predict_secondary_structure([seq1_str])
                struct2 = model_instance.predict_secondary_structure([seq2_str])

                if struct1 and struct2:
                    results['structure_similarity'] = self._calculate_structure_similarity(struct1[0], struct2[0])
                    results['structures'] = [struct1[0], struct2[0]]

            return results

        except Exception as e:
            raise PredictionError(f"Sequence comparison failed: {str(e)}")

    def compare_structures(self, struct1: str, struct2: str) -> Dict[str, Any]:
        """Compare two RNA secondary structures in dot-bracket notation

        Args:
            struct1: First structure string
            struct2: Second structure string

        Returns:
            Structure comparison results
        """
        try:
            if not struct1 or not struct2:
                raise ValueError("Both structure strings must be non-empty.")

            results = {
                'structure1': struct1,
                'structure2': struct2,
                'lengths': [len(struct1), len(struct2)],
                'structure_similarity': self._compare_second_structure_dot(struct1, struct2)
            }

            return results

        except Exception as e:
            raise PredictionError(f"Structure comparison failed: {str(e)}")

    def batch_analyze(self, sequences: Union[str, List[str]],
                      analysis_type: str = "full",
                      model: str = "rna-fm",
                      **kwargs) -> List[Dict[str, Any]]:
        """Batch analyze multiple sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type ("full", "properties", "embedding", "structure")
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            List of analysis results
        """
        # Process input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        
        results = []
        for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
            try:
                result = self.analyze_sequence(sequence, analysis_type, model, **kwargs)
                if isinstance(result, list):
                    result = result[0]  # Single sequence should return single result
                result['sequence_index'] = i
                results.append(result)

            except Exception as e:
                results.append({
                    'sequence_index': i,
                    'sequence': sequence,
                    'sequence_id': seq_id,
                    'error': str(e),
                    'failed': True
                })

        return results

    def _analyze_basic_properties(self, sequence: str) -> Dict[str, Any]:
        seq_upper = sequence.upper()
        length = len(sequence)

        return {
            'gc_content': (seq_upper.count('G') + seq_upper.count('C')) / length,
            'composition': {
                'A': seq_upper.count('A') / length,
                'U': seq_upper.count('U') / length,
                'G': seq_upper.count('G') / length,
                'C': seq_upper.count('C') / length
            },
            'purine_content': (seq_upper.count('A') + seq_upper.count('G')) / length,
            'pyrimidine_content': (seq_upper.count('C') + seq_upper.count('U')) / length
        }

    def _analyze_structure(self, structure: str) -> Dict[str, Any]:
        return {
            'length': len(structure),
            'paired_bases': structure.count('(') + structure.count(')'),
            'unpaired_bases': structure.count('.'),
            'pairing_ratio': (structure.count('(') + structure.count(')')) / len(structure),
            'stem_count': self._count_stems(structure)
        }

    def _count_stems(self, structure: str) -> int:
        stem_count = 0
        in_stem = False

        for char in structure:
            if char == '(' and not in_stem:
                stem_count += 1
                in_stem = True
            elif char == '.' and in_stem:
                in_stem = False

        return stem_count

    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float | None:
        if not seq1 or not seq2:
            return 0.0

        alignments = pairwise2.align.localxx(seq1, seq2)

        if len(alignments) > 0:
            c = 0
            for i in range(len(alignments[0].seqA)):
                if alignments[0].seqA[i] == alignments[0].seqB[i]:
                    c += 1
            score = c / len(alignments[0].seqA)
            return score
        else:
            return None

    def _calculate_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        if emb1.ndim > 1:
            emb1_mean = np.mean(emb1, axis=0)
        else:
            emb1_mean = emb1

        if emb2.ndim > 1:
            emb2_mean = np.mean(emb2, axis=0)
        else:
            emb2_mean = emb2

        dot_product = np.dot(emb1_mean, emb2_mean)
        norm1 = np.linalg.norm(emb1_mean)
        norm2 = np.linalg.norm(emb2_mean)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _calculate_structure_similarity(self, struct1: str, struct2: str) -> float:
        if len(struct1) != len(struct2):
            min_len = min(len(struct1), len(struct2))
            matches = sum(1 for i in range(min_len) if struct1[i] == struct2[i])
            return matches / max(len(struct1), len(struct2))
        else:
            matches = sum(1 for i in range(len(struct1)) if struct1[i] == struct2[i])
            return matches / len(struct1)

    def calculate_structure_f1(self, struct1: str, struct2: str) -> Dict[str, float]:
        """Calculate F1 score for secondary structure comparison
        
        Args:
            struct1: First structure in dot-bracket notation
            struct2: Second structure in dot-bracket notation
            
        Returns:
            Dictionary with precision, recall, and f1_score
        """
        struct1 = struct1.replace("&", ".")
        struct2 = struct2.replace("&", ".")
        
        pairs1 = self._extract_base_pairs(struct1)
        pairs2 = self._extract_base_pairs(struct2)
        
        if not pairs1 and not pairs2:
            return {'precision': 1.0, 'recall': 1.0, 'f1_score': 1.0}
        
        if not pairs2:
            return {'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
        
        if not pairs1:
            return {'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
        
        true_positives = len(pairs1.intersection(pairs2))
        
        precision = true_positives / len(pairs2) if len(pairs2) > 0 else 0.0
        recall = true_positives / len(pairs1) if len(pairs1) > 0 else 0.0
        
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        return {
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score)
        }

    def _extract_base_pairs(self, structure: str) -> set:
        """Extract base pairs from dot-bracket notation"""
        pairs = set()
        stack_round = []
        stack_square = []
        stack_curly = []
        
        for i, char in enumerate(structure):
            if char == '(':
                stack_round.append(i)
            elif char == ')':
                if stack_round:
                    j = stack_round.pop()
                    pairs.add((j, i) if j < i else (i, j))
            elif char == '[':
                stack_square.append(i)
            elif char == ']':
                if stack_square:
                    j = stack_square.pop()
                    pairs.add((j, i) if j < i else (i, j))
            elif char == '{':
                stack_curly.append(i)
            elif char == '}':
                if stack_curly:
                    j = stack_curly.pop()
                    pairs.add((j, i) if j < i else (i, j))
        
        return pairs

    def calculate_sequence_recovery(self, native_seq: str, designed_seq: str) -> Dict[str, Any]:
        """Calculate sequence recovery rate
        
        Args:
            native_seq: Native/reference sequence
            designed_seq: Designed/predicted sequence
            
        Returns:
            Dictionary with overall and per-nucleotide recovery rates
        """
        native_seq = native_seq.upper().replace('T', 'U')
        designed_seq = designed_seq.upper().replace('T', 'U')
        
        min_len = min(len(native_seq), len(designed_seq))
        
        total_matches = 0
        nucleotide_matches = {'A': 0, 'U': 0, 'G': 0, 'C': 0}
        nucleotide_counts = {'A': 0, 'U': 0, 'G': 0, 'C': 0}
        
        for i in range(min_len):
            nat_base = native_seq[i]
            des_base = designed_seq[i]
            
            if nat_base in nucleotide_counts:
                nucleotide_counts[nat_base] += 1
                
                if nat_base == des_base:
                    total_matches += 1
                    nucleotide_matches[nat_base] += 1
        
        overall_recovery = total_matches / min_len if min_len > 0 else 0.0
        
        per_nucleotide_recovery = {}
        for base in ['A', 'U', 'G', 'C']:
            if nucleotide_counts[base] > 0:
                per_nucleotide_recovery[base] = nucleotide_matches[base] / nucleotide_counts[base]
            else:
                per_nucleotide_recovery[base] = 0.0
        
        return {
            'overall_recovery': float(overall_recovery),
            'total_matches': total_matches,
            'total_positions': min_len,
            'per_nucleotide_recovery': per_nucleotide_recovery,
            'nucleotide_counts': nucleotide_counts
        }

    def _dotbracket_to_graph(self, dot_bracket) -> nx.Graph:
        G = nx.Graph()
        dot_bracket = dot_bracket.replace("&", ".")
        # Stacks to keep track of different types of brackets
        stack_round = []
        stack_square = []
        stack_curly = []

        # Map closing bracket to corresponding stack
        bracket_map = {')': stack_round, ']': stack_square, '}': stack_curly}

        # Iterate over the dot-bracket string
        for i, char in enumerate(dot_bracket):
            G.add_node(i)
            if char in ['(', '[', '{']:
                # Open bracket, push to corresponding stack
                if char == '(':
                    stack_round.append(i)
                elif char == '[':
                    stack_square.append(i)
                elif char == '{':
                    stack_curly.append(i)
            elif char in [')', ']', '}']:
                # Close bracket, pop from corresponding stack and add edge
                stack = bracket_map[char]
                if stack:
                    j = stack.pop()
                    G.add_edge(j, i)
                else:
                    raise ValueError(f"Unmatched closing bracket '{char}' at position {i}")

        # Check for unmatched opening brackets
        for stack, bracket in zip([stack_round, stack_square, stack_curly], ['(', '[', '{']):
            if stack:
                raise ValueError(f"Unmatched opening bracket '{bracket}' remains")

        # Add edges for sequential connectivity
        for i in range(len(dot_bracket) - 1):
            G.add_edge(i, i + 1)

        return G

    def _compare_second_structure_dot(self, dot1, dot2, max_time_seconds=-1) -> float:
        start_time = time.time()
        rna_graph = self._dotbracket_to_graph(dot1)
        rna_graph1 = self._dotbracket_to_graph(dot2)
        min_v = float('inf')

        # Calculate the total/average number of vertices and edges
        total_vertices = len(rna_graph.nodes) + len(rna_graph1.nodes)
        total_edges = len(rna_graph.edges) + len(rna_graph1.edges)
        norm_factor = (total_vertices + total_edges) / 2

        for v in optimize_graph_edit_distance(rna_graph, rna_graph1):
            if max_time_seconds <= 0:
                return v / norm_factor
            min_v = min(min_v, v)
            current_time = time.time()
            if current_time - start_time > max_time_seconds:
                break

        # Normalize the minimum value
        normalized_v = min_v / norm_factor

        return normalized_v


