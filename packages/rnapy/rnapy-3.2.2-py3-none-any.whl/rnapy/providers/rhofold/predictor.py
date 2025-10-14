import os
from typing import Dict, Any, List, Union, Optional
from pathlib import Path
import numpy as np

from ...core.base import BasePredictor
from ...core.exceptions import PredictionError, InvalidSequenceError
from .adapter import RhoFoldAdapter


class RhoFoldPredictor(BasePredictor):
    """High-level predictor interface for RhoFold"""
    
    def __init__(self, model: RhoFoldAdapter):
        super().__init__(model)
        self.adapter = model
    
    def predict_single(self, input_data: Union[str, Dict[str, Any]], 
                      output_dir: Optional[str] = None,
                      msa_file: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """Predict 3D structure for a single RNA sequence
        
        Args:
            input_data: RNA sequence string or dictionary
            output_dir: Output directory for results
            msa_file: Optional MSA file path
            **kwargs: Additional parameters
            
        Returns:
            Prediction results dictionary
        """
        try:
            return self.adapter.predict(
                input_data=input_data,
                msa_file=msa_file,
                output_dir=output_dir,
                **kwargs
            )
        except Exception as e:
            raise PredictionError(f"Single sequence prediction failed: {str(e)}")
    
    def predict_batch(self, input_batch: List[Union[str, Dict[str, Any]]],
                     output_base_dir: Optional[str] = None,
                     **kwargs) -> List[Dict[str, Any]]:
        """Predict 3D structures for multiple RNA sequences
        
        Args:
            input_batch: List of RNA sequences or dictionaries
            output_base_dir: Base directory for outputs
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, input_data in enumerate(input_batch):
            try:
                # Create individual output directory
                if output_base_dir:
                    if isinstance(input_data, dict) and 'id' in input_data:
                        seq_id = input_data['id']
                    else:
                        seq_id = f"seq_{i}"
                    output_dir = os.path.join(output_base_dir, seq_id)
                else:
                    output_dir = None
                
                result = self.predict_single(
                    input_data=input_data,
                    output_dir=output_dir,
                    **kwargs
                )
                result['batch_index'] = i
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to predict structure for batch item {i}: {str(e)}")
                results.append({
                    'batch_index': i,
                    'error': str(e),
                    'failed': True,
                    'sequence': str(input_data) if isinstance(input_data, str) else input_data.get('sequence', 'unknown')
                })
        
        return results
    
    def predict_from_fasta(self, fasta_file: str,
                          output_base_dir: Optional[str] = None,
                          **kwargs) -> List[Dict[str, Any]]:
        """Predict 3D structures from FASTA file
        
        Args:
            fasta_file: Path to FASTA file
            output_base_dir: Base directory for outputs
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        try:
            sequences = self._parse_fasta_file(fasta_file)
            return self.predict_batch(
                input_batch=sequences,
                output_base_dir=output_base_dir,
                **kwargs
            )
        except Exception as e:
            raise PredictionError(f"FASTA prediction failed: {str(e)}")
    
    def predict_with_msa_generation(self, sequence: str,
                                  output_dir: Optional[str] = None,
                                  database_path: Optional[str] = None,
                                  **kwargs) -> Dict[str, Any]:
        """Predict structure with automatic MSA generation
        
        Args:
            sequence: RNA sequence
            output_dir: Output directory
            database_path: Path to sequence databases
            **kwargs: Additional parameters
            
        Returns:
            Prediction results
        """
        # Temporarily update config for MSA generation
        old_config = self.adapter.config.copy()
        
        try:
            if database_path:
                self.adapter.config['database_path'] = Path(database_path)
                self.adapter.config['use_msa'] = True
                self.adapter.config['single_seq_pred'] = False
            
            result = self.predict_single(
                input_data=sequence,
                output_dir=output_dir,
                **kwargs
            )
            
            return result
            
        finally:
            # Restore original config
            self.adapter.config = old_config
    
    def predict_structure_only(self, sequence: str,
                             output_dir: Optional[str] = None,
                             **kwargs) -> str:
        """Predict structure and return only the main structure file path
        
        Args:
            sequence: RNA sequence
            output_dir: Output directory
            **kwargs: Additional parameters
            
        Returns:
            Path to the predicted structure file
        """
        result = self.predict_single(
            input_data=sequence,
            output_dir=output_dir,
            **kwargs
        )
        
        # Return best available structure file
        if 'structure_3d_refined' in result:
            return result['structure_3d_refined']
        elif 'structure_3d_unrelaxed' in result:
            return result['structure_3d_unrelaxed']
        else:
            raise PredictionError("No structure file found in prediction results")
    
    def predict_with_confidence_filtering(self, sequences: List[str],
                                        min_confidence: float = 0.7,
                                        output_base_dir: Optional[str] = None,
                                        **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """Predict structures with confidence-based filtering
        
        Args:
            sequences: List of RNA sequences
            min_confidence: Minimum confidence threshold
            output_base_dir: Base directory for outputs
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with 'high_confidence' and 'low_confidence' results
        """
        results = self.predict_batch(
            input_batch=sequences,
            output_base_dir=output_base_dir,
            **kwargs
        )
        
        high_confidence = []
        low_confidence = []
        
        for result in results:
            if result.get('failed', False):
                low_confidence.append(result)
                continue
                
            avg_conf = result.get('average_confidence', 0.0)
            if avg_conf >= min_confidence:
                high_confidence.append(result)
            else:
                low_confidence.append(result)
        
        return {
            'high_confidence': high_confidence,
            'low_confidence': low_confidence,
            'threshold': min_confidence
        }
    
    def compare_structures(self, sequence1: str, sequence2: str,
                          output_dir: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """Compare predicted structures of two sequences
        
        Args:
            sequence1: First RNA sequence
            sequence2: Second RNA sequence
            output_dir: Output directory
            **kwargs: Additional parameters
            
        Returns:
            Comparison results
        """
        # Create subdirectories
        if output_dir:
            dir1 = os.path.join(output_dir, "seq1")
            dir2 = os.path.join(output_dir, "seq2")
        else:
            dir1 = dir2 = None
        
        # Predict both structures
        result1 = self.predict_single(sequence1, output_dir=dir1, **kwargs)
        result2 = self.predict_single(sequence2, output_dir=dir2, **kwargs)
        
        # Basic comparison
        comparison = {
            'sequence1': sequence1,
            'sequence2': sequence2,
            'length1': len(sequence1),
            'length2': len(sequence2),
            'confidence1': result1.get('average_confidence', 0.0),
            'confidence2': result2.get('average_confidence', 0.0),
            'structure_file1': result1.get('structure_3d_refined', result1.get('structure_3d_unrelaxed')),
            'structure_file2': result2.get('structure_3d_refined', result2.get('structure_3d_unrelaxed')),
            'results': [result1, result2]
        }
        
        # Sequence similarity
        comparison['sequence_similarity'] = self._calculate_sequence_similarity(sequence1, sequence2)
        
        # Secondary structure comparison if available
        if 'secondary_structure' in result1 and 'secondary_structure' in result2:
            comparison['structure_similarity'] = self._calculate_structure_similarity(
                result1['secondary_structure'], result2['secondary_structure']
            )
        
        return comparison
    
    def validate_input(self, input_data: Union[str, Dict[str, Any]]) -> bool:
        """Validate input data
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if isinstance(input_data, str):
                sequence = input_data
            elif isinstance(input_data, dict):
                sequence = input_data.get('sequence', input_data.get('seq', ''))
            else:
                return False
            
            # Check if sequence is valid RNA
            valid_nucleotides = set('AUCG')
            if not sequence or not all(c.upper() in valid_nucleotides for c in sequence):
                return False
            
            # Check length constraints
            max_len = self.adapter.config.get('max_sequence_length', 1000)
            if len(sequence) > max_len:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_prediction_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for batch predictions
        
        Args:
            results: List of prediction results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        total = len(results)
        successful = sum(1 for r in results if not r.get('failed', False))
        failed = total - successful
        
        summary = {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0.0
        }
        
        # Confidence statistics for successful predictions
        successful_results = [r for r in results if not r.get('failed', False)]
        if successful_results:
            confidences = [r.get('average_confidence', 0.0) for r in successful_results]
            summary.update({
                'mean_confidence': np.mean(confidences),
                'min_confidence': np.min(confidences),
                'max_confidence': np.max(confidences),
                'std_confidence': np.std(confidences)
            })
            
            # Length statistics
            lengths = [r.get('sequence_length', len(r.get('sequence', ''))) for r in successful_results]
            summary.update({
                'mean_length': np.mean(lengths),
                'min_length': np.min(lengths),
                'max_length': np.max(lengths)
            })
        
        return summary
    
    def _parse_fasta_file(self, fasta_file: str) -> List[Dict[str, str]]:
        """Parse FASTA file into sequence list"""
        sequences = []
        
        with open(fasta_file, 'r') as f:
            current_id = None
            current_seq = []
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # Save previous sequence
                    if current_id is not None and current_seq:
                        sequences.append({
                            'id': current_id,
                            'sequence': ''.join(current_seq)
                        })
                    
                    # Start new sequence
                    current_id = line[1:].split()[0]  # Take first word after '>'
                    current_seq = []
                else:
                    current_seq.append(line.upper())
            
            # Save last sequence
            if current_id is not None and current_seq:
                sequences.append({
                    'id': current_id,
                    'sequence': ''.join(current_seq)
                })
        
        return sequences
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence similarity between two sequences"""
        if not seq1 or not seq2:
            return 0.0
        
        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i].upper() == seq2[i].upper())
        
        return matches / max(len(seq1), len(seq2))
    
    def _calculate_structure_similarity(self, struct1: str, struct2: str) -> float:
        """Calculate structure similarity between two dot-bracket structures"""
        if len(struct1) != len(struct2):
            min_len = min(len(struct1), len(struct2))
            matches = sum(1 for i in range(min_len) if struct1[i] == struct2[i])
            return matches / max(len(struct1), len(struct2))
        else:
            matches = sum(1 for i in range(len(struct1)) if struct1[i] == struct2[i])
            return matches / len(struct1) 