"""RhoDesign Adapter for RNA Inverse Folding"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Union, Optional

import numpy as np
import torch

# Import RhoDesign components
from .RhoDesign import RhoDesignModel
from .RhoDesign_without2d import RhoDesignModel as RhoDesignModelWithout2D
from .alphabet import Alphabet
from .config import RhoDesignConfig, get_rhodesign_config
from .util import load_structure, extract_coords_from_structure, seq_rec_rate
from ...core.base import BaseModel
from ...core.exceptions import ModelLoadError, PredictionError, InvalidSequenceError


class RhoDesignArgs:
    """Argument class for RhoDesign model following original pattern"""
    
    def __init__(self, config: Union[RhoDesignConfig, Dict[str, Any]]):
        if isinstance(config, RhoDesignConfig):
            self.encoder_embed_dim = config.encoder_embed_dim
            self.decoder_embed_dim = config.decoder_embed_dim
            self.dropout = config.dropout
            self.gvp_top_k_neighbors = config.gvp_top_k_neighbors
            self.gvp_node_hidden_dim_vector = config.gvp_node_hidden_dim_vector
            self.gvp_node_hidden_dim_scalar = config.gvp_node_hidden_dim_scalar
            self.gvp_edge_hidden_dim_scalar = config.gvp_edge_hidden_dim_scalar
            self.gvp_edge_hidden_dim_vector = config.gvp_edge_hidden_dim_vector
            self.gvp_num_encoder_layers = config.gvp_num_encoder_layers
            self.gvp_dropout = config.gvp_dropout
            self.encoder_layers = config.encoder_layers
            self.encoder_attention_heads = config.encoder_attention_heads
            self.attention_dropout = config.attention_dropout
            self.encoder_ffn_embed_dim = config.encoder_ffn_embed_dim
            self.decoder_layers = config.decoder_layers
            self.decoder_attention_heads = config.decoder_attention_heads
            self.decoder_ffn_embed_dim = config.decoder_ffn_embed_dim
        else:
            self.encoder_embed_dim = config.get('encoder_embed_dim', 512)
            self.decoder_embed_dim = config.get('decoder_embed_dim', 512)
            self.dropout = config.get('dropout', 0.1)
            self.gvp_top_k_neighbors = config.get('gvp_top_k_neighbors', 15)
            self.gvp_node_hidden_dim_vector = config.get('gvp_node_hidden_dim_vector', 256)
            self.gvp_node_hidden_dim_scalar = config.get('gvp_node_hidden_dim_scalar', 512)
            self.gvp_edge_hidden_dim_scalar = config.get('gvp_edge_hidden_dim_scalar', 32)
            self.gvp_edge_hidden_dim_vector = config.get('gvp_edge_hidden_dim_vector', 1)
            self.gvp_num_encoder_layers = config.get('gvp_num_encoder_layers', 3)
            self.gvp_dropout = config.get('gvp_dropout', 0.1)
            self.encoder_layers = config.get('encoder_layers', 3)
            self.encoder_attention_heads = config.get('encoder_attention_heads', 4)
            self.attention_dropout = config.get('attention_dropout', 0.1)
            self.encoder_ffn_embed_dim = config.get('encoder_ffn_embed_dim', 512)
            self.decoder_layers = config.get('decoder_layers', 3)
            self.decoder_attention_heads = config.get('decoder_attention_heads', 4)
            self.decoder_ffn_embed_dim = config.get('decoder_ffn_embed_dim', 512)

        # Fixed attributes from original inference code
        self.local_rank = int(os.getenv("LOCAL_RANK", -1))
        self.device_id = [0, 1, 2, 3, 4, 5, 6, 7]
        self.epochs = 100
        self.lr = 1e-5
        self.batch_size = 1


class RhoDesignAdapter(BaseModel):
    """RhoDesign adapter for RNA inverse folding (structure to sequence)"""

    def __init__(self, config: Union[RhoDesignConfig, Dict[str, Any]], device: str = "cpu"):
        super().__init__(config, device)
        
        if isinstance(config, RhoDesignConfig):
            self.model_type = config.model_type
            self.temperature = config.temperature
            self.use_secondary_structure = config.use_secondary_structure
            self.model_variant = config.model_variant
        else:
            self.model_type = config.get('model_type', 'rhodesign')
            self.temperature = config.get('temperature', 1e-5)
            self.use_secondary_structure = config.get('use_secondary_structure', True)
            self.model_variant = config.get('model_variant', 'with_2d')
            
        self._is_loaded = False
        self._model_instance = None
        self._model_args = None
        self._alphabet = None
        self._temp_dirs = []

        # Set up logging
        logging.basicConfig(level=logging.INFO)

    def _get_timestamp(self) -> str:
        """Return current UTC timestamp in ISO 8601 format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def load_model(self, checkpoint_path: str = None) -> None:
        """Load RhoDesign model
        
        Args:
            checkpoint_path: Path to model checkpoint
        """
        try:
            def _set_checkpoint(p: Path):
                if isinstance(self.config, RhoDesignConfig):
                    self.config.checkpoint_path = p
                else:
                    self.config['checkpoint_path'] = p

            def _get_checkpoint() -> Optional[Path]:
                if isinstance(self.config, RhoDesignConfig):
                    return self.config.checkpoint_path
                else:
                    return self.config.get('checkpoint_path')

            if checkpoint_path:
                _set_checkpoint(Path(checkpoint_path))
            else:
                # Default checkpoint path based on model variant
                if self.model_variant == 'with_2d':
                    default_path = Path("models/rhodesign/ss_apexp_best.pth")
                else:
                    default_path = Path("models/rhodesign/no_ss_apexp_best.pth")
                _set_checkpoint(default_path)

            checkpoint = _get_checkpoint()
            if checkpoint is None or not Path(checkpoint).exists():
                self.logger.info(f"Checkpoint not found at {checkpoint}. Please provide the model checkpoint.")
                self._download_model()

            self.logger.info(f"Loading {self.model_type} model from {checkpoint}")

            # Create model arguments
            self._model_args = RhoDesignArgs(self.config)
            
            # Create alphabet
            self._alphabet = Alphabet(['A', 'G', 'C', 'U', 'X'])
            
            # Create model instance based on variant
            if self.model_variant == 'with_2d':
                self._model_instance = RhoDesignModel(self._model_args, self._alphabet)
            else:
                self._model_instance = RhoDesignModelWithout2D(self._model_args, self._alphabet)
            
            # Move model to device
            self._model_instance = self._model_instance.to(self.device)
            
            # Load checkpoint
            model_dir = torch.load(checkpoint, map_location=self.device)
            self._model_instance.load_state_dict(model_dir)
            self._model_instance.eval()

            self._is_loaded = True
            self.logger.info(f"Successfully loaded {self.model_type} model")

        except Exception as e:
            raise ModelLoadError(f"Failed to load {self.model_type} model: {str(e)}")

    def _download_model(self) -> None:
        """Download RhoDesign model if not found"""
        self.logger.info("RhoDesign model download not implemented. Please manually download the model checkpoint.")
        raise ModelLoadError("Model checkpoint not found. Please download manually from the official repository.")

    def predict(self, input_data: Union[str, Dict[str, Any]],
                output_dir: Optional[str] = None,
                n_samples: Optional[int] = None,
                temperature: Optional[float] = None,
                **kwargs) -> Dict[str, Any]:
        """Generate RNA sequences from 3D structure
        
        Args:
            input_data: PDB file path or dict with structure info
            output_dir: Output directory for results  
            n_samples: Number of sequences to generate (not used for single prediction)
            temperature: Sampling temperature (overrides config)
            **kwargs: Additional parameters including secondary_structure_file
            
        Returns:
            Dictionary containing generation results
        """
        try:
            if not self._is_loaded:
                raise ModelLoadError("Model not loaded. Call load_model() first.")

            # Process input
            processed_input = self.preprocess(input_data, **kwargs)

            # Create temporary output directory if none provided
            if output_dir is None:
                temp_dir = tempfile.mkdtemp(prefix='rhodesign_')
                self._temp_dirs.append(temp_dir)
                output_dir = temp_dir
            else:
                os.makedirs(output_dir, exist_ok=True)

            # Use provided temperature or config temperature
            sample_temperature = temperature if temperature is not None else self.temperature

            # Run inference
            results = self._run_inference(processed_input, output_dir, sample_temperature)

            # Postprocess results
            return self.postprocess(results, processed_input, output_dir)

        except Exception as e:
            raise PredictionError(f"RhoDesign prediction failed: {str(e)}")

    def preprocess(self, raw_input: Union[str, Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Preprocess input for RhoDesign
        
        Args:
            raw_input: PDB file path or input dict
            **kwargs: Additional parameters including secondary_structure_file
            
        Returns:
            Preprocessed input dictionary
        """
        if isinstance(raw_input, str):
            pdb_file = raw_input
            pdb_id = os.path.splitext(os.path.basename(pdb_file))[0]
            ss_file = kwargs.get('secondary_structure_file', kwargs.get('ss_file'))
        elif isinstance(raw_input, dict):
            pdb_file = raw_input.get('pdb_file', raw_input.get('structure_file', ''))
            pdb_id = raw_input.get('id', raw_input.get('name', os.path.splitext(os.path.basename(pdb_file))[0]))
            ss_file = raw_input.get('secondary_structure_file', raw_input.get('ss_file'))
        else:
            raise InvalidSequenceError("Input must be a PDB file path or dictionary")

        # Validate PDB file
        pdb_path = Path(pdb_file)
        if not pdb_path.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_file}")

        # Validate secondary structure file if using 2D variant
        ss_path = None
        if self.model_variant == 'with_2d' and self.use_secondary_structure:
            if not ss_file:
                self.logger.warning("No secondary structure file provided for with_2d variant. "
                                  "Model may not perform optimally.")
            else:
                ss_path = Path(ss_file)
                if not ss_path.exists():
                    self.logger.warning(f"Secondary structure file not found: {ss_file}")
                    ss_path = None

        return {
            'pdb_file': str(pdb_path),
            'ss_file': str(ss_path) if ss_path else None,
            'pdb_id': pdb_id,
            'original_input': raw_input
        }

    def _run_inference(self, input_data: Dict[str, Any], output_dir: str, temperature: float) -> Dict[str, Any]:
        """Run RhoDesign inference"""
        try:
            # Load structure
            pdb = load_structure(input_data['pdb_file'])
            coords, original_seq = extract_coords_from_structure(pdb)

            # Load secondary structure if available and needed
            ss_ct_map = None
            if self.model_variant == 'with_2d' and input_data['ss_file']:
                try:
                    ss_ct_map = np.load(input_data['ss_file'])
                except Exception as e:
                    self.logger.warning(f"Failed to load secondary structure file: {e}")

            # Generate sequence
            with torch.no_grad():
                if self.model_variant == 'with_2d':
                    # With secondary structure
                    pred_seq = self._model_instance.sample(
                        coords, ss_ct_map, self.device, temperature=temperature
                    )
                else:
                    # Without secondary structure
                    pred_seq = self._model_instance.sample(
                        coords, self.device, temperature=temperature
                    )

            # Calculate recovery rate if original sequence available
            recovery_rate = seq_rec_rate(original_seq, pred_seq) if original_seq else 0.0

            # Save result to FASTA file
            fasta_file = os.path.join(output_dir, f"{input_data['pdb_id']}_predicted.fasta")
            with open(fasta_file, 'w') as f:
                f.write(f'>{input_data["pdb_id"]}_predicted_by_RhoDesign\n')
                f.write(f'{pred_seq}\n')

            return {
                'pdb_file': input_data['pdb_file'],
                'ss_file': input_data['ss_file'],
                'pdb_id': input_data['pdb_id'],
                'predicted_sequence': pred_seq,
                'original_sequence': original_seq,
                'recovery_rate': recovery_rate,
                'fasta_file': fasta_file,
                'output_dir': output_dir,
                'temperature': temperature,
                'model_variant': self.model_variant
            }

        except Exception as e:
            raise PredictionError(f"RhoDesign inference failed: {str(e)}")

    def postprocess(self, results: Dict[str, Any], input_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Post-process RhoDesign results"""
        
        # Structure results following RiboDiffusion pattern
        postprocessed = {
            'model': self.model_type,
            'model_variant': self.model_variant,
            'input': {
                'structure_file': results['pdb_file'],
                'secondary_structure_file': results['ss_file'],
                'structure_id': results['pdb_id']
            },
            'sequences': [results['predicted_sequence']],
            'sequence_ids': [f"{results['pdb_id']}_predicted"],
            'metadata': {
                'recovery_rate': results['recovery_rate'],
                'original_sequence': results['original_sequence'],
                'temperature': results['temperature'],
                'n_samples': 1,  # RhoDesign generates one sequence at a time
                'use_secondary_structure': self.use_secondary_structure and results['ss_file'] is not None
            },
            'files': {
                'fasta_files': [results['fasta_file']],
                'output_dir': results['output_dir']
            },
            'timestamp': self._get_timestamp()
        }

        # Add quality metrics
        if results['original_sequence']:
            postprocessed['quality_metrics'] = {
                'sequence_recovery_rate': results['recovery_rate'],
                'sequence_length': len(results['predicted_sequence']),
                'original_length': len(results['original_sequence'])
            }

        return postprocessed

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "name": self.model_type,
            "type": "inverse_folding",
            "variant": self.model_variant,
            "loaded": self._is_loaded,
            "device": self.device,
            "capabilities": [
                "structure_to_sequence",
                "single_sequence_generation",
                "recovery_rate_calculation"
            ],
            "supported_formats": {
                "input": ["pdb"],
                "output": ["fasta", "sequence_string"]
            },
            "parameters": {
                "temperature": self.temperature,
                "use_secondary_structure": self.use_secondary_structure,
                "model_variant": self.model_variant
            } if self._is_loaded else None
        }

    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self._temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
        self._temp_dirs.clear()

    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()