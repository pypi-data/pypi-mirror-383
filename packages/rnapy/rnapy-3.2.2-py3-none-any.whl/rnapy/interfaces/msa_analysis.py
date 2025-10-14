"""MSA Analysis Interface for RNA-MSM based operations"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

import numpy as np

from ..core.exceptions import ModelNotFoundError, PredictionError, InvalidSequenceError
from ..core.factory import ModelFactory
from ..utils.file_utils import process_sequence_input, save_npy_file, save_npz_file


class MSAAnalysisInterface:
    """Interface for Multiple Sequence Alignment based RNA analysis using RNA-MSM"""
    
    def __init__(self, model_factory: ModelFactory, loaded_models: Dict[str, Any] = None):
        self.factory = model_factory
        self.loaded_models = loaded_models or {}
        self.logger = logging.getLogger(__name__)

    def update_loaded_models(self, loaded_models: Dict[str, Any]):
        """Update loaded models reference"""
        self.loaded_models = loaded_models

    def extract_msa_features(
        self,
        sequences: Union[str, List[str]],
        feature_type: str = "embeddings",
        model: str = "rna-msm",
        layer: int = -1,
        save_dir: Optional[str] = None,
        **kwargs
    ) -> Union[np.ndarray, Dict[str, np.ndarray], Dict[str, Any]]:
        """Extract features from RNA sequences using MSA transformer
        
        Args:
            sequences: RNA sequence(s) or FASTA file path
            feature_type: Type of features ("embeddings", "attention", "both")  
            model: Model name to use
            layer: Layer to extract from (-1 for last layer)
            save_dir: Directory to save features
            **kwargs: Additional parameters
            
        Returns:
            Extracted features as numpy arrays or dict
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Process input sequences
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
            
            # Create predictor for the model
            from ..providers.rna_msm import RnaMSMPredictor
            predictor = RnaMSMPredictor(model_instance)
            
            results = {}
            
            # Extract features for each sequence/MSA
            for seq_id, sequence in zip(sequence_ids, sequence_list):
                feature_result = predictor.extract_features(
                    sequence, 
                    feature_type=feature_type,
                    layer=layer,
                    save_path=None  # Handle saving here
                )
                results[seq_id] = feature_result
            
            # Save if requested
            if save_dir:
                save_dir = Path(save_dir)
                save_dir.mkdir(parents=True, exist_ok=True)
                
                for seq_id, feature_data in results.items():
                    if feature_type == "embeddings" and isinstance(feature_data, np.ndarray):
                        save_npy_file(feature_data, save_dir / f"{seq_id}_embeddings.npy")
                    elif feature_type == "attention" and isinstance(feature_data, np.ndarray):
                        save_npy_file(feature_data, save_dir / f"{seq_id}_attention.npy")
                    elif feature_type == "both" and isinstance(feature_data, dict):
                        if "embeddings" in feature_data:
                            save_npy_file(feature_data["embeddings"], save_dir / f"{seq_id}_embeddings.npy")
                        if "attention_maps" in feature_data:
                            save_npy_file(feature_data["attention_maps"], save_dir / f"{seq_id}_attention.npy")
            
            # Return single result if single input
            if is_single_input and len(results) == 1:
                return next(iter(results.values()))
            
            return results
            
        except Exception as e:
            raise PredictionError(f"MSA feature extraction failed: {str(e)}")

    def analyze_msa(
        self,
        msa_sequences: List[str],
        model: str = "rna-msm", 
        extract_consensus: bool = True,
        extract_conservation: bool = True,
        save_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze Multiple Sequence Alignment
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use
            extract_consensus: Extract consensus sequence
            extract_conservation: Calculate conservation scores
            save_dir: Directory to save analysis results
            **kwargs: Additional parameters
            
        Returns:
            MSA analysis results including features, consensus, conservation
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            if not msa_sequences or len(msa_sequences) < 2:
                raise InvalidSequenceError("MSA must contain at least 2 sequences")

            # Check alignment (all sequences same length)
            seq_length = len(msa_sequences[0])
            if not all(len(seq) == seq_length for seq in msa_sequences):
                raise InvalidSequenceError("MSA sequences must have the same length")

            model_instance = self.loaded_models[model]
            
            # Create predictor
            from ..providers.rna_msm import RnaMSMPredictor
            predictor = RnaMSMPredictor(model_instance)
            
            # Run MSA analysis
            results = predictor.analyze_msa(
                msa_sequences,
                extract_consensus=extract_consensus,
                extract_conservation=extract_conservation,
                save_path=None  # Handle saving here
            )
            
            # Save if requested
            if save_dir:
                save_dir = Path(save_dir)
                save_dir.mkdir(parents=True, exist_ok=True)
                
                # Save features
                if 'features' in results:
                    features = results['features']
                    if 'embeddings' in features and features['embeddings'] is not None:
                        save_npy_file(features['embeddings'], save_dir / "msa_embeddings.npy")
                    if 'attention_maps' in features and features['attention_maps'] is not None:
                        save_npy_file(features['attention_maps'], save_dir / "msa_attention.npy")
                
                # Save analysis results as JSON
                json_data = {
                    "msa_info": results["msa_info"],
                    "consensus_sequence": results.get("consensus_sequence"),
                    "conservation_scores": results.get("conservation_scores")
                }
                
                with open(save_dir / "msa_analysis.json", 'w') as f:
                    json.dump(json_data, f, indent=2)
                
                self.logger.info(f"MSA analysis results saved to {save_dir}")
            
            return results
            
        except Exception as e:
            raise PredictionError(f"MSA analysis failed: {str(e)}")

    def compare_sequences_msa(
        self,
        seq1: Union[str, List[str]],
        seq2: Union[str, List[str]],
        model: str = "rna-msm",
        comparison_method: str = "embedding_similarity",
        **kwargs
    ) -> Dict[str, Any]:
        """Compare sequences using MSA-based features
        
        Args:
            seq1: First sequence or MSA
            seq2: Second sequence or MSA  
            model: Model name to use
            comparison_method: Method for comparison
            **kwargs: Additional parameters
            
        Returns:
            Comparison results with similarity scores
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Create predictor
            from ..providers.rna_msm import RnaMSMPredictor
            predictor = RnaMSMPredictor(model_instance)
            
            # Run sequence comparison
            results = predictor.compare_sequences(
                seq1, seq2, 
                comparison_method=comparison_method
            )
            
            # Add metadata
            results.update({
                'model': model,
                'input1_type': 'msa' if isinstance(seq1, list) else 'sequence',
                'input2_type': 'msa' if isinstance(seq2, list) else 'sequence'
            })
            
            return results
            
        except Exception as e:
            raise PredictionError(f"MSA sequence comparison failed: {str(e)}")

    def extract_consensus_sequence(
        self,
        msa_sequences: List[str],
        model: str = "rna-msm",
        **kwargs
    ) -> str:
        """Extract consensus sequence from MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use
            **kwargs: Additional parameters
            
        Returns:
            Consensus sequence string
        """
        try:
            if not msa_sequences or len(msa_sequences) < 2:
                raise InvalidSequenceError("MSA must contain at least 2 sequences")

            # Check alignment
            seq_length = len(msa_sequences[0])
            if not all(len(seq) == seq_length for seq in msa_sequences):
                raise InvalidSequenceError("MSA sequences must have the same length")

            # Simple consensus extraction (most frequent nucleotide at each position)
            consensus = []
            for pos in range(seq_length):
                counts = {'A': 0, 'U': 0, 'G': 0, 'C': 0, '-': 0}
                
                for seq in msa_sequences:
                    if pos < len(seq):
                        nucl = seq[pos].upper()
                        if nucl in counts:
                            counts[nucl] += 1
                
                consensus_nucl = max(counts, key=counts.get)
                consensus.append(consensus_nucl)
            
            return ''.join(consensus)
            
        except Exception as e:
            raise PredictionError(f"Consensus extraction failed: {str(e)}")

    def calculate_conservation_scores(
        self,
        msa_sequences: List[str],
        **kwargs
    ) -> List[float]:
        """Calculate conservation scores for each position in MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            **kwargs: Additional parameters
            
        Returns:
            List of conservation scores (0-1, higher = more conserved)
        """
        try:
            if not msa_sequences or len(msa_sequences) < 2:
                raise InvalidSequenceError("MSA must contain at least 2 sequences")

            seq_length = len(msa_sequences[0])
            if not all(len(seq) == seq_length for seq in msa_sequences):
                raise InvalidSequenceError("MSA sequences must have the same length")

            conservation_scores = []
            
            for pos in range(seq_length):
                counts = {'A': 0, 'U': 0, 'G': 0, 'C': 0, '-': 0}
                total = 0
                
                for seq in msa_sequences:
                    if pos < len(seq):
                        nucl = seq[pos].upper()
                        if nucl in counts:
                            counts[nucl] += 1
                            total += 1
                
                if total == 0:
                    conservation_scores.append(0.0)
                    continue
                
                # Calculate Shannon entropy
                entropy = 0.0
                for count in counts.values():
                    if count > 0:
                        freq = count / total
                        entropy -= freq * np.log2(freq)
                
                # Convert to conservation (lower entropy = higher conservation)
                max_entropy = np.log2(5)  # 5 possible states (A,U,G,C,-)
                conservation = 1.0 - (entropy / max_entropy)
                conservation_scores.append(conservation)
            
            return conservation_scores
            
        except Exception as e:
            raise PredictionError(f"Conservation calculation failed: {str(e)}")

    def batch_msa_analysis(
        self,
        msa_list: List[List[str]],
        model: str = "rna-msm",
        extract_consensus: bool = True,
        extract_conservation: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Batch analyze multiple MSAs
        
        Args:
            msa_list: List of MSA sequences (each MSA is a list of sequences)
            model: Model name to use
            extract_consensus: Extract consensus for each MSA
            extract_conservation: Calculate conservation for each MSA
            **kwargs: Additional parameters
            
        Returns:
            List of MSA analysis results
        """
        results = []
        
        for i, msa_sequences in enumerate(msa_list):
            try:
                result = self.analyze_msa(
                    msa_sequences,
                    model=model,
                    extract_consensus=extract_consensus,
                    extract_conservation=extract_conservation,
                    **kwargs
                )
                result['msa_index'] = i
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze MSA {i}: {e}")
                results.append({
                    'msa_index': i,
                    'error': str(e),
                    'failed': True
                })
        
        return results

    def get_msa_statistics(self, msa_sequences: List[str]) -> Dict[str, Any]:
        """Get basic statistics for an MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            
        Returns:
            MSA statistics including length, depth, composition
        """
        try:
            if not msa_sequences:
                raise InvalidSequenceError("Empty MSA")

            seq_length = len(msa_sequences[0])
            msa_depth = len(msa_sequences)
            
            # Check if aligned
            is_aligned = all(len(seq) == seq_length for seq in msa_sequences)
            
            # Calculate composition
            total_counts = {'A': 0, 'U': 0, 'G': 0, 'C': 0, '-': 0, 'N': 0}
            total_chars = 0
            
            for seq in msa_sequences:
                for char in seq.upper():
                    if char in total_counts:
                        total_counts[char] += 1
                    else:
                        total_counts['N'] += 1
                    total_chars += 1
            
            # Calculate frequencies
            composition = {}
            if total_chars > 0:
                for nucleotide, count in total_counts.items():
                    composition[nucleotide] = count / total_chars
            
            return {
                'msa_depth': msa_depth,
                'alignment_length': seq_length,
                'is_aligned': is_aligned,
                'composition': composition,
                'gap_frequency': composition.get('-', 0.0),
                'gc_content': composition.get('G', 0) + composition.get('C', 0)
            }
            
        except Exception as e:
            raise PredictionError(f"MSA statistics calculation failed: {str(e)}") 