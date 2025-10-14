from typing import Dict, Any, List, Optional, Union
import os
from pathlib import Path

from ..core.exceptions import ModelNotFoundError, PredictionError
from ..core.factory import ModelFactory


class InverseFoldingInterface:
    """Interface for RNA inverse folding - generating sequences from 3D structures"""
    
    def __init__(self, model_factory: ModelFactory, loaded_models: Dict[str, Any] = None):
        self.factory = model_factory
        self.loaded_models = loaded_models or {}

    def update_loaded_models(self, loaded_models: Dict[str, Any]):
        self.loaded_models = loaded_models

    def generate_sequences(self, structure_file: str,
                          model: str = "ribodiffusion",
                          n_samples: int = 1,
                          output_dir: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """Generate RNA sequences from 3D structure
        
        Args:
            structure_file: Path to PDB structure file
            model: Model name for inverse folding
            n_samples: Number of sequences to generate
            output_dir: Output directory for results
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing generated sequences and metadata
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Validate input
            structure_path = Path(structure_file)
            if not structure_path.exists():
                raise FileNotFoundError(f"Structure file not found: {structure_file}")
            
            if not structure_path.suffix.lower() == '.pdb':
                raise ValueError("Only PDB format is currently supported for structure files")
            
            # Generate sequences
            results = model_instance.predict(
                input_data=str(structure_path),
                output_dir=output_dir,
                n_samples=n_samples,
                **kwargs
            )
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Inverse folding failed: {str(e)}")

    def batch_generate_sequences(self, structure_files: Union[List[str], str],
                                model: str = "ribodiffusion",
                                n_samples: int = 1,
                                output_base_dir: Optional[str] = None,
                                **kwargs) -> List[Dict[str, Any]]:
        """Generate sequences for multiple structures
        
        Args:
            structure_files: List of PDB files or directory containing PDB files
            model: Model name for inverse folding
            n_samples: Number of sequences to generate per structure
            output_base_dir: Base output directory
            **kwargs: Additional parameters
            
        Returns:
            List of results for each structure
        """
        try:
            if isinstance(structure_files, str):
                # If it's a directory, get all PDB files
                path = Path(structure_files)
                if path.is_dir():
                    structure_files = list(path.glob("*.pdb"))
                else:
                    structure_files = [structure_files]
            
            results = []
            for i, structure_file in enumerate(structure_files):
                try:
                    # Create individual output directory
                    if output_base_dir:
                        structure_name = Path(structure_file).stem
                        output_dir = os.path.join(output_base_dir, structure_name)
                    else:
                        output_dir = None
                    
                    result = self.generate_sequences(
                        structure_file=str(structure_file),
                        model=model,
                        n_samples=n_samples,
                        output_dir=output_dir,
                        **kwargs
                    )
                    
                    result['structure_index'] = i
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        'structure_index': i,
                        'structure_file': str(structure_file),
                        'error': str(e),
                        'failed': True,
                        'model_used': model
                    })
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Batch inverse folding failed: {str(e)}")

    def analyze_generated_sequences(self, generation_results: Dict[str, Any],
                                   include_structure_analysis: bool = True) -> Dict[str, Any]:
        """Analyze properties of generated sequences
        
        Args:
            generation_results: Results from generate_sequences
            include_structure_analysis: Whether to predict secondary structure
            
        Returns:
            Analysis results
        """
        try:
            sequences = generation_results.get('generated_sequences', [])
            if not sequences:
                return {'error': 'No sequences to analyze'}
            
            analysis = {
                'sequence_count': len(sequences),
                'sequences': sequences,
                'structure_file': generation_results.get('pdb_file', ''),
                'model_used': generation_results.get('model_type', 'unknown')
            }
            
            # Basic sequence statistics
            lengths = [len(seq) for seq in sequences]
            all_seqs = ''.join(sequences)
            total_bases = len(all_seqs)
            
            analysis['sequence_statistics'] = {
                'lengths': lengths,
                'average_length': sum(lengths) / len(lengths),
                'min_length': min(lengths),
                'max_length': max(lengths),
                'unique_sequences': len(set(sequences)),
                'diversity_ratio': len(set(sequences)) / len(sequences) if sequences else 0
            }
            
            # Nucleotide composition
            if total_bases > 0:
                analysis['composition'] = {
                    'A': all_seqs.count('A') / total_bases,
                    'U': all_seqs.count('U') / total_bases,
                    'G': all_seqs.count('G') / total_bases,
                    'C': all_seqs.count('C') / total_bases,
                    'GC_content': (all_seqs.count('G') + all_seqs.count('C')) / total_bases,
                    'purine_content': (all_seqs.count('A') + all_seqs.count('G')) / total_bases,
                    'pyrimidine_content': (all_seqs.count('C') + all_seqs.count('U')) / total_bases
                }
            
            # Quality metrics from generation
            if 'quality_metrics' in generation_results:
                analysis['quality_metrics'] = generation_results['quality_metrics']
            
            # Structure analysis if requested and RNA-FM is available
            if include_structure_analysis and 'rna-fm' in self.loaded_models:
                try:
                    rna_fm_model = self.loaded_models['rna-fm']
                    predicted_structures = rna_fm_model.predict_secondary_structure(sequences)
                    
                    analysis['predicted_structures'] = predicted_structures
                    analysis['structure_metrics'] = self._analyze_predicted_structures(predicted_structures)
                    
                except Exception as e:
                    analysis['structure_analysis_error'] = str(e)
            
            return analysis
            
        except Exception as e:
            raise PredictionError(f"Sequence analysis failed: {str(e)}")

    def _analyze_predicted_structures(self, structures: List[str]) -> Dict[str, Any]:
        """Analyze predicted secondary structures"""
        if not structures:
            return {}
        
        total_positions = sum(len(struct) for struct in structures)
        all_structures = ''.join(structures)
        
        paired_count = all_structures.count('(') + all_structures.count(')')
        unpaired_count = all_structures.count('.')
        
        stem_counts = []
        for struct in structures:
            stem_count = 0
            in_stem = False
            for char in struct:
                if char == '(' and not in_stem:
                    stem_count += 1
                    in_stem = True
                elif char == '.' and in_stem:
                    in_stem = False
            stem_counts.append(stem_count)
        
        return {
            'average_pairing_ratio': paired_count / total_positions if total_positions > 0 else 0,
            'average_stem_count': sum(stem_counts) / len(stem_counts) if stem_counts else 0,
            'structure_diversity': len(set(structures)) / len(structures) if structures else 0,
            'paired_positions': paired_count,
            'unpaired_positions': unpaired_count
        }

    def compare_with_native_sequence(self, generation_results: Dict[str, Any],
                                   native_sequence: Optional[str] = None) -> Dict[str, Any]:
        """Compare generated sequences with native sequence if available
        
        Args:
            generation_results: Results from generate_sequences
            native_sequence: Native sequence for comparison (if available)
            
        Returns:
            Comparison results
        """
        try:
            generated_sequences = generation_results.get('generated_sequences', [])
            if not generated_sequences:
                return {'error': 'No generated sequences to compare'}
            
            comparison = {
                'generated_count': len(generated_sequences),
                'native_sequence': native_sequence,
                'has_native': native_sequence is not None
            }
            
            if native_sequence:
                similarities = []
                for seq in generated_sequences:
                    # Simple sequence similarity
                    min_len = min(len(seq), len(native_sequence))
                    matches = sum(1 for i in range(min_len) 
                                if seq[i].upper() == native_sequence[i].upper())
                    similarity = matches / max(len(seq), len(native_sequence))
                    similarities.append(similarity)
                
                comparison['sequence_similarities'] = similarities
                comparison['average_similarity'] = sum(similarities) / len(similarities)
                comparison['best_similarity'] = max(similarities)
                comparison['worst_similarity'] = min(similarities)
                
                # Find most similar sequence
                best_idx = similarities.index(max(similarities))
                comparison['most_similar_sequence'] = {
                    'index': best_idx,
                    'sequence': generated_sequences[best_idx],
                    'similarity': similarities[best_idx]
                }
            
            # Recovery rate from generation results
            if 'quality_metrics' in generation_results:
                quality_metrics = generation_results['quality_metrics']
                if 'recovery_rates' in quality_metrics:
                    comparison['recovery_rates'] = quality_metrics['recovery_rates']
                    comparison['average_recovery_rate'] = quality_metrics.get('average_recovery_rate', 0)
            
            return comparison
            
        except Exception as e:
            raise PredictionError(f"Sequence comparison failed: {str(e)}")

    def save_results(self, results: Dict[str, Any], 
                    output_file: str,
                    format: str = "json") -> str:
        """Save generation results to file
        
        Args:
            results: Results from generate_sequences or batch_generate_sequences
            output_file: Output file path
            format: Output format ("json", "csv", "tsv")
            
        Returns:
            Path to saved file
        """
        try:
            import json
            import pandas as pd
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            
            elif format.lower() in ["csv", "tsv"]:
                # Flatten results for tabular format
                if 'generated_sequences' in results:
                    # Single generation result
                    rows = []
                    for i, seq in enumerate(results['generated_sequences']):
                        row = {
                            'sequence_index': i,
                            'sequence': seq,
                            'length': len(seq),
                            'pdb_file': results.get('pdb_file', ''),
                            'model_type': results.get('model_type', ''),
                        }
                        
                        # Add recovery rate if available
                        if 'quality_metrics' in results and 'recovery_rates' in results['quality_metrics']:
                            if i < len(results['quality_metrics']['recovery_rates']):
                                row['recovery_rate'] = results['quality_metrics']['recovery_rates'][i]
                        
                        rows.append(row)
                    
                    df = pd.DataFrame(rows)
                else:
                    # Batch results or other format
                    df = pd.DataFrame([results])
                
                separator = '\t' if format.lower() == "tsv" else ','
                df.to_csv(output_path, sep=separator, index=False)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return str(output_path)
            
        except Exception as e:
            raise PredictionError(f"Failed to save results: {str(e)}")

    def get_supported_models(self) -> List[str]:
        """Get list of supported inverse folding models"""
        supported_models = []
        for model_name, model_instance in self.loaded_models.items():
            model_info = model_instance.get_model_info()
            if model_info.get('task_type') == 'inverse_folding':
                supported_models.append(model_name)
        return supported_models 