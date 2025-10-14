"""RNA-FM Model Adapter"""

import os
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

import numpy as np
import torch

from . import pretrained
from .data import BatchConverter
from .config import RnaFmConfig
from ...core.base import BaseModel
from ...core.exceptions import ModelLoadError, PredictionError, InvalidSequenceError


class RNAFMAdapter(BaseModel):
    def __init__(self, config: Union[RnaFmConfig, Dict[str, Any]], device: str = "cpu"):
        super().__init__(config, device)
        # Handle both RnaFmConfig object and dict for backward compatibility
        if isinstance(config, RnaFmConfig):
            self.model_type = config.model_type
        else:
            self.model_type = config.get('model_type', 'RNA-FM')  # RNA-FM or mRNA-FM
        # Normalize model_type to avoid theme mismatch (e.g., 'rna_fm' vs 'RNA-FM')
        self.model_type = str(self.model_type).replace('-', '_').lower()
        self.alphabet = None
        self.batch_converter = None
        self._is_loaded = False
        
    def load_model(self, checkpoint_path: str) -> None:
        try:
            checkpoint_path = Path(checkpoint_path)
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
            
            # Decide theme based on normalized model_type
            # rna_fm -> 'rna' tokens; mrna_fm -> 'rna-3mer' tokens
            if self.model_type in {"rna_fm", "rna", "rnafm"}:
                theme = "rna"
                pretty_model = "RNA-FM"
            elif self.model_type in {"mrna_fm", "mrna", "mrnafm"}:
                theme = "rna-3mer"
                pretty_model = "mRNA-FM"
            else:
                # default to RNA-FM
                theme = "rna"
                pretty_model = str(self.model_type)

            self.logger.info(f"Loading {pretty_model} model from {checkpoint_path}")

            # Load model with resolved theme
            self.model, self.alphabet = pretrained.load_model_and_alphabet_local(str(checkpoint_path), theme=theme)
            self.batch_converter = BatchConverter(self.alphabet)
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self._is_loaded = True
            self.logger.info(f"Successfully loaded {pretty_model} model")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {str(e)}")
    
    def preprocess(self, raw_input: Union[str, List[str]]) -> torch.Tensor:
        if not self._is_loaded:
            raise ModelLoadError("Model not loaded. Call load_model() first.")

        if isinstance(raw_input, str):
            sequences = [("seq_0", raw_input)]
        elif isinstance(raw_input, list):
            sequences = [(f"seq_{i}", seq) for i, seq in enumerate(raw_input)]
        else:
            raise InvalidSequenceError("Input must be a string or list of strings")

        for name, seq in sequences:
            if not self._validate_sequence(seq):
                raise InvalidSequenceError(f"Invalid RNA sequence: {seq}")
        
        # Convert to tokens
        labels, strs, tokens = self.batch_converter(sequences)
        tokens = tokens.to(self.device)
        
        return tokens
    
    def predict(self, input_data: Union[str, List[str]], 
               return_embeddings: bool = True,
               return_contacts: bool = True,
               return_attention: bool = False) -> Dict[str, Any]:
        try:
            if not self._is_loaded:
                raise ModelLoadError("Model not loaded. Call load_model() first.")
            
            # Preprocess
            tokens = self.preprocess(input_data)
            
            # Get repr_layer from config
            if isinstance(self.config, RnaFmConfig):
                repr_layer = self.config.num_layers  # Use num_layers as default repr_layer
            else:
                repr_layer = self.config.get('repr_layer', 12)

            # Inference
            with torch.no_grad():
                results = self.model(
                    tokens,
                    repr_layers=[repr_layer],
                    return_contacts=return_contacts,
                    need_head_weights=return_attention
                )
            
            # Postprocess
            return self.postprocess(results, input_data, return_embeddings, return_contacts, return_attention)
            
        except Exception as e:
            raise PredictionError(f"Prediction failed: {str(e)}")
    
    def postprocess(self, raw_output: Dict[str, Any], 
                   original_input: Union[str, List[str]],
                   return_embeddings: bool = True,
                   return_contacts: bool = True,
                   return_attention: bool = False) -> Dict[str, Any]:
        processed_results = {}

        # Extract embeddings
        if return_embeddings and 'representations' in raw_output:
            # Get repr_layer from config
            if isinstance(self.config, RnaFmConfig):
                repr_layer = self.config.num_layers  # Use num_layers as default repr_layer
            else:
                repr_layer = self.config.get('repr_layer', 12)

            representations = raw_output['representations']
            if repr_layer in representations:
                embeddings = representations[repr_layer]
                embeddings = embeddings[:, 1:-1, :]  # Remove special tokens [batch, seq_len, hidden_dim]
                processed_results['embeddings'] = embeddings.cpu().numpy()
        
        # Extract contact maps and predict secondary structure
        if return_contacts and 'contacts' in raw_output:
            contacts = raw_output['contacts']
            # Remove special tokens
            contacts = contacts[:, 1:-1, 1:-1]  # [batch, seq_len, seq_len]
            processed_results['contacts'] = contacts.cpu().numpy()
            
            # Predict secondary structure from contacts
            if isinstance(self.config, RnaFmConfig):
                threshold = 0.5  # Default threshold since it's not in RnaFmConfig
            else:
                threshold = self.config.get('threshold', 0.5)
            predicted_structure = self._contacts_to_structure(contacts, threshold)
            processed_results['secondary_structure'] = predicted_structure
        
        # Extract attention weights
        if return_attention and 'attentions' in raw_output:
            attentions = raw_output['attentions']
            processed_results['attention_weights'] = attentions.cpu().numpy()

        # Include original sequences
        if isinstance(original_input, str):
            processed_results['sequences'] = [original_input]
        else:
            processed_results['sequences'] = original_input
        
        return processed_results
    
    def extract_embeddings(self, sequences: Union[str, List[str]], 
                          layer: int = 12,
                          format: str = "raw") -> np.ndarray:
        """Extract embeddings with different formats
        
        Args:
            sequences: Input sequences
            layer: Layer to extract from
            format: Format type - "raw", "mean", "bos"
        """
        # Store old layer value and set new one
        if isinstance(self.config, RnaFmConfig):
            old_layer = self.config.num_layers
            # For RnaFmConfig, we can't dynamically change it, so just use the layer parameter
            pass
        else:
            old_layer = self.config.get('repr_layer', 12)
            self.config['repr_layer'] = layer

        results = self.predict(
            sequences, 
            return_embeddings=True, 
            return_contacts=False, 
            return_attention=False
        )
        
        # Restore old layer value
        if not isinstance(self.config, RnaFmConfig):
            self.config['repr_layer'] = old_layer

        embeddings = results['embeddings']
        
        # Apply format transformation
        if format == "raw":
            return embeddings
        elif format == "mean":
            return np.array([np.mean(emb, axis=0) for emb in embeddings])
        elif format == "bos":
            # Get BOS token representation (first token after removing special tokens)
            # For BOS we need to get the original representations before removing special tokens
            tokens = self.preprocess(sequences)
            with torch.no_grad():
                results = self.model(
                    tokens,
                    repr_layers=[layer],
                    return_contacts=False,
                    need_head_weights=False
                )
            representations = results['representations'][layer]
            bos_embeddings = representations[:, 0, :].cpu().numpy()  # First token (BOS)
            return bos_embeddings
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'raw', 'mean', or 'bos'")
    
    def predict_secondary_structure(self, sequences: Union[str, List[str]], 
                                  threshold: float = 0.5,
                                  advanced_postprocess: bool = True,
                                  allow_noncanonical: bool = True) -> List[str]:
        """Predict secondary structure with advanced postprocessing options"""
        # Store old threshold value and set new one
        if isinstance(self.config, RnaFmConfig):
            old_threshold = 0.5  # Default since it's not in RnaFmConfig
        else:
            old_threshold = self.config.get('threshold', 0.5)
            self.config['threshold'] = threshold

        results = self.predict(
            sequences,
            return_embeddings=False,
            return_contacts=True,
            return_attention=False
        )
        
        # Restore old threshold value
        if not isinstance(self.config, RnaFmConfig):
            self.config['threshold'] = old_threshold

        if advanced_postprocess:
            # Use advanced postprocessing
            structures = []
            for i, seq in enumerate(results['sequences']):
                contact_map = results['contacts'][i]
                structure = self._advanced_postprocess_contacts(
                    contact_map, seq, threshold, allow_noncanonical
                )
                structures.append(structure)
            return structures
        else:
            return results['secondary_structure']
    
    def _postprocess_contacts_unified(self, contact_map: np.ndarray,
                                      sequence: Optional[str] = None,
                                      threshold: float = 0.5,
                                      check_canonical: bool = False,
                                      allow_noncanonical: bool = True,
                                      return_multiplets: bool = False) -> Any:
        """Unified contact map postprocessing

        Args:
            contact_map: Contact probability matrix
            sequence: RNA sequence
            threshold: Contact probability threshold
            check_canonical: Check for canonical pairs
            allow_noncanonical: Allow non-canonical pairs if check_canonical is True
            return_multiplets: Whether to return multiplet list

        Returns:
            Processed contact map and optional multiplet list
        """
        canonical_pairs = ['AU', 'UA', 'GC', 'CG', 'GU', 'UG'] if check_canonical else None
        seq_len = contact_map.shape[0]

        contact_map = contact_map * (1 - np.eye(seq_len))
        pred_map = (contact_map > threshold)

        x_array, y_array = np.nonzero(pred_map)
        prob_array = np.array([contact_map[x_array[i], y_array[i]] for i in range(x_array.shape[0])])

        sort_index = np.argsort(-prob_array)
        
        mask_map = np.zeros_like(pred_map)
        already_x = set()
        already_y = set()
        multiplet_list = []
        
        for index in sort_index:
            x = x_array[index]
            y = y_array[index]
            
            # No sharp stem-loop (minimum loop size = 1)
            if abs(x - y) <= 1:
                continue

            if check_canonical and sequence and x < len(sequence) and y < len(sequence):
                seq_pair = sequence[x] + sequence[y]
                if seq_pair not in canonical_pairs and not allow_noncanonical:
                    continue

            if x in already_x or y in already_y:
                if return_multiplets:
                    multiplet_list.append([x+1, y+1])  # 1-indexed for output
                continue
            else:
                mask_map[x, y] = 1
                already_x.add(x)
                already_y.add(y)

        # final_map = pred_map * mask_map

        # structure = self._matrix_to_dotbracket(final_map)

        structure = pred_map * mask_map
        if return_multiplets:
            return structure, multiplet_list
        return structure

    def _advanced_postprocess_contacts(self, contact_map: np.ndarray,
                                     sequence: str,
                                     threshold: float = 0.5,
                                     allow_nc: bool = True) -> Any:
        return self._postprocess_contacts_unified(
            contact_map=contact_map,
            sequence=sequence,
            threshold=threshold,
            check_canonical=True,
            allow_noncanonical=allow_nc,
            return_multiplets=False
        )

    def _postprocess_contacts(self, contact_map: np.ndarray, threshold: float) -> Any:
        return self._postprocess_contacts_unified(
            contact_map=contact_map,
            sequence=None,
            threshold=threshold,
            check_canonical=False,
            allow_noncanonical=True,
            return_multiplets=False
        )

    def _matrix_to_dotbracket(self, contact_matrix: np.ndarray) -> str:
        """Convert contact matrix to dot-bracket notation"""
        seq_len = contact_matrix.shape[0]
        structure = ['.'] * seq_len
        
        # Find all base pairs
        pairs = []
        for i in range(seq_len):
            for j in range(i + 1, seq_len):
                if contact_matrix[i, j] > 0:
                    pairs.append((i, j))
        
        # Sort by opening position
        pairs.sort()
        
        # Assign brackets
        for i, j in pairs:
            structure[i] = '('
            structure[j] = ')'
        
        return ''.join(structure)
    
    def save_ct_file(self, sequences: Union[str, List[str]], 
                    output_dir: str,
                    sequence_ids: Optional[List[str]] = None,
                    threshold: float = 0.5,
                    advanced_postprocess: bool = True,
                    allow_noncanonical: bool = True) -> List[str]:
        """Generate and save CT files for secondary structure prediction"""
        if isinstance(sequences, str):
            sequences = [sequences]
        
        if sequence_ids is None:
            sequence_ids = [f"seq_{i}" for i in range(len(sequences))]
        
        if len(sequence_ids) != len(sequences):
            raise ValueError("Number of sequence IDs must match number of sequences")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get contact maps
        results = self.predict(
            sequences,
            return_embeddings=False,
            return_contacts=True,
            return_attention=False
        )
        
        ct_files = []
        for i, (seq, seq_id) in enumerate(zip(sequences, sequence_ids)):
            contact_map = results['contacts'][i]
            
            if advanced_postprocess:
                # Use advanced postprocessing
                processed_map = self._get_processed_contact_matrix(
                    contact_map, seq, threshold, allow_noncanonical
                )
            else:
                # Simple thresholding
                processed_map = (contact_map > threshold).astype(int)
            
            # Generate CT file
            ct_file = self._matrix_to_ct(processed_map, seq, seq_id, output_dir)
            ct_files.append(ct_file)
        
        return ct_files
    
    def _get_processed_contact_matrix(self, contact_map: np.ndarray, 
                                    sequence: str, 
                                    threshold: float = 0.5,
                                    allow_nc: bool = True) -> np.ndarray:
        """Get processed contact matrix with multiplet handling"""
        canonical_pairs = ['AU', 'UA', 'GC', 'CG', 'GU', 'UG']
        
        # Remove diagonal
        contact_map = contact_map * (1 - np.eye(contact_map.shape[0]))
        pred_map = (contact_map > threshold)
        
        # Handle multiplets
        seq_len = len(sequence)
        x_array, y_array = np.nonzero(pred_map)
        prob_array = []
        for i in range(x_array.shape[0]):
            prob_array.append(contact_map[x_array[i], y_array[i]])
        prob_array = np.array(prob_array)
        
        sort_index = np.argsort(-prob_array)
        
        mask_map = np.zeros_like(pred_map)
        already_x = set()
        already_y = set()
        
        for index in sort_index:
            x = x_array[index]
            y = y_array[index]
            
            # No sharp stem-loop
            if abs(x - y) <= 1:
                continue
            
            # Check canonical pairs
            if x < len(sequence) and y < len(sequence):
                seq_pair = sequence[x] + sequence[y]
                if seq_pair not in canonical_pairs and not allow_nc:
                    continue
            
            # Handle conflicts
            if x in already_x or y in already_y:
                continue
            else:
                mask_map[x, y] = 1
                already_x.add(x)
                already_y.add(y)
        
        return pred_map * mask_map
    
    def _matrix_to_ct(self, contact_matrix: np.ndarray,
                     sequence: str, 
                     seq_id: str, 
                     output_dir: str) -> str:
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
        fifth_col = [pair_dict[i] + 1 if pair_dict[i] != -1 else 0 for i in range(seq_len)]  # paired position (1-indexed, 0 for unpaired)
        last_col = list(range(1, seq_len + 1))  # position again
        
        # Write CT file
        ct_file = os.path.join(output_dir, f"{seq_id}.ct")
        
        with open(ct_file, "w") as f:
            f.write(f"{seq_len}\t{seq_id}\n")  # header
            for i in range(seq_len):
                f.write(f"{first_col[i]}\t{second_col[i]}\t{third_col[i]}\t{fourth_col[i]}\t{fifth_col[i]}\t{last_col[i]}\n")
        
        return ct_file
    
    def _validate_sequence(self, sequence: str) -> bool:
        valid_nucleotides = set('AUCG')
        return all(c.upper() in valid_nucleotides for c in sequence)
    
    def _contacts_to_structure(self, contacts: torch.Tensor, threshold: float) -> List[str]:
        batch_size, seq_len, _ = contacts.shape
        structures = []
        
        for b in range(batch_size):
            contact_map = contacts[b].cpu().numpy()
            # Postprocess to dot-bracket notation
            structure = self._postprocess_contacts(contact_map, threshold)
            structures.append(structure)
        
        return structures
    
    def get_model_info(self) -> Dict[str, Any]:
        if not self._is_loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_type": self.model_type,
            "device": str(self.device),
            "num_layers": getattr(self.model.args, 'layers', 'unknown'),
            "embed_dim": getattr(self.model.args, 'embed_dim', 'unknown'),
            "attention_heads": getattr(self.model.args, 'attention_heads', 'unknown'),
            "alphabet_size": len(self.alphabet) if self.alphabet else 0
        }
