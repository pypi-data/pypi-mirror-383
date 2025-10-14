"""RNA-MSM Predictor for high-level MSA-based RNA analysis"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple

import numpy as np
import torch

from .adapter import RnaMSMAdapter
from ...core.base import BasePredictor
from ...core.exceptions import PredictionError, InvalidSequenceError
from ...utils.file_utils import process_sequence_input, save_npy_file, save_npz_file


class RnaMSMPredictor(BasePredictor):
    """High-level predictor for RNA-MSM model operations"""

    def __init__(self, model: RnaMSMAdapter):
        super().__init__(model)
        self.adapter = model

    def predict_single(self, input_data: Union[str, List[str], Dict[str, Any]]) -> Dict[str, Any]:
        """Predict on single input
        
        Args:
            input_data: Single RNA sequence, MSA sequences, or MSA data dict
            
        Returns:
            Prediction results with attention maps and embeddings
        """
        if not isinstance(input_data, (str, list, dict)):
            raise InvalidSequenceError("Input must be string, list, or dict")
            
        try:
            # Preprocess input
            processed_input = self.adapter.preprocess(input_data)
            
            # Run prediction
            raw_output = self.adapter.predict(processed_input)
            
            # Postprocess results
            results = self.adapter.postprocess(raw_output)
            
            # Add input metadata
            if isinstance(input_data, str):
                results["input_info"] = {
                    "input_type": "single_sequence",
                    "sequence_length": len(input_data),
                    "msa_depth": 1
                }
            elif isinstance(input_data, list):
                results["input_info"] = {
                    "input_type": "msa_sequences",
                    "sequence_length": len(input_data[0]) if input_data else 0,
                    "msa_depth": len(input_data)
                }
            else:
                sequences = input_data.get('sequences', [])
                results["input_info"] = {
                    "input_type": "msa_dict",
                    "sequence_length": len(sequences[0]) if sequences else 0,
                    "msa_depth": len(sequences)
                }
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Single prediction failed: {str(e)}")

    def predict_batch(self, input_batch: List[Any]) -> List[Dict[str, Any]]:
        """Predict on batch of inputs
        
        Args:
            input_batch: List of inputs (sequences, MSAs, or data dicts)
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, input_data in enumerate(input_batch):
            try:
                result = self.predict_single(input_data)
                result["batch_index"] = i
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process batch item {i}: {e}")
                results.append({
                    "batch_index": i,
                    "error": str(e),
                    "success": False
                })
        
        return results

    def extract_features(
        self,
        sequences: Union[str, List[str]],
        feature_type: str = "embeddings",
        layer: int = -1,
        save_path: Optional[str] = None
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """Extract features from RNA sequences
        
        Args:
            sequences: RNA sequence(s) or FASTA file path
            feature_type: Type of features to extract ("embeddings", "attention", "both")
            layer: Layer to extract from (-1 for last layer)
            save_path: Path to save features
            
        Returns:
            Extracted features as numpy arrays
        """
        try:
            # Process input sequences
            sequence_ids, sequence_list = process_sequence_input(sequences)
            
            # Update extraction settings
            original_layer = self.adapter.extract_layer
            original_attention = self.adapter.extract_attention
            original_embeddings = self.adapter.extract_embeddings
            
            self.adapter.extract_layer = layer
            self.adapter.extract_attention = feature_type in ["attention", "both"]
            self.adapter.extract_embeddings = feature_type in ["embeddings", "both"]
            
            results = {}
            
            for seq_id, sequence in zip(sequence_ids, sequence_list):
                prediction = self.predict_single(sequence)
                
                if feature_type == "embeddings" and "embeddings" in prediction:
                    results[seq_id] = prediction["embeddings"]
                elif feature_type == "attention" and "attention_maps" in prediction:
                    results[seq_id] = prediction["attention_maps"]
                elif feature_type == "both":
                    results[seq_id] = {
                        "embeddings": prediction.get("embeddings"),
                        "attention_maps": prediction.get("attention_maps")
                    }
            
            # Restore original settings
            self.adapter.extract_layer = original_layer
            self.adapter.extract_attention = original_attention
            self.adapter.extract_embeddings = original_embeddings
            
            # Save if requested
            if save_path:
                self._save_features(results, save_path, feature_type)
            
            # Return single result if single input
            if len(results) == 1 and isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas')):
                return next(iter(results.values()))
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Feature extraction failed: {str(e)}")

    def analyze_msa(
        self,
        msa_sequences: List[str],
        extract_consensus: bool = True,
        extract_conservation: bool = True,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze multiple sequence alignment
        
        Args:
            msa_sequences: List of aligned RNA sequences
            extract_consensus: Extract consensus sequence
            extract_conservation: Calculate conservation scores
            save_path: Path to save analysis results
            
        Returns:
            MSA analysis results
        """
        try:
            # Validate MSA
            if not msa_sequences or len(msa_sequences) < 2:
                raise InvalidSequenceError("MSA must contain at least 2 sequences")
            
            # Check alignment (all sequences same length)
            seq_length = len(msa_sequences[0])
            if not all(len(seq) == seq_length for seq in msa_sequences):
                raise InvalidSequenceError("MSA sequences must have the same length")
            
            # Run MSA prediction
            prediction = self.predict_single(msa_sequences)
            
            results = {
                "msa_info": {
                    "num_sequences": len(msa_sequences),
                    "alignment_length": seq_length,
                    "msa_depth": len(msa_sequences)
                },
                "features": {
                    "embeddings": prediction.get("embeddings"),
                    "attention_maps": prediction.get("attention_maps")
                }
            }
            
            # Extract consensus sequence
            if extract_consensus:
                consensus = self._extract_consensus(msa_sequences)
                results["consensus_sequence"] = consensus
            
            # Calculate conservation scores
            if extract_conservation:
                conservation = self._calculate_conservation(msa_sequences)
                results["conservation_scores"] = conservation
            
            # # Save if requested
            # if save_path:
            #     import json
            #     save_path = Path(save_path)
            #     save_path.parent.mkdir(parents=True, exist_ok=True)
            #     with open(save_path.with_suffix('.json'), 'w') as f:
            #         # Convert numpy arrays to lists for JSON serialization
            #         json_data = {
            #             "msa_info": results["msa_info"],
            #             "consensus_sequence": results["consensus_sequence"],
            #             "conservation_scores": results["conservation_scores"]
            #         }
            #         json.dump(json_data, f, indent=2)
            
            return results
            
        except Exception as e:
            raise PredictionError(f"MSA analysis failed: {str(e)}")

    def compare_sequences(
        self,
        seq1: Union[str, List[str]],
        seq2: Union[str, List[str]],
        comparison_method: str = "embedding_similarity"
    ) -> Dict[str, Any]:
        """Compare sequences using MSA-based features
        
        Args:
            seq1: First sequence or MSA
            seq2: Second sequence or MSA
            comparison_method: Method for comparison
            
        Returns:
            Comparison results
        """
        try:
            # Get features for both inputs
            features1 = self.extract_features(seq1, "embeddings")
            features2 = self.extract_features(seq2, "embeddings")
            
            # Handle single vs multiple sequences
            if isinstance(features1, dict):
                emb1 = next(iter(features1.values()))
            else:
                emb1 = features1
                
            if isinstance(features2, dict):
                emb2 = next(iter(features2.values()))
            else:
                emb2 = features2
            
            # Calculate similarity
            if comparison_method == "embedding_similarity":
                # Cosine similarity between mean embeddings
                mean_emb1 = np.mean(emb1, axis=0)
                mean_emb2 = np.mean(emb2, axis=0)
                
                similarity = np.dot(mean_emb1, mean_emb2) / (
                    np.linalg.norm(mean_emb1) * np.linalg.norm(mean_emb2)
                )
                
                results = {
                    "similarity_score": float(similarity),
                    "comparison_method": comparison_method,
                    "embedding_dims": emb1.shape,
                }
            else:
                raise ValueError(f"Unsupported comparison method: {comparison_method}")
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Sequence comparison failed: {str(e)}")

    def _extract_consensus(self, msa_sequences: List[str]) -> str:
        """Extract consensus sequence from MSA"""
        seq_length = len(msa_sequences[0])
        consensus = []
        
        for pos in range(seq_length):
            # Count nucleotides at position
            counts = {'A': 0, 'U': 0, 'G': 0, 'C': 0, '-': 0}
            
            for seq in msa_sequences:
                if pos < len(seq):
                    nucl = seq[pos].upper()
                    if nucl in counts:
                        counts[nucl] += 1
            
            # Select most frequent nucleotide
            consensus_nucl = max(counts, key=counts.get)
            consensus.append(consensus_nucl)
        
        return ''.join(consensus)

    def _calculate_conservation(self, msa_sequences: List[str]) -> List[float]:
        """Calculate conservation scores for each position"""
        seq_length = len(msa_sequences[0])
        conservation_scores = []
        
        for pos in range(seq_length):
            # Count nucleotides at position
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
            
            # Convert entropy to conservation (lower entropy = higher conservation)
            max_entropy = np.log2(5)  # 5 possible states (A,U,G,C,-)
            conservation = 1.0 - (entropy / max_entropy)
            conservation_scores.append(conservation)
        
        return conservation_scores

    def _save_features(self, results: Dict[str, Any], save_path: str, feature_type: str):
        """Save extracted features to file"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        if feature_type in ["embeddings", "attention"]:
            # Save as .npz for multiple sequences
            if len(results) > 1:
                np.savez_compressed(save_path.with_suffix('.npz'), **results)
            else:
                # Save as .npy for single sequence
                single_result = next(iter(results.values()))
                np.save(save_path.with_suffix('.npy'), single_result)
        else:
            # Save as pickle for complex data
            import pickle
            with open(save_path.with_suffix('.pkl'), 'wb') as f:
                pickle.dump(results, f)
        
        self.logger.info(f"Features saved to {save_path}")

    def get_predictor_info(self) -> Dict[str, Any]:
        """Get predictor information"""
        return {
            "predictor_type": "RnaMSMPredictor",
            "model_info": self.adapter.get_model_info(),
            "capabilities": [
                "feature_extraction",
                "msa_analysis",
                "sequence_comparison",
                "batch_processing"
            ]
        } 