"""RiboDiffusion Adapter for RNA Inverse Folding"""

import functools
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

import ml_collections
import numpy as np
import torch
import tree

# Import RiboDiffusion components
from .diffusion.noise_schedule import NoiseScheduleVP
from .models import create_model, ExponentialMovingAverage
from .sampling import get_sampling_fn
from .utils import get_data_inverse_scaler, restore_checkpoint
from . import run_lib
from .config import get_config, RiboDiffusionConfig, convert_to_ml_collections
from ...core.base import BaseModel
from ...core.exceptions import ModelLoadError, PredictionError, InvalidSequenceError
from ...utils.file_utils import NUM_TO_LETTER, PDBtoData, sample_to_fasta


class RiboDiffusionAdapter(BaseModel):
    """RiboDiffusion adapter for RNA inverse folding (structure to sequence)"""

    def __init__(self, config: Union[RiboDiffusionConfig, Dict[str, Any]], device: str = "cpu"):
        super().__init__(config, device)
        if isinstance(config, RiboDiffusionConfig):
            self.model_type = config.model_type
        else:
            self.model_type = config.get('model_type', 'ribodiffusion')
        self._is_loaded = False
        self._model_instance = None
        self._config_instance = None
        self._temp_dirs = []

        # Set up logging
        logging.basicConfig(level=logging.INFO)

        if isinstance(config, RiboDiffusionConfig):
            self.n_samples = config.n_samples
            self.sampling_steps = config.sampling_steps
            self.cond_scale = config.cond_scale
            self.dynamic_threshold = config.dynamic_threshold
            self.dynamic_thresholding_percentile = config.dynamic_thresholding_percentile
            self.deterministic = config.deterministic
        else:
            self.n_samples = config.get('n_samples', 1)
            self.sampling_steps = config.get('sampling_steps', 200)
            self.cond_scale = config.get('cond_scale', -1.0)
            self.dynamic_threshold = config.get('dynamic_threshold', False)
            self.dynamic_thresholding_percentile = config.get('dynamic_thresholding_percentile', 0.95)
            self.deterministic = config.get('deterministic', True)

    def load_model(self, checkpoint_path: str = None) -> None:
        """Load RiboDiffusion model
        
        Args:
            checkpoint_path: Path to model checkpoint
        """
        try:
            def _set_checkpoint(p: Path):
                if isinstance(self.config, RiboDiffusionConfig):
                    self.config.checkpoint_path = p
                else:
                    self.config['checkpoint_path'] = p

            def _get_checkpoint() -> Optional[Path]:
                if isinstance(self.config, RiboDiffusionConfig):
                    return self.config.checkpoint_path
                else:
                    return self.config.get('checkpoint_path')

            if checkpoint_path:
                _set_checkpoint(Path(checkpoint_path))
            else:
                # Default checkpoint path
                default_path = Path("models/exp_inf.pth")
                _set_checkpoint(default_path)

            checkpoint = _get_checkpoint()
            if checkpoint is None or not Path(checkpoint).exists():
                self.logger.info(f"Checkpoint not found at {checkpoint}. Attempting to download or prompt.")
                self._download_model()

            self.logger.info(f"Loading {self.model_type} model from {checkpoint}")

            # Setup RiboDiffusion environment
            self._setup_ribodiffusion_environment()

            # Load the model
            self._load_ribodiffusion_model()

            self._is_loaded = True
            self.logger.info(f"Successfully loaded {self.model_type} model")

        except Exception as e:
            raise ModelLoadError(f"Failed to load RiboDiffusion model: {str(e)}")

    def _setup_ribodiffusion_environment(self) -> None:
        """Setup RiboDiffusion environment and imports"""
        try:
            # Add RiboDiffusion to Python path
            import sys
            ref_ribodiffusion_path = Path(__file__).parent.parent.parent.parent / "ref" / "RiboDiffusion"
            if ref_ribodiffusion_path.exists():
                sys.path.insert(0, str(ref_ribodiffusion_path))

            # Store references for later use
            self._run_lib = run_lib
            self._NoiseScheduleVP = NoiseScheduleVP
            self._create_model = create_model
            self._ExponentialMovingAverage = ExponentialMovingAverage
            self._get_sampling_fn = get_sampling_fn
            self._get_data_inverse_scaler = get_data_inverse_scaler
            self._restore_checkpoint = restore_checkpoint
            self._PDBtoData = PDBtoData
            self._sample_to_fasta = sample_to_fasta
            self._ml_collections = ml_collections

            # Load config
            self._load_config()

        except ImportError as e:
            raise ModelLoadError(
                f"Failed to import RiboDiffusion modules: {str(e)}. Please ensure RiboDiffusion dependencies are installed.")

    def _load_config(self) -> None:
        """Load RiboDiffusion configuration"""
        try:
            # Import the config file
            import sys
            config_path = Path(__file__).parent.parent.parent.parent / "ref" / "RiboDiffusion" / "configs"
            sys.path.insert(0, str(config_path))

            if isinstance(self.config, RiboDiffusionConfig):
                self._config_instance = convert_to_ml_collections(self.config)
            else:
                self._config_instance = get_config()

            # Override with runtime/device & eval settings
            self._config_instance.device = torch.device(self.device)
            self._config_instance.eval = self._ml_collections.ConfigDict()
            self._config_instance.eval.n_samples = self.n_samples
            self._config_instance.eval.sampling_steps = self.sampling_steps
            self._config_instance.eval.cond_scale = self.cond_scale
            self._config_instance.eval.dynamic_threshold = self.dynamic_threshold
            self._config_instance.eval.dynamic_thresholding_percentile = getattr(self, 'dynamic_thresholding_percentile', 0.95)

            if self.deterministic:
                self._config_instance.seed = 42

        except Exception as e:
            raise ModelLoadError(f"Failed to load RiboDiffusion config: {str(e)}")

    def _load_ribodiffusion_model(self) -> None:
        """Load the RiboDiffusion model instance"""
        try:
            # Set random seed
            if self.deterministic:
                self._run_lib.set_random_seed(self._config_instance)

            # Initialize model
            self._model_instance = self._create_model(self._config_instance)
            ema = self._ExponentialMovingAverage(self._model_instance.parameters(),
                                                 decay=self._config_instance.model.ema_decay)
            optimizer = self._run_lib.get_optimizer(self._config_instance, self._model_instance.parameters())

            state = dict(optimizer=optimizer, model=self._model_instance, ema=ema, step=0)

            def _get_checkpoint_path_str() -> str:
                if isinstance(self.config, RiboDiffusionConfig):
                    return str(self.config.checkpoint_path) if self.config.checkpoint_path else ''
                return str(self.config.get('checkpoint_path', ''))

            checkpoint_path = _get_checkpoint_path_str()
            state = self._restore_checkpoint(checkpoint_path, state, device=self._config_instance.device)
            ema.copy_to(self._model_instance.parameters())

            self._model_instance.eval()

            # Initialize noise scheduler
            self._noise_scheduler = self._NoiseScheduleVP(
                self._config_instance.sde.schedule,
                continuous_beta_0=self._config_instance.sde.continuous_beta_0,
                continuous_beta_1=self._config_instance.sde.continuous_beta_1
            )

            # Get data scaler
            self._inverse_scaler = self._get_data_inverse_scaler(self._config_instance)

        except Exception as e:
            raise ModelLoadError(f"Failed to load RiboDiffusion model instance: {str(e)}")

    def _download_model(self) -> None:
        """Download RiboDiffusion model if not found"""
        self.logger.info("RiboDiffusion model download not implemented. Please manually download the model checkpoint.")
        raise ModelLoadError("Model checkpoint not found. Please download manually from the official repository.")

    def predict(self, input_data: Union[str, Dict[str, Any]],
                output_dir: Optional[str] = None,
                n_samples: Optional[int] = None,
                **kwargs) -> Dict[str, Any]:
        """Generate RNA sequences from 3D structure
        
        Args:
            input_data: PDB file path or dict with structure info
            output_dir: Output directory for results  
            n_samples: Number of sequences to generate
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing generation results
        """
        try:
            if not self._is_loaded:
                raise ModelLoadError("Model not loaded. Call load_model() first.")

            # Preprocess input
            processed_input = self.preprocess(input_data)

            # Create temporary output directory if none provided
            if output_dir is None:
                temp_dir = tempfile.mkdtemp(prefix='ribodiffusion_')
                self._temp_dirs.append(temp_dir)
                output_dir = temp_dir
            else:
                os.makedirs(output_dir, exist_ok=True)

            # Override n_samples if provided
            if n_samples is not None:
                old_n_samples = self._config_instance.eval.n_samples
                self._config_instance.eval.n_samples = n_samples

            try:
                # Run inference
                results = self._run_inference(processed_input, output_dir)

                # Postprocess results
                return self.postprocess(results, processed_input, output_dir)

            finally:
                # Restore original n_samples
                if n_samples is not None:
                    self._config_instance.eval.n_samples = old_n_samples

        except Exception as e:
            raise PredictionError(f"RiboDiffusion prediction failed: {str(e)}")

    def preprocess(self, raw_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Preprocess input for RiboDiffusion
        
        Args:
            raw_input: PDB file path or input dict
            
        Returns:
            Preprocessed input dictionary
        """
        if isinstance(raw_input, str):
            pdb_file = raw_input
            pdb_id = os.path.splitext(os.path.basename(pdb_file))[0]
        elif isinstance(raw_input, dict):
            pdb_file = raw_input.get('pdb_file', raw_input.get('structure_file', ''))
            pdb_id = raw_input.get('id', raw_input.get('name', os.path.splitext(os.path.basename(pdb_file))[0]))
        else:
            raise InvalidSequenceError("Input must be a PDB file path or dictionary")

        # Validate PDB file
        pdb_path = Path(pdb_file)
        if not pdb_path.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_file}")

        return {
            'pdb_file': str(pdb_path),
            'pdb_id': pdb_id,
            'original_input': raw_input
        }

    def _run_inference(self, input_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Run RiboDiffusion inference"""
        try:
            # Create PDB to data conversion function
            pdb2data = functools.partial(
                self._PDBtoData,
                num_posenc=self._config_instance.data.num_posenc,
                num_rbf=self._config_instance.data.num_rbf,
                knn_num=self._config_instance.data.knn_num
            )

            # Convert PDB to graph data
            struct_data = pdb2data(input_data['pdb_file'])

            # Prepare data for sampling
            struct_data = tree.map_structure(
                lambda x: x.unsqueeze(0).repeat_interleave(
                    self._config_instance.eval.n_samples, dim=0
                ).to(self._config_instance.device),
                struct_data
            )

            # Setup sampling function
            test_sampling_fn = self._get_sampling_fn(
                self._config_instance,
                self._noise_scheduler,
                self._config_instance.eval.sampling_steps,
                self._inverse_scaler
            )

            # Generate sequences
            with torch.no_grad():
                samples = test_sampling_fn(self._model_instance, struct_data)

            # Create output directories
            fasta_dir = os.path.join(output_dir, 'fasta')
            os.makedirs(fasta_dir, exist_ok=True)

            # Save sequences
            generated_sequences = []
            fasta_files = []

            for i in range(len(samples)):
                fasta_file = os.path.join(fasta_dir, f"{input_data['pdb_id']}_{i}.fasta")
                self._sample_to_fasta(samples[i], input_data['pdb_id'], fasta_file)
                fasta_files.append(fasta_file)

                # Convert sample to sequence string
                seq_tensor = samples[i].cpu().numpy()
                sequence = ''.join([NUM_TO_LETTER[idx] for idx in seq_tensor])
                generated_sequences.append(sequence)

            # Calculate recovery rate
            if 'seq' in struct_data:
                original_seq = struct_data['seq'][0].cpu()  # Take first batch item
                recovery_rates = []
                for sample in samples:
                    recovery_rate = sample.eq(original_seq).float().mean().item()
                    recovery_rates.append(recovery_rate)
                avg_recovery_rate = np.mean(recovery_rates)
            else:
                recovery_rates = []
                avg_recovery_rate = 0.0

            return {
                'pdb_file': input_data['pdb_file'],
                'pdb_id': input_data['pdb_id'],
                'generated_sequences': generated_sequences,
                'fasta_files': fasta_files,
                'recovery_rates': recovery_rates,
                'average_recovery_rate': avg_recovery_rate,
                'n_samples': len(samples),
                'output_dir': output_dir,
                'fasta_dir': fasta_dir
            }

        except Exception as e:
            raise PredictionError(f"RiboDiffusion inference failed: {str(e)}")

    def postprocess(self, raw_output: Dict[str, Any],
                    original_input: Dict[str, Any],
                    output_dir: str) -> Dict[str, Any]:
        """Postprocess RiboDiffusion output
        
        Args:
            raw_output: Raw output from RiboDiffusion
            original_input: Original input data
            output_dir: Output directory
            
        Returns:
            Processed results dictionary
        """
        processed_results = {
            'pdb_file': raw_output['pdb_file'],
            'pdb_id': raw_output['pdb_id'],
            'model_type': self.model_type,
            'task_type': 'inverse_folding',
            'generated_sequences': raw_output['generated_sequences'],
            'sequence_count': raw_output['n_samples'],
            'output_directory': output_dir,
            'fasta_directory': raw_output['fasta_dir'],
            'fasta_files': raw_output['fasta_files'],
            'config': {
                'n_samples': self._config_instance.eval.n_samples,
                'sampling_steps': self._config_instance.eval.sampling_steps,
                'cond_scale': self._config_instance.eval.cond_scale,
                'dynamic_threshold': self._config_instance.eval.dynamic_threshold,
                'dynamic_thresholding_percentile': getattr(self._config_instance.eval, 'dynamic_thresholding_percentile', 0.95)
            }
        }

        # Add quality metrics
        if raw_output['recovery_rates']:
            processed_results['quality_metrics'] = {
                'recovery_rates': raw_output['recovery_rates'],
                'average_recovery_rate': raw_output['average_recovery_rate'],
                'best_recovery_rate': max(raw_output['recovery_rates']),
                'worst_recovery_rate': min(raw_output['recovery_rates'])
            }

        # Add sequence statistics
        sequences = raw_output['generated_sequences']
        if sequences:
            lengths = [len(seq) for seq in sequences]
            processed_results['sequence_statistics'] = {
                'lengths': lengths,
                'average_length': np.mean(lengths),
                'length_std': np.std(lengths),
                'unique_sequences': len(set(sequences)),
                'diversity_ratio': len(set(sequences)) / len(sequences)
            }

            # Add composition analysis
            all_seqs = ''.join(sequences)
            total_bases = len(all_seqs)
            processed_results['composition_analysis'] = {
                'A': all_seqs.count('A') / total_bases,
                'U': all_seqs.count('U') / total_bases,
                'G': all_seqs.count('G') / total_bases,
                'C': all_seqs.count('C') / total_bases,
                'GC_content': (all_seqs.count('G') + all_seqs.count('C')) / total_bases
            }

        # Validation
        validate_output = True
        if isinstance(self.config, RiboDiffusionConfig):
            validate_output = self.config.validate_output
        elif isinstance(self.config, dict):
            validate_output = self.config.get('validate_output', True)
        if validate_output:
            processed_results['validation'] = self._validate_output(processed_results)

        return processed_results

    def _validate_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output sequences and results"""
        validation = {'valid': True, 'warnings': [], 'errors': []}

        # Check if sequences were generated
        if not results.get('generated_sequences'):
            validation['errors'].append("No sequences were generated")
            validation['valid'] = False
            return validation

        # Check sequence validity
        valid_nucleotides = set('AUCG')
        for i, seq in enumerate(results['generated_sequences']):
            if not all(c.upper() in valid_nucleotides for c in seq):
                validation['errors'].append(f"Invalid nucleotides in sequence {i}")
                validation['valid'] = False

        # Check recovery rate
        if 'quality_metrics' in results:
            avg_recovery = results['quality_metrics']['average_recovery_rate']
            if avg_recovery < 0.3:
                validation['warnings'].append(f"Low average recovery rate: {avg_recovery:.3f}")
            elif avg_recovery < 0.5:
                validation['warnings'].append(f"Medium recovery rate: {avg_recovery:.3f}")

        # Check diversity
        if 'sequence_statistics' in results:
            diversity = results['sequence_statistics']['diversity_ratio']
            if diversity < 0.5:
                validation['warnings'].append(f"Low sequence diversity: {diversity:.3f}")

        # Check file existence
        for fasta_file in results.get('fasta_files', []):
            if not os.path.exists(fasta_file) or os.path.getsize(fasta_file) == 0:
                validation['errors'].append(f"Invalid or empty FASTA file: {fasta_file}")
                validation['valid'] = False

        return validation

    def generate_sequences(self, pdb_file: str, n_samples: int = 1,
                           output_dir: Optional[str] = None, **kwargs) -> List[str]:
        """Generate RNA sequences from PDB structure (simplified interface)
        
        Args:
            pdb_file: Path to PDB file
            n_samples: Number of sequences to generate
            output_dir: Output directory
            **kwargs: Additional parameters
            
        Returns:
            List of generated sequences
        """
        results = self.predict(pdb_file, output_dir=output_dir, n_samples=n_samples, **kwargs)
        return results.get('generated_sequences', [])

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self._is_loaded:
            return {"loaded": False}

        return {
            "loaded": True,
            "model_type": self.model_type,
            "device": str(self.device),
            "task_type": "inverse_folding",
            "input_format": "PDB",
            "output_format": "FASTA",
            "supports_batch": False,
            "max_sampling_steps": 1000,
            "default_n_samples": self.n_samples
        }

    def cleanup(self) -> None:
        """Clean up temporary directories and files"""
        # Use getattr to handle cases where __init__ didn't complete.
        temp_dirs = getattr(self, "_temp_dirs", None)
        if not temp_dirs:
            return
        for temp_dir in list(temp_dirs):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                # Guard logger usage in interpreter shutdown
                try:
                    if hasattr(self, "logger") and self.logger:
                        self.logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")
                except Exception:
                    pass
        try:
            temp_dirs.clear()
        except Exception:
            pass

    def __del__(self):
        """Destructor - cleanup temporary files"""
        try:
            self.cleanup()
        except Exception:
            # Be silent on interpreter shutdown or partial initialization
            pass
