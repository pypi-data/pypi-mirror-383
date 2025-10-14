from typing import Dict, Any, List, Optional, Union
import os
import logging

from ..core.exceptions import ModelNotFoundError, PredictionError
from ..core.factory import ModelFactory
from ..utils.file_utils import save_ct_file, process_sequence_input


class StructurePredictionInterface:
    def __init__(self, model_factory: ModelFactory, loaded_models: Dict[str, Any] = None):
        self.factory = model_factory
        self.loaded_models = loaded_models or {}
        self.logger = logging.getLogger(__name__)

    def update_loaded_models(self, loaded_models: Dict[str, Any]):
        self.loaded_models = loaded_models

    def predict_2d_structure(self, sequences: Union[str, List[str]],
                             model: str = "rna-fm",
                             threshold: float = 0.5,
                             save_dir: Optional[str] = None,
                             **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Predict 2D structure of RNA sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name
            threshold: Contact prediction threshold
            save_dir: File path to save results (CT format for single sequence)
            **kwargs: Additional parameters
            
        Returns:
            Structure prediction results - single dict or list of dicts
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            predictor_model = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
            
            structure_predictions = predictor_model.predict_secondary_structure(sequence_list, threshold=threshold)
            
            results_list = []
            for i, (seq_id, sequence, structure) in enumerate(zip(sequence_ids, sequence_list, structure_predictions)):
                # Get contact predictions
                result = predictor_model.predict(
                    sequence,
                    return_embeddings=False,
                    return_contacts=True,
                    return_attention=False
                )
                
                # Save to file if needed
                if save_dir:
                    os.makedirs(save_dir, exist_ok=True)
                    if is_single_input:
                        save_path = save_dir if save_dir.endswith('.ct') else os.path.join(save_dir, f"{seq_id}.ct")
                        save_ct_file(save_path, sequence, structure=structure)
                    else:
                        # Save every sequence to separate file
                        save_path = os.path.join(save_dir, f"{seq_id}.ct")
                        save_ct_file(save_path, sequence, structure=structure)

                
                results_list.append({
                    'sequence': sequence,
                    'sequence_id': seq_id,
                    'secondary_structure': structure,
                    'contacts': result.get('contacts'),
                    'model_used': model,
                    'threshold': threshold
                })
            
            return results_list[0] if is_single_input else results_list

        except Exception as e:
            raise PredictionError(f"2D structure prediction failed: {str(e)}")

    def predict_3d_structure(self, sequences: Union[str, List[str]],
                             msa_file: Optional[str] = None,
                             model: str = "rhofold",
                             save_dir: Optional[str] = None,
                             **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Predict 3D structure using RhoFold or other 3D prediction models
        
        Args:
            sequences: RNA sequences or FASTA file path
            msa_file: Multiple sequence alignment file
            model: Model name (default: rhofold)
            save_dir: Output directory for structure files
            **kwargs: Additional parameters
            
        Returns:
            3D structure prediction results
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")
            
            model_instance = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            from ..utils.file_utils import process_sequence_input
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
            
            # For list input, check if only one sequence in the list
            if isinstance(sequences, list) and len(sequences) == 1:
                is_single_input = True
            
            results_list = []
            for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
                try:
                    # Prepare input data
                    input_data = {
                        'sequence': sequence,
                        'id': seq_id
                    }
                    
                    # Create output directory for this sequence if base dir provided
                    if save_dir:
                        # For single input, use save_dir directly; for multiple inputs, use subdirectories
                        if is_single_input:
                            seq_output_dir = save_dir
                        else:
                            seq_output_dir = os.path.join(save_dir, seq_id)
                        # Ensure directory exists
                        os.makedirs(seq_output_dir, exist_ok=True)
                    else:
                        seq_output_dir = None
                    
                    # Predict 3D structure
                    if hasattr(model_instance, 'predict'):
                        result = model_instance.predict(
                            input_data=input_data,
                            msa_file=msa_file,
                            output_dir=seq_output_dir,
                            **kwargs
                        )
                    else:
                        # Fallback for models without direct predict method
                        raise NotImplementedError(f"3D prediction not implemented for model {model}")
                    
                    # Ensure consistent result format
                    if not isinstance(result, dict):
                        result = {'error': 'Invalid result format'}
                    
                    result.update({
                        'model_used': model,
                        'prediction_type': '3d_structure',
                        'sequence_id': seq_id,
                        'sequence': sequence
                    })
                    
                    results_list.append(result)
                    
                except Exception as e:
                    self.logger.error(f"Failed to predict 3D structure for {seq_id}: {str(e)}")
                    results_list.append({
                        'sequence': sequence,
                        'sequence_id': seq_id,
                        'error': str(e),
                        'failed': True,
                        'model_used': model,
                        'prediction_type': '3d_structure'
                    })
            
            # For backward compatibility with existing demos:
            # If multiple sequences, return aggregated result with all structures
            if is_single_input:
                return results_list[0]
            else:
                # Return aggregated result for multiple sequences
                aggregated_result = {
                    'model_used': model,
                    'prediction_type': '3d_structure',
                    'num_sequences': len(results_list),
                    'results': results_list,
                    'save_dir': save_dir
                }
                
                # If all sequences succeeded, aggregate their outputs
                if all('failed' not in result or not result.get('failed', False) for result in results_list):
                    # Use the first sequence's results as the base for backward compatibility
                    first_result = results_list[0]
                    for key in ['structure_3d_refined', 'structure_3d_unrelaxed', 'secondary_structure', 'average_confidence']:
                        if key in first_result:
                            aggregated_result[key] = first_result[key]
                    
                    # Add information about other sequences
                    if len(results_list) > 1:
                        aggregated_result['additional_structures'] = [
                            {
                                'sequence_id': result['sequence_id'],
                                'structure_3d_refined': result.get('structure_3d_refined'),
                                'structure_3d_unrelaxed': result.get('structure_3d_unrelaxed'),
                                'secondary_structure': result.get('secondary_structure'),
                                'average_confidence': result.get('average_confidence')
                            }
                            for result in results_list[1:]
                        ]
                
                return aggregated_result
            
        except Exception as e:
            raise PredictionError(f"3D structure prediction failed: {str(e)}")

    def predict_structure(self, sequences: Union[str, List[str]],
                          structure_type: str = "2d",
                          model: str = "rna-fm",
                          **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Predict structure for sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            structure_type: "2d" or "3d"
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Prediction results
        """
        if structure_type == "2d":
            return self.predict_2d_structure(sequences, model, **kwargs)
        elif structure_type == "3d":
            return self.predict_3d_structure(sequences, model=model, **kwargs)
        else:
            raise ValueError(f"Unsupported structure type: {structure_type}")

    def batch_predict_structure(self, sequences: Union[str, List[str]],
                                structure_type: str = "2d",
                                model: str = "rna-fm",
                                **kwargs) -> List[Dict[str, Any]]:
        """Batch predict structures for multiple sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            structure_type: "2d" or "3d"
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        # Process input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        
        results = []
        for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
            try:
                if structure_type == "2d":
                    result = self.predict_2d_structure(sequence, model, **kwargs)
                elif structure_type == "3d":
                    result = self.predict_3d_structure(sequence, model=model, **kwargs)
                else:
                    raise ValueError(f"Unsupported structure type: {structure_type}")

                # Ensure result is a dict (not list)
                if isinstance(result, list):
                    result = result[0]
                    
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

    def compare_structures(self, structure1: str, structure2: str) -> Dict[str, Any]:
        """Compare two RNA secondary structures
        
        Args:
            structure1: First structure in dot-bracket notation
            structure2: Second structure in dot-bracket notation
            
        Returns:
            Comparison results including similarity score and matches
        """
        if len(structure1) != len(structure2):
            min_len = min(len(structure1), len(structure2))
            matches = sum(1 for i in range(min_len) if structure1[i] == structure2[i])
            similarity = matches / max(len(structure1), len(structure2))
        else:
            matches = sum(1 for i in range(len(structure1)) if structure1[i] == structure2[i])
            similarity = matches / len(structure1)

        return {
            'structure1': structure1,
            'structure2': structure2,
            'lengths': [len(structure1), len(structure2)],
            'similarity': similarity,
            'matches': matches if len(structure1) == len(structure2) else sum(
                1 for i in range(min(len(structure1), len(structure2))) if structure1[i] == structure2[i])
        }
