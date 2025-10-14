import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Union, Optional
import shutil

import numpy as np
import torch

from .config import get_rhofold_config, validate_rhofold_config, create_rhofold_model_config
from ...core.base import BaseModel
from ...core.exceptions import ModelLoadError, PredictionError, InvalidSequenceError


class RhoFoldAdapter(BaseModel):
    """RhoFold adapter for RNA 3D structure prediction"""

    def __init__(self, config: Dict[str, Any], device: str = "cpu"):
        super().__init__(config, device)

        # Initialize attributes early to prevent destructor errors
        self._temp_dirs = []  # Track temporary directories for cleanup
        self._is_loaded = False
        self._model_instance = None

        # Now load and validate config
        self.config = get_rhofold_config(config)
        validate_rhofold_config(self.config)

        self.model_type = getattr(self.config, 'model_type', 'rhofold')

        # Set up logging
        logging.basicConfig(level=logging.INFO)

    def _get_config_value(self, key: str, default=None):
        """Safely get configuration value from Pydantic config object"""
        return getattr(self.config, key, default)

    def load_model(self, checkpoint_path: str = None) -> None:
        """Load RhoFold model
        
        Args:
            checkpoint_path: Path to model checkpoint
        """
        try:
            if checkpoint_path:
                # For Pydantic objects, we need to update differently
                if hasattr(self.config, 'checkpoint_path'):
                    self.config.checkpoint_path = Path(checkpoint_path)
                else:
                    # Fallback - create new config with updated path
                    config_dict = self.config.model_dump() if hasattr(self.config, 'model_dump') else self.config.dict()
                    config_dict['checkpoint_path'] = Path(checkpoint_path)
                    self.config = get_rhofold_config(config_dict)

            checkpoint_path = self.config.checkpoint_path
            if not checkpoint_path.exists():
                self.logger.info(f"Checkpoint not found at {checkpoint_path}")
                self._download_model(checkpoint_path)

            self.logger.info(f"Loading {self.model_type} model from {checkpoint_path}")

            # Import RhoFold modules (assume they are in the ref directory or installed)
            self._setup_rhofold_environment()

            # Load the model
            self._load_rhofold_model(checkpoint_path)

            self._is_loaded = True
            self.logger.info(f"Successfully loaded {self.model_type} model")

        except Exception as e:
            raise ModelLoadError(f"Failed to load RhoFold model: {str(e)}")

    def _setup_rhofold_environment(self) -> None:
        """Setup RhoFold environment and imports"""
        try:
            # Import RhoFold components
            # from rhofold.rhofold import RhoFold
            # from rhofold.config import rhofold_config
            # from rhofold.utils.alphabet import get_features
            # from rhofold.utils import get_device, save_ss2ct, timing
            # from rhofold.relax.relax import AmberRelaxation
            from .rhofold import RhoFold
            from .config import get_rhofold_config, create_rhofold_model_config
            from .utils.alphabet import get_features
            from .utils import get_device, save_ss2ct, timing
            from .relax.relax import AmberRelaxation

            # Store references for later use
            self._RhoFold = RhoFold
            self._rhofold_config = get_rhofold_config()
            self._get_features = get_features
            self._get_device = get_device
            self._save_ss2ct = save_ss2ct
            self._timing = timing
            self._AmberRelaxation = AmberRelaxation

        except ImportError as e:
            raise ModelLoadError(
                f"Failed to import RhoFold modules: {str(e)}. Please ensure RhoFold is properly installed.")

    def _load_rhofold_model(self, checkpoint_path: Path) -> None:
        """Load the RhoFold model instance"""
        try:
            # Convert RhoFoldConfig to model config format
            model_config = create_rhofold_model_config(self._rhofold_config)

            # Initialize model with proper config structure
            self._model_instance = self._RhoFold(model_config)

            # Load checkpoint
            self.logger.info(f"Loading checkpoint from {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))

            if 'model' in checkpoint:
                state_dict = checkpoint['model']
            else:
                state_dict = checkpoint

            # Load with strict=False to allow extra/missing keys and log details
            load_result = self._model_instance.load_state_dict(state_dict, strict=False)
            if hasattr(load_result, 'unexpected_keys') and load_result.unexpected_keys:
                self.logger.info(
                    "Ignoring unexpected keys in state_dict: %s",
                    ", ".join(load_result.unexpected_keys)
                )
            if hasattr(load_result, 'missing_keys') and load_result.missing_keys:
                self.logger.info(
                    "Missing keys when loading state_dict: %s",
                    ", ".join(load_result.missing_keys)
                )

            self._model_instance.eval()

            # Move to device
            device_name = self._get_config_value('device', 'cpu')
            self.device = self._get_device(device_name)
            self._model_instance = self._model_instance.to(self.device)

        except Exception as e:
            raise ModelLoadError(f"Failed to load RhoFold model instance: {str(e)}")

    def _download_model(self, checkpoint_path: Path) -> None:
        """Download RhoFold model if not found"""
        self.logger.info("Downloading RhoFold model...")
        try:
            # Create directory
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

            # Download using huggingface_hub
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id='cuhkaih/rhofold',
                local_dir=checkpoint_path.parent,
                allow_patterns="*.pt"
            )

            # Check if file exists after download
            if not checkpoint_path.exists():
                # Try alternative filename
                alt_path = checkpoint_path.parent / "RhoFold_pretrained.pt"
                if alt_path.exists():
                    alt_path.rename(checkpoint_path)
                else:
                    raise FileNotFoundError("Downloaded model not found")

        except Exception as e:
            raise ModelLoadError(f"Failed to download model: {str(e)}")

    def predict(self, input_data: Union[str, Dict[str, Any]],
                msa_file: Optional[str] = None,
                output_dir: Optional[str] = None,
                **kwargs) -> Dict[str, Any]:
        """
        Predict RNA 3D structure using RhoFold
        
        Args:
            input_data: RNA sequence or input dictionary
            msa_file: Optional path to MSA file
            output_dir: Output directory for results
            **kwargs: Additional parameters including relax_steps
            
        Returns:
            Dictionary containing prediction results
        """
        if not self._is_loaded:
            raise ModelLoadError("Model not loaded. Call load_model() first.")

        try:
            # Extract relax_steps from kwargs if provided
            if 'relax_steps' in kwargs:
                # Temporarily update config with provided relax_steps
                original_relax_steps = getattr(self.config, 'relax_steps', 1000)
                setattr(self.config, 'relax_steps', kwargs['relax_steps'])
                self.logger.info(f"Using custom relax_steps: {kwargs['relax_steps']}")
            
            # Preprocess input
            processed_input = self.preprocess(input_data, msa_file)
            
            # Create output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix='rhofold_', 
                                            dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp'))
                self._temp_dirs.append(output_dir)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Run inference
            inference_results = self._run_inference(processed_input, output_dir)
            
            # Run refinement if enabled
            if self._get_config_value('enable_relaxation', True) and self._get_config_value('relax_steps', 1000) > 0:
                inference_results = self._run_refinement(inference_results, output_dir)
            
            # Post-process results
            final_results = self.postprocess(inference_results, processed_input, output_dir)
            
            # Restore original relax_steps if it was temporarily changed
            if 'relax_steps' in kwargs:
                setattr(self.config, 'relax_steps', original_relax_steps)
            
            return final_results

        except Exception as e:
            # Restore original relax_steps in case of error
            if 'relax_steps' in kwargs and 'original_relax_steps' in locals():
                setattr(self.config, 'relax_steps', original_relax_steps)
            raise PredictionError(f"RhoFold prediction failed: {str(e)}")

    def preprocess(self, raw_input: Union[str, Dict[str, Any]],
                   msa_file: Optional[str] = None) -> Dict[str, Any]:
        """Preprocess input for RhoFold
        
        Args:
            raw_input: RNA sequence or input dict
            msa_file: Optional MSA file
            
        Returns:
            Preprocessed input dictionary
        """
        if isinstance(raw_input, str):
            sequence = raw_input
            seq_id = "seq_0"
        elif isinstance(raw_input, dict):
            sequence = raw_input.get('sequence', raw_input.get('seq', ''))
            seq_id = raw_input.get('id', raw_input.get('name', 'seq_0'))
        else:
            raise InvalidSequenceError("Input must be a string sequence or dictionary")

        # Validate sequence
        if not self._validate_sequence(sequence):
            raise InvalidSequenceError(f"Invalid RNA sequence: {sequence}")

        # Check length
        max_len = self._get_config_value('max_sequence_length', 1000)
        if len(sequence) > max_len:
            raise InvalidSequenceError(f"Sequence too long: {len(sequence)} > {max_len}")

        # Create temporary files for RhoFold input in project directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        temp_base = os.path.join(project_root, 'temp')
        os.makedirs(temp_base, exist_ok=True)
        temp_dir = tempfile.mkdtemp(prefix='rhofold_input_', dir=temp_base)
        self._temp_dirs.append(temp_dir)

        # Write FASTA file
        fasta_file = os.path.join(temp_dir, f"{seq_id}.fasta")
        with open(fasta_file, 'w') as f:
            f.write(f">{seq_id}\n{sequence}\n")

        processed_input = {
            'sequence': sequence,
            'seq_id': seq_id,
            'fasta_file': fasta_file,
            'msa_file': msa_file,
            'temp_dir': temp_dir,
            'length': len(sequence)
        }

        # Generate MSA if not provided and MSA is enabled
        if self._get_config_value('use_msa', True) and msa_file is None:
            if not self._get_config_value('single_seq_pred', False):
                processed_input['msa_file'] = self._generate_msa(processed_input)

        return processed_input

    def _generate_msa(self, input_data: Dict[str, Any]) -> str:
        """Generate MSA for the input sequence"""
        if not self._get_config_value('database_path') or not self._get_config_value('binary_path'):
            self.logger.warning("Database or binary path not configured. Using single sequence prediction.")
            return input_data['fasta_file']

        try:
            from .data.balstn import BLASTN

            databases = [
                str(self._get_config_value('database_path') / 'rnacentral.fasta'),
                str(self._get_config_value('database_path') / 'nt')
            ]

            blast = BLASTN(
                binary_dpath=str(self._get_config_value('binary_path')),
                databases=databases
            )

            msa_file = os.path.join(input_data['temp_dir'], f"{input_data['seq_id']}.a3m")
            blast.query(input_data['fasta_file'], msa_file, self.logger)

            return msa_file

        except Exception as e:
            self.logger.warning(f"MSA generation failed: {str(e)}. Using single sequence.")
            return input_data['fasta_file']

    def _run_inference(self, input_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Run RhoFold inference"""
        try:
            # Prepare features
            fasta_file = input_data['fasta_file']
            msa_file = input_data.get('msa_file', fasta_file)

            data_dict = self._get_features(fasta_file, msa_file)

            # Move tensors to device
            tokens = data_dict['tokens'].to(self.device)
            rna_fm_tokens = data_dict['rna_fm_tokens'].to(self.device)

            # Forward pass
            with torch.no_grad():
                outputs = self._model_instance(
                    tokens=tokens,
                    rna_fm_tokens=rna_fm_tokens,
                    seq=data_dict['seq']
                )

            # Get final output
            output = outputs[-1]

            # Save outputs
            results = {
                'sequence': input_data['sequence'],
                'seq_id': input_data['seq_id'],
                'raw_output': output,
                'data_dict': data_dict,
                'output_dir': output_dir
            }

            seq_id = input_data['seq_id']

            # Save secondary structure
            if self._get_config_value('save_secondary_structure', True):
                ss_prob_map = torch.sigmoid(output['ss'][0, 0]).data.cpu().numpy()
                ss_file = os.path.join(output_dir, f'{seq_id}-ss.ct')
                self._save_ss2ct(ss_prob_map, data_dict['seq'], ss_file, threshold=0.5)
                results['secondary_structure_file'] = ss_file
                results['secondary_structure_prob'] = ss_prob_map

            # Save distogram and other predictions
            if self._get_config_value('save_distogram', True):
                npz_file = os.path.join(output_dir, f'{seq_id}-results.npz')
                np.savez_compressed(
                    npz_file,
                    dist_n=torch.softmax(output['n'].squeeze(0), dim=0).data.cpu().numpy(),
                    dist_p=torch.softmax(output['p'].squeeze(0), dim=0).data.cpu().numpy(),
                    dist_c=torch.softmax(output['c4_'].squeeze(0), dim=0).data.cpu().numpy(),
                    ss_prob_map=ss_prob_map if 'ss_prob_map' in locals() else None,
                    plddt=output['plddt'][0].data.cpu().numpy(),
                )
                results['distogram_file'] = npz_file
                results['confidence_scores'] = output['plddt'][0].data.cpu().numpy()

            # Save unrelaxed structure
            if self._get_config_value('save_unrelaxed', True):
                unrelaxed_file = os.path.join(output_dir, f'{seq_id}-unrelaxed_model.pdb')
                node_cords_pred = output['cord_tns_pred'][-1].squeeze(0)

                self._model_instance.structure_module.converter.export_pdb_file(
                    data_dict['seq'],
                    node_cords_pred.data.cpu().numpy(),
                    path=unrelaxed_file,
                    chain_id=None,
                    confidence=output['plddt'][0].data.cpu().numpy(),
                    logger=self.logger
                )
                results['unrelaxed_structure_file'] = unrelaxed_file

            return results

        except Exception as e:
            raise PredictionError(f"RhoFold inference failed: {str(e)}")

    def _run_refinement(self, results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Run structure refinement using Amber relaxation"""
        if 'unrelaxed_structure_file' not in results:
            self.logger.warning("No unrelaxed structure found for refinement")
            return results

        try:
            relax_steps = self._get_config_value('relax_steps', 1000)
            if relax_steps <= 0:
                return results

            with self._timing(f'Amber Relaxation: {relax_steps} iterations', logger=self.logger):
                amber_relax = self._AmberRelaxation(max_iterations=relax_steps, logger=self.logger)
                relaxed_file = os.path.join(output_dir, f'{results['seq_id']}-relaxed_{relax_steps}_model.pdb')

                amber_relax.process(results['unrelaxed_structure_file'], relaxed_file)
                results['relaxed_structure_file'] = relaxed_file

        except Exception as e:
            self.logger.warning(f"Structure refinement failed: {str(e)}")

        return results

    def postprocess(self, raw_output: Dict[str, Any],
                    original_input: Dict[str, Any],
                    output_dir: str) -> Dict[str, Any]:
        """Postprocess RhoFold output
        
        Args:
            raw_output: Raw output from RhoFold
            original_input: Original input data
            output_dir: Output directory
            
        Returns:
            Processed results dictionary
        """
        processed_results = {
            'sequence': raw_output['sequence'],
            'sequence_id': raw_output['seq_id'],
            'sequence_length': len(raw_output['sequence']),
            'model_type': self.model_type,
            'output_directory': output_dir,
            'prediction_time': time.time()  # Could be actual prediction time
        }

        # Add structure files
        if 'unrelaxed_structure_file' in raw_output:
            processed_results['structure_3d_unrelaxed'] = raw_output['unrelaxed_structure_file']

        if 'relaxed_structure_file' in raw_output:
            processed_results['structure_3d_refined'] = raw_output['relaxed_structure_file']

        # Add secondary structure
        if 'secondary_structure_file' in raw_output:
            processed_results['secondary_structure_file'] = raw_output['secondary_structure_file']

            # Parse secondary structure from CT file
            try:
                secondary_structure = self._parse_ct_file(raw_output['secondary_structure_file'])
                processed_results['secondary_structure'] = secondary_structure
            except Exception as e:
                self.logger.warning(f"Failed to parse secondary structure: {str(e)}")

        # Add confidence scores
        if 'confidence_scores' in raw_output:
            processed_results['confidence_scores'] = raw_output['confidence_scores']
            processed_results['average_confidence'] = float(np.mean(raw_output['confidence_scores']))

        # Add additional files
        if 'distogram_file' in raw_output:
            processed_results['distogram_file'] = raw_output['distogram_file']

        # Validation
        if self._get_config_value('validate_output', True):
            processed_results['validation'] = self._validate_output(processed_results)

        return processed_results

    def _parse_ct_file(self, ct_file: str) -> str:
        """Parse CT file to dot-bracket notation"""
        try:
            pairs = {}
            sequence_length = 0

            with open(ct_file, 'r') as f:
                lines = f.readlines()

                # First line contains sequence length
                if lines:
                    sequence_length = int(lines[0].split()[0])

                # Parse pairing information
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 5:
                        pos = int(parts[0]) - 1  # Convert to 0-based
                        pair_pos = int(parts[4]) - 1 if int(parts[4]) > 0 else -1
                        if pair_pos >= 0:
                            pairs[pos] = pair_pos

            # Convert to dot-bracket notation
            structure = ['.'] * sequence_length
            for i, j in pairs.items():
                if i < j:  # Avoid duplicates
                    structure[i] = '('
                    structure[j] = ')'

            return ''.join(structure)

        except Exception as e:
            self.logger.warning(f"Failed to parse CT file: {str(e)}")
            return '.' * len(getattr(self.config, 'sequence', ''))

    def _validate_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output structure and results"""
        validation = {'valid': True, 'warnings': [], 'errors': []}

        # Check if structure files exist and are readable
        for key in ['structure_3d_unrelaxed', 'structure_3d_refined']:
            if key in results:
                pdb_file = results[key]
                if not os.path.exists(pdb_file) or os.path.getsize(pdb_file) == 0:
                    validation['errors'].append(f"Invalid or empty structure file: {pdb_file}")
                    validation['valid'] = False

        # Check confidence scores
        if 'average_confidence' in results:
            avg_conf = results['average_confidence']
            if avg_conf < 0.5:
                validation['warnings'].append(f"Low average confidence: {avg_conf:.3f}")
            elif avg_conf < 0.7:
                validation['warnings'].append(f"Medium confidence: {avg_conf:.3f}")

        # Check for very long sequences (computational limitations)
        if 'sequence_length' in results and results['sequence_length'] > 500:
            validation['warnings'].append(
                f"Long sequence ({results['sequence_length']} nt) - results may be less reliable")

        return validation

    def _validate_sequence(self, sequence: str) -> bool:
        """Validate RNA sequence"""
        if not sequence:
            return False

        valid_nucleotides = set('AUCG')
        return all(c.upper() in valid_nucleotides for c in sequence)

    def extract_features(self, sequence: str, feature_type: str = "structure") -> np.ndarray:
        """Extract features from RNA sequence using RhoFold
        
        Args:
            sequence: RNA sequence
            feature_type: Type of features to extract
            
        Returns:
            Extracted features array
        """
        if not self._is_loaded:
            raise ModelLoadError("Model not loaded. Call load_model() first.")

        # This is a simplified feature extraction
        # Full implementation would extract intermediate representations
        results = self.predict(sequence)

        if feature_type == "structure" and 'distogram_file' in results:
            # Load and return distogram features
            data = np.load(results['distogram_file'])
            return data['dist_n']  # Return N atom distances as example

        return np.array([])

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self._is_loaded:
            return {"loaded": False}

        return {
            "loaded": True,
            "model_type": self.model_type,
            "device": str(self.device),
            "config": self.config,
            "supports_3d_prediction": True,
            "supports_msa": self._get_config_value('use_msa', True),
            "max_sequence_length": self._get_config_value('max_sequence_length', 1000)
        }

    def cleanup(self) -> None:
        """Clean up temporary directories and files"""
        for temp_dir in self._temp_dirs:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")
        self._temp_dirs.clear()

    def __del__(self):
        """Destructor - cleanup temporary files"""
        self.cleanup()
