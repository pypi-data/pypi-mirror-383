"""RNA-FM Predictor Implementation"""

from typing import Dict, Any, List, Union, Optional
import numpy as np
from pathlib import Path

from ...core.base import BasePredictor
from ...core.exceptions import PredictionError, InvalidSequenceError
from .adapter import RNAFMAdapter


class RNAFMPredictor(BasePredictor):
    def __init__(self, model: RNAFMAdapter):
        super().__init__(model)
        
    def predict_single(self, input_data: str, 
                      analysis_type: str = "full") -> Dict[str, Any]:
        """Single prediction
        
        Args:
            input_data: RNA sequence
            analysis_type: Type of analysis ("full", "embedding", "structure", "contacts")
        """
        if not self.validate_input(input_data):
            raise InvalidSequenceError(f"Invalid RNA sequence: {input_data}")
        
        # Set parameters based on analysis type
        return_embeddings = analysis_type in ["full", "embedding"]
        return_contacts = analysis_type in ["full", "structure", "contacts"]
        return_attention = analysis_type == "full"
        
        try:
            result = self.model.predict(
                input_data,
                return_embeddings=return_embeddings,
                return_contacts=return_contacts,
                return_attention=return_attention
            )
            
            # Add metadata
            result['sequence_length'] = len(input_data)
            result['analysis_type'] = analysis_type
            
            return result
            
        except Exception as e:
            raise PredictionError(f"Single prediction failed: {str(e)}")
    
    def predict_batch(self, input_batch: List[str], 
                     analysis_type: str = "full") -> List[Dict[str, Any]]:
        if not input_batch:
            return []
        
        # validate all sequences
        for i, seq in enumerate(input_batch):
            if not self.validate_input(seq):
                raise InvalidSequenceError(f"Invalid RNA sequence at index {i}: {seq}")
        
        try:
            return_embeddings = analysis_type in ["full", "embedding"]
            return_contacts = analysis_type in ["full", "structure", "contacts"]
            return_attention = analysis_type == "full"

            result = self.model.predict(
                input_batch,
                return_embeddings=return_embeddings,
                return_contacts=return_contacts,
                return_attention=return_attention
            )

            batch_results = []
            for i, seq in enumerate(input_batch):
                single_result = {
                    'sequence': seq,
                    'sequence_length': len(seq),
                    'analysis_type': analysis_type
                }
                
                if return_embeddings and 'embeddings' in result:
                    single_result['embeddings'] = result['embeddings'][i]
                
                if return_contacts and 'contacts' in result:
                    single_result['contacts'] = result['contacts'][i]
                
                if return_contacts and 'secondary_structure' in result:
                    single_result['secondary_structure'] = result['secondary_structure'][i]
                
                if return_attention and 'attention_weights' in result:
                    single_result['attention_weights'] = {
                        layer: attn[i] for layer, attn in result['attention_weights'].items()
                    }
                
                batch_results.append(single_result)
            
            return batch_results
            
        except Exception as e:
            raise PredictionError(f"Batch prediction failed: {str(e)}")
    
    def extract_embeddings(self, sequences: Union[str, List[str]], 
                          layer: int = 12,
                          format: str = "raw") -> Union[np.ndarray, List[np.ndarray]]:
        """Extract embeddings with different formats
        
        Args:
            sequences: Single sequence or list of sequences
            layer: Layer to extract embeddings from
            format: Format type - "raw", "mean", "bos"
        
        Returns:
            Embedding array (single or list)
        """
        try:
            embeddings = self.model.extract_embeddings(sequences, layer, format)
            
            if isinstance(sequences, str):
                return embeddings[0] if format == "raw" else embeddings  # Return single embedding
            else:
                return [embeddings[i] for i in range(len(sequences))] if format == "raw" else embeddings
                
        except Exception as e:
            raise PredictionError(f"Embedding extraction failed: {str(e)}")
    
    def predict_secondary_structure(self, sequences: Union[str, List[str]], 
                                  threshold: float = 0.5,
                                  advanced_postprocess: bool = True,
                                  allow_noncanonical: bool = True) -> Union[str, List[str]]:
        """Predict secondary structure with advanced options
        
        Args:
            sequences: Sequence Array (single or list)
            threshold: Threshold for base pairing
            advanced_postprocess: Use advanced postprocessing with multiplet handling
            allow_noncanonical: Allow non-canonical base pairs
            
        Returns:
            Secondary structure in dot-bracket notation (single or list)
        """
        try:
            structures = self.model.predict_secondary_structure(
                sequences, threshold, advanced_postprocess, allow_noncanonical
            )
            
            if isinstance(sequences, str):
                return structures[0]  # Return single structure
            else:
                return structures
                
        except Exception as e:
            raise PredictionError(f"Secondary structure prediction failed: {str(e)}")
    
    def save_ct_files(self, sequences: Union[str, List[str]], 
                     output_dir: str,
                     sequence_ids: Optional[List[str]] = None,
                     threshold: float = 0.5,
                     advanced_postprocess: bool = True,
                     allow_noncanonical: bool = True) -> List[str]:
        """Generate and save CT files for sequences
        
        Args:
            sequences: RNA sequences
            output_dir: Output directory for CT files
            sequence_ids: Optional sequence identifiers
            threshold: Contact probability threshold
            advanced_postprocess: Use advanced postprocessing
            allow_noncanonical: Allow non-canonical pairs
            
        Returns:
            List of generated CT file paths
        """
        try:
            return self.model.save_ct_file(
                sequences, output_dir, sequence_ids, 
                threshold, advanced_postprocess, allow_noncanonical
            )
        except Exception as e:
            raise PredictionError(f"CT file generation failed: {str(e)}")
    
    def analyze_sequence_properties(self, sequence: str) -> Dict[str, Any]:
        """Analyze comprehensive sequence properties"""
        try:
            properties = {
                'length': len(sequence),
                'gc_content': (sequence.upper().count('G') + sequence.upper().count('C')) / len(sequence),
                'composition': {
                    'A': sequence.upper().count('A') / len(sequence),
                    'U': sequence.upper().count('U') / len(sequence),
                    'G': sequence.upper().count('G') / len(sequence),
                    'C': sequence.upper().count('C') / len(sequence)
                }
            }

            result = self.predict_single(sequence, analysis_type="full")

            if 'secondary_structure' in result:
                structure = result['secondary_structure']
                properties['structure_info'] = self._analyze_structure(structure)

            if 'embeddings' in result:
                embeddings = result['embeddings']
                properties['embedding_stats'] = {
                    'mean': float(np.mean(embeddings)),
                    'std': float(np.std(embeddings)),
                    'shape': embeddings.shape
                }
            
            return properties
            
        except Exception as e:
            raise PredictionError(f"Sequence analysis failed: {str(e)}")
    
    def compare_sequences(self, seq1: str, seq2: str, 
                         comparison_type: str = "full",
                         embedding_format: str = "raw") -> Dict[str, Any]:
        """Compare two sequences with advanced options
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            comparison_type: Type of comparison ("full", "embedding", "structure")
            embedding_format: Format for embedding comparison
        """
        try:
            results = {
                'sequence_lengths': [len(seq1), len(seq2)],
                'comparison_type': comparison_type
            }
            
            if comparison_type in ["full", "embedding"]:
                emb1 = self.extract_embeddings(seq1, format=embedding_format)
                emb2 = self.extract_embeddings(seq2, format=embedding_format)
                results['embedding_similarity'] = self._calculate_embedding_similarity(emb1, emb2)
                results['embedding_format'] = embedding_format
            
            if comparison_type in ["full", "structure"]:
                struct1 = self.predict_secondary_structure(seq1)
                struct2 = self.predict_secondary_structure(seq2)
                results['structure_similarity'] = self._calculate_structure_similarity(struct1, struct2)
                results['structures'] = [struct1, struct2]
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Sequence comparison failed: {str(e)}")
    
    def predict_contacts(self, sequences: Union[str, List[str]], 
                        threshold: float = 0.5,
                        return_processed: bool = True,
                        allow_noncanonical: bool = True) -> Union[np.ndarray, List[np.ndarray]]:
        """Predict contact maps with optional processing
        
        Args:
            sequences: Input sequences
            threshold: Contact probability threshold
            return_processed: Return processed contact maps (with multiplet handling)
            allow_noncanonical: Allow non-canonical base pairs in processing
            
        Returns:
            Contact maps (raw or processed)
        """
        try:
            if isinstance(sequences, str):
                sequences = [sequences]
            
            results = self.model.predict(
                sequences,
                return_embeddings=False,
                return_contacts=True,
                return_attention=False
            )
            
            contact_maps = []
            for i, seq in enumerate(sequences):
                contact_map = results['contacts'][i]
                
                if return_processed:
                    processed_map = self.model._get_processed_contact_matrix(
                        contact_map, seq, threshold, allow_noncanonical
                    )
                    contact_maps.append(processed_map)
                else:
                    contact_maps.append(contact_map)
            
            if len(contact_maps) == 1:
                return contact_maps[0]
            else:
                return contact_maps
                
        except Exception as e:
            raise PredictionError(f"Contact prediction failed: {str(e)}")
    
    def analyze_structure_details(self, sequence: str, 
                                 threshold: float = 0.5,
                                 advanced_postprocess: bool = True,
                                 allow_noncanonical: bool = True) -> Dict[str, Any]:
        """Detailed structure analysis with multiplet information
        
        Args:
            sequence: RNA sequence
            threshold: Contact threshold
            advanced_postprocess: Use advanced postprocessing
            allow_noncanonical: Allow non-canonical pairs
            
        Returns:
            Detailed structure analysis results
        """
        try:
            results = self.model.predict(
                sequence,
                return_embeddings=False,
                return_contacts=True,
                return_attention=False
            )
            
            contact_map = results['contacts'][0]
            
            # Get both processed and unprocessed structures
            basic_structure = self.model._postprocess_contacts(contact_map, threshold)
            
            if advanced_postprocess:
                advanced_structure = self.model._advanced_postprocess_contacts(
                    contact_map, sequence, threshold, allow_noncanonical
                )
            else:
                advanced_structure = basic_structure
            
            # Count multiplets by comparing processed vs unprocessed
            basic_pairs = self._count_base_pairs(basic_structure)
            advanced_pairs = self._count_base_pairs(advanced_structure)
            
            return {
                'sequence': sequence,
                'sequence_length': len(sequence),
                'basic_structure': basic_structure,
                'advanced_structure': advanced_structure,
                'basic_structure_info': self._analyze_structure(basic_structure),
                'advanced_structure_info': self._analyze_structure(advanced_structure),
                'multiplets_removed': basic_pairs - advanced_pairs,
                'contact_map_stats': {
                    'max_contact': float(np.max(contact_map)),
                    'mean_contact': float(np.mean(contact_map)),
                    'contacts_above_threshold': int(np.sum(contact_map > threshold))
                }
            }
            
        except Exception as e:
            raise PredictionError(f"Structure analysis failed: {str(e)}")
    
    def validate_input(self, input_data: str) -> bool:
        """validate input data"""
        if not isinstance(input_data, str) or not input_data:
            return False

        valid_nucleotides = set('AUCG')
        return all(c.upper() in valid_nucleotides for c in input_data)
    
    def _count_base_pairs(self, structure: str) -> int:
        """Count number of base pairs in dot-bracket notation"""
        return structure.count('(')
    
    def _analyze_structure(self, structure: str) -> Dict[str, Any]:
        """analyze structure"""
        return {
            'length': len(structure),
            'paired_bases': structure.count('(') + structure.count(')'),
            'unpaired_bases': structure.count('.'),
            'pairing_ratio': (structure.count('(') + structure.count(')')) / len(structure),
            'stem_count': self._count_stems(structure)
        }
    
    def _count_stems(self, structure: str) -> int:
        """Count number of stems in dot-bracket notation"""
        stem_count = 0
        in_stem = False
        
        for char in structure:
            if char == '(' and not in_stem:
                stem_count += 1
                in_stem = True
            elif char == '.' and in_stem:
                in_stem = False
        
        return stem_count
    
    def _calculate_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate embedding similarity using cosine similarity"""
        # Handle different embedding formats
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
