import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Sequence

import numpy as np

from rnapy.core import ConfigManager, ModelFactory
from rnapy.core.config_loader import config_loader
from rnapy.core.exceptions import ModelLoadError
from rnapy.interfaces import StructurePredictionInterface, SequenceAnalysisInterface, InverseFoldingInterface, \
    MSAAnalysisInterface
from rnapy.providers.RiboDiffusion import RiboDiffusionAdapter
from rnapy.providers.rhodesign import RhoDesignAdapter
from rnapy.providers.rhofold import RhoFoldAdapter
from rnapy.providers.rna_fm import RNAFMAdapter, RNAFMPredictor
from rnapy.providers.rna_msm import RnaMSMAdapter, RnaMSMPredictor
from rnapy.utils.download_model_utils import auto_download_model, get_default_model_path, verify_model_file, \
    ModelDownloadError
from rnapy.data import DatasetDownloader
from rnapy.providers.lddt import calculate_lddt as lddt_calculate
from rnapy.providers.rmsd.calculate_rmsd import main as rmsd_main
from rnapy.providers.tm_score import calculate_tm_score as tm_score_calculate, convert_cif_to_pdb


class RNAToolkit:
    def __init__(self, config_dir: str = "configs", device: str = "cpu"):
        """Initialize RNA toolkit

        Args:
            config_dir: Configuration directory
            device: Computing device ("cpu" or "cuda")
        """
        self.device = device
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize configuration manager
        self.config_manager = ConfigManager(config_dir)
        try:
            config_loader.config_dir = Path(config_dir)
        except Exception:
            pass
        self.config_manager.create_default_configs()

        # Initialize model factory
        self.model_factory = ModelFactory()
        self._register_models()

        # Cache loaded models
        self._loaded_models = {}

        # Initialize interfaces
        self.structure_predictor = StructurePredictionInterface(self.model_factory, self._loaded_models)
        self.sequence_analyzer = SequenceAnalysisInterface(self.model_factory, self._loaded_models)
        self.inverse_folder = InverseFoldingInterface(self.model_factory, self._loaded_models)
        self.msa_analyzer = MSAAnalysisInterface(self.model_factory, self._loaded_models)

        self.logger.info(f"RNAToolkit initialized with device: {device}")

        # Dataset Download
        self.dataset_downloader = DatasetDownloader()

    def _register_models(self):
        """Register all available models"""
        # RNA-FM models
        self.model_factory.register_model("rna-fm", RNAFMAdapter)
        self.model_factory.register_model("rna_fm", RNAFMAdapter)  # Compatibility alias
        self.model_factory.register_model("mrna-fm", RNAFMAdapter)
        self.model_factory.register_model("mrna_fm", RNAFMAdapter)  # Compatibility alias

        # RhoFold models  
        self.model_factory.register_model("rhofold", RhoFoldAdapter)
        self.model_factory.register_model("rho-fold", RhoFoldAdapter)  # Compatibility alias
        self.model_factory.register_model("rhofold+", RhoFoldAdapter)  # For RhoFold+ variant

        # RiboDiffusion models
        self.model_factory.register_model("ribodiffusion", RiboDiffusionAdapter)
        self.model_factory.register_model("ribo-diffusion", RiboDiffusionAdapter)  # Compatibility alias

        # RhoDesign models
        self.model_factory.register_model("rhodesign", RhoDesignAdapter)
        self.model_factory.register_model("rho-design", RhoDesignAdapter)  # Compatibility alias

        # RNA-MSM models
        self.model_factory.register_model("rna-msm", RnaMSMAdapter)
        self.model_factory.register_model("rna_msm", RnaMSMAdapter)  # Compatibility alias

    def load_model(self, model_name: str, checkpoint_path: str = None, auto_download: bool = True, **kwargs) -> None:
        """Load pretrained model with automatic download support

        Args:
            model_name: Model name (e.g., 'rna-fm', 'mrna-fm')
            checkpoint_path: Model checkpoint file path. If None, will auto-download if auto_download=True
            auto_download: Whether to automatically download model if checkpoint_path not found
            **kwargs: Additional configuration parameters
        """
        try:
            # Handle checkpoint path resolution and auto-download
            final_checkpoint_path = self._resolve_checkpoint_path(
                model_name, checkpoint_path, auto_download
            )

            # Merge configurations using new config loader
            base_config = config_loader.load_global_config()

            # Load provider-specific config
            normalized_model_name = model_name.replace('-', '_')
            if normalized_model_name in ['rna_fm']:
                provider_config = config_loader.load_provider_config("rna_fm", **kwargs)
            elif normalized_model_name in ['mrna_fm']:
                provider_config = config_loader.load_provider_config("mrna_fm", **kwargs)
            elif normalized_model_name in ['rhofold', 'rho_fold']:
                provider_config = config_loader.load_provider_config("rhofold", **kwargs)
            elif normalized_model_name in ['ribodiffusion', 'ribo_diffusion']:
                provider_config = config_loader.load_provider_config("ribodiffusion", **kwargs)
            elif normalized_model_name in ['rhodesign', 'rho_design']:
                provider_config = config_loader.load_provider_config("rhodesign", **kwargs)
            elif normalized_model_name in ['rna_msm', 'rna_msm']:
                provider_config = config_loader.load_provider_config("rna_msm", **kwargs)
            else:
                # For unknown models, use base config with kwargs
                provider_config = base_config
                provider_config.update(kwargs)

            # Use provider config as the final config (it already includes merged settings)
            config = provider_config

            # Create model
            model = self.model_factory.create_model(model_name, config, self.device)

            # Load checkpoint
            model.load_model(final_checkpoint_path)

            # Cache model
            self._loaded_models[model_name] = model

            # Update model references in interfaces
            self.structure_predictor.update_loaded_models(self._loaded_models)
            self.sequence_analyzer.update_loaded_models(self._loaded_models)
            self.inverse_folder.update_loaded_models(self._loaded_models)
            self.msa_analyzer.update_loaded_models(self._loaded_models)

            self.logger.info(f"Successfully loaded model: {model_name}")

        except Exception as e:
            raise ModelLoadError(f"Failed to load model {model_name}: {str(e)}")

    def analyze_sequence(self, sequences: Union[str, List[str]],
                         model: str = "rna-fm",
                         analysis_type: str = "full",
                         **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Comprehensive sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            analysis_type: Analysis type ('full', 'embedding', 'structure', 'properties')
            **kwargs: Additional parameters
        
        Returns:
            Analysis results - single dict or list of dicts
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.analyze_sequence(sequences, analysis_type, model, **kwargs)

    def predict_structure(self, sequences: Union[str, List[str]],
                          structure_type: str = "2d",
                          model: str = "rna-fm",
                          threshold: float = 0.5,
                          save_dir: Optional[str] = None,
                          **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Predict RNA structure
        
        Args:
            sequences: RNA sequences or FASTA file path
            structure_type: Structure type ("2d" or "3d")
            model: Model name to use
            threshold: Contact probability threshold (for 2D structure only)
            save_dir: File path to save results (CT format for single sequence)
            **kwargs: Additional parameters
        
        Returns:
            Structure prediction results
        """
        self._ensure_model_loaded(model)

        if structure_type == "2d":
            return self.structure_predictor.predict_2d_structure(sequences, model, threshold, save_dir=save_dir,
                                                                 **kwargs)
        elif structure_type == "3d":
            return self.structure_predictor.predict_3d_structure(sequences, model=model, save_dir=save_dir, **kwargs)
        else:
            raise ValueError(f"Unsupported structure type: {structure_type}")

    def extract_embeddings(self, sequences: Union[str, List[str]],
                           model: str = "rna-fm",
                           layer: int = 12,
                           format: str = "raw",
                           save_dir: Optional[str] = None,
                           **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Extract sequence embeddings
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            layer: Layer number to extract
            format: Embedding format ("raw", "mean", "bos")
            save_dir: File path to save embeddings (.npy for single, .npz for multiple)
            **kwargs: Additional parameters
        
        Returns:
            Embedding representation array(s)
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.extract_embeddings(sequences, model, layer, format, save_dir=save_dir, **kwargs)

    def compare_sequences(self, seq1: Union[str, List[str]], seq2: Union[str, List[str]],
                          model: str = "rna-fm",
                          comparison_type: str = "sequence",
                          embedding_format: str = "raw",
                          **kwargs) -> Dict[str, Any]:
        """Compare two sequences
        
        Args:
            seq1: First sequence(s) or FASTA file
            seq2: Second sequence(s) or FASTA file
            model: Model name to use
            comparison_type: Comparison type ("full", "embedding", "structure", "sequence")
            embedding_format: Embedding format ("raw", "mean", "bos")
            **kwargs: Additional parameters
        
        Returns:
            Comparison results dictionary
        """
        return self.sequence_analyzer.compare_sequences(seq1, seq2, model, comparison_type, embedding_format, **kwargs)

    def compare_structures(self, structure1: str, structure2: str) -> Dict[str, Any]:
        """Compare two RNA structures

        Args:
            structure1: structure in dot-bracket format
            structure2: structure in dot-bracket format

        Returns:
            Results dictionary
        """
        return self.sequence_analyzer.compare_structures(structure1, structure2)

    def calculate_structure_f1(self, structure1: str, structure2: str) -> Dict[str, float]:
        """Calculate F1 score for secondary structure comparison
        
        Args:
            structure1: First structure in dot-bracket notation
            structure2: Second structure in dot-bracket notation
            
        Returns:
            Dictionary with precision, recall, and f1_score
        """
        return self.sequence_analyzer.calculate_structure_f1(structure1, structure2)

    def calculate_sequence_recovery(self, native_seq: str, designed_seq: str) -> Dict[str, Any]:
        """Calculate sequence recovery rate
        
        Args:
            native_seq: Native/reference sequence
            designed_seq: Designed/predicted sequence
            
        Returns:
            Dictionary with overall and per-nucleotide recovery rates
        """
        return self.sequence_analyzer.calculate_sequence_recovery(native_seq, designed_seq)

    def batch_analyze(self, sequences: Union[str, List[str]],
                      analysis_type: str = "full",
                      model: str = "rna-fm",
                      **kwargs) -> List[Dict[str, Any]]:
        """Batch sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type
            model: Model name to use
            **kwargs: Additional parameters
        
        Returns:
            List of analysis results
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.batch_analyze(sequences, analysis_type, model, **kwargs)

    def predict_secondary_structure(self, sequences: Union[str, List[str]],
                                    threshold: float = 0.5,
                                    model: str = "rna-fm",
                                    advanced_postprocess: bool = True,
                                    allow_noncanonical: bool = True,
                                    **kwargs) -> Union[str, List[str]]:
        """Predict secondary structure
        
        Args:
            sequences: RNA sequences or FASTA file path
            threshold: Contact probability threshold
            model: Model name to use
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Dot-bracket format secondary structure(s)
        """
        self._ensure_model_loaded(model)

        # Get model instance and handle FASTA input processing
        from .utils.file_utils import process_sequence_input
        sequence_ids, sequence_list = process_sequence_input(sequences)

        model_instance = self._loaded_models[model]
        structures = model_instance.predict_secondary_structure(
            sequence_list, threshold, advanced_postprocess, allow_noncanonical
        )

        # Return single structure if single input
        is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
        return structures[0] if is_single_input else structures

    def save_ct_files(self, sequences: Union[str, List[str]],
                      output_dir: str,
                      sequence_ids: Optional[List[str]] = None,
                      model: str = "rna-fm",
                      threshold: float = 0.5,
                      advanced_postprocess: bool = True,
                      allow_noncanonical: bool = True,
                      **kwargs) -> List[str]:
        """Generate and save CT files
        
        Args:
            sequences: RNA sequences or FASTA file path
            output_dir: Output directory
            sequence_ids: Optional sequence identifiers
            model: Model name to use
            threshold: Contact probability threshold
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            List of generated CT file paths
        """
        self._ensure_model_loaded(model)

        # Process input to get sequences and IDs
        from .utils.file_utils import process_sequence_input
        auto_ids, sequence_list = process_sequence_input(sequences)

        # Use provided IDs or auto-generated ones
        if sequence_ids is None:
            sequence_ids = auto_ids

        model_instance = self._loaded_models[model]
        return model_instance.save_ct_file(
            sequence_list, output_dir, sequence_ids,
            threshold, advanced_postprocess, allow_noncanonical
        )

    def predict_contacts(self, sequences: Union[str, List[str]],
                         model: str = "rna-fm",
                         threshold: float = 0.5,
                         return_processed: bool = True,
                         allow_noncanonical: bool = True,
                         **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Predict contact map
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            threshold: Contact probability threshold
            return_processed: Return processed contact map (with multiple pairing handling)
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Contact map(s) - raw or processed
        """
        self._ensure_model_loaded(model)

        # Process input
        from .utils.file_utils import process_sequence_input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))

        predictor = self.create_predictor(model)
        contacts = predictor.predict_contacts(
            sequence_list, threshold, return_processed, allow_noncanonical
        )

        return contacts[0] if is_single_input else contacts

    def analyze_structure_details(self, sequence: str,
                                  model: str = "rna-fm",
                                  threshold: float = 0.5,
                                  advanced_postprocess: bool = True,
                                  allow_noncanonical: bool = True,
                                  **kwargs) -> Dict[str, Any]:
        """Detailed structure analysis
        
        Args:
            sequence: RNA sequence
            model: Model name to use
            threshold: Contact threshold
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Detailed structure analysis results
        """
        self._ensure_model_loaded(model)

        predictor = self.create_predictor(model)
        return predictor.analyze_structure_details(
            sequence, threshold, advanced_postprocess, allow_noncanonical
        )

    def create_predictor(self, model: str = "rna-fm"):
        """Create predictor instance
        
        Args:
            model: Model name
        
        Returns:
            Predictor instance
        """
        self._ensure_model_loaded(model)
        if model in ("rna-msm", "rna_msm"):
            return RnaMSMPredictor(self._loaded_models[model])
        else:
            return RNAFMPredictor(self._loaded_models[model])

    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        """Get model information
        
        Args:
            model: Model name, if None returns info for all loaded models
        
        Returns:
            Model information dictionary
        """
        if model is None:
            return {
                name: model_instance.get_model_info()
                for name, model_instance in self._loaded_models.items()
            }
        else:
            if model in self._loaded_models:
                return self._loaded_models[model].get_model_info()
            else:
                return {"loaded": False, "available": model in self.model_factory.list_models()}

    def list_available_models(self) -> List[str]:
        """List all available models"""
        return self.model_factory.list_models()

    def list_loaded_models(self) -> List[str]:
        """List loaded models"""
        return list(self._loaded_models.keys())

    def get_model_download_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get download information for a specific model
        
        Args:
            model_name: Model name to check
            
        Returns:
            Model download info including local status
        """
        from rnapy.utils.download_model_utils import get_model_info_from_registry

        model_info = get_model_info_from_registry(model_name)
        if not model_info:
            return None

        # Check local status
        default_path = get_default_model_path(model_name)
        local_exists = default_path and Path(default_path).exists()
        local_valid = local_exists and verify_model_file(default_path)

        return {
            "model_name": model_name,
            "description": model_info["description"],
            "repo_id": model_info["repo_id"],
            "filename": model_info["filename"],
            "local_dir": model_info["local_dir"],
            "local_path": default_path,
            "local_exists": local_exists,
            "local_valid": local_valid,
            "download_required": not local_valid
        }

    def download_model(self, model_name: str, force_download: bool = False) -> str:
        """Download a model without loading it
        
        Args:
            model_name: Model name to download
            force_download: Force re-download even if file exists
            
        Returns:
            Path to downloaded model file
        """
        try:
            downloaded_path = auto_download_model(model_name, force_download=force_download)
            self.logger.info(f"Model {model_name} downloaded to: {downloaded_path}")
            return downloaded_path
        except Exception as e:
            raise ModelLoadError(f"Failed to download model {model_name}: {str(e)}")

    def check_models_status(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all available models
        
        Returns:
            Dict with status info for each model
        """
        status = {}
        for model_name in self.list_available_models():
            # Get basic model info
            info = self.get_model_info(model_name)
            download_info = self.get_model_download_info(model_name)

            status[model_name] = {
                "loaded": info.get("loaded", False),
                "downloadable": download_info is not None,
                "local_exists": download_info.get("local_exists", False) if download_info else False,
                "local_valid": download_info.get("local_valid", False) if download_info else False,
                "download_required": download_info.get("download_required", True) if download_info else True
            }

        return status

    def generate_sequences_from_structure(self, structure_file: str,
                                          model: str = "ribodiffusion",
                                          n_samples: int = 1,
                                          save_dir: Optional[str] = None,
                                          **kwargs) -> Dict[str, Any]:
        """Generate RNA sequences from 3D structure (inverse folding)
        
        Args:
            structure_file: Path to PDB structure file
            model: Model name for inverse folding
            n_samples: Number of sequences to generate
            save_dir: Output directory for results
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing generated sequences and metadata
        """
        return self.inverse_folder.generate_sequences(
            structure_file=structure_file,
            model=model,
            n_samples=n_samples,
            output_dir=save_dir,
            **kwargs
        )

    def batch_generate_sequences_from_structures(self, structure_files: Union[List[str], str],
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
        return self.inverse_folder.batch_generate_sequences(
            structure_files=structure_files,
            model=model,
            n_samples=n_samples,
            output_base_dir=output_base_dir,
            **kwargs
        )

    def analyze_generated_sequences(self, generation_results: Dict[str, Any],
                                    include_structure_analysis: bool = True) -> Dict[str, Any]:
        """Analyze properties of generated sequences
        
        Args:
            generation_results: Results from generate_sequences_from_structure
            include_structure_analysis: Whether to predict secondary structure
        
        Returns:
            Analysis results
        """
        return self.inverse_folder.analyze_generated_sequences(
            generation_results=generation_results,
            include_structure_analysis=include_structure_analysis
        )

    def compare_with_native_sequence(self, generation_results: Dict[str, Any],
                                     native_sequence: Optional[str] = None) -> Dict[str, Any]:
        """Compare generated sequences with native sequence if available
        
        Args:
            generation_results: Results from generate_sequences_from_structure
            native_sequence: Native sequence for comparison (if available)
        
        Returns:
            Comparison results
        """
        return self.inverse_folder.compare_with_native_sequence(
            generation_results=generation_results,
            native_sequence=native_sequence
        )

    # MSA Analysis methods
    def extract_msa_features(self, sequences: Union[str, List[str]],
                             feature_type: str = "embeddings",
                             model: str = "rna-msm",
                             layer: int = -1,
                             save_dir: Optional[str] = None,
                             **kwargs) -> Union[np.ndarray, Dict[str, np.ndarray], Dict[str, Any]]:
        """Extract features from RNA sequences using MSA transformer
        
        Args:
            sequences: RNA sequence(s) or FASTA file path
            feature_type: Type of features ("embeddings", "attention", "both")
            model: Model name to use (default: rna-msm)
            layer: Layer to extract from (-1 for last layer)
            save_dir: Directory to save features
            **kwargs: Additional parameters
            
        Returns:
            Extracted features as numpy arrays or dict
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.extract_msa_features(
            sequences=sequences,
            feature_type=feature_type,
            model=model,
            layer=layer,
            save_dir=save_dir,
            **kwargs
        )

    def analyze_msa(self, msa_sequences: List[str],
                    model: str = "rna-msm",
                    extract_consensus: bool = True,
                    extract_conservation: bool = True,
                    save_dir: Optional[str] = None,
                    **kwargs) -> Dict[str, Any]:
        """Analyze Multiple Sequence Alignment
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use (default: rna-msm)
            extract_consensus: Extract consensus sequence
            extract_conservation: Calculate conservation scores
            save_dir: Directory to save analysis results
            **kwargs: Additional parameters
            
        Returns:
            MSA analysis results including features, consensus, conservation
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.analyze_msa(
            msa_sequences=msa_sequences,
            model=model,
            extract_consensus=extract_consensus,
            extract_conservation=extract_conservation,
            save_dir=save_dir,
            **kwargs
        )

    def compare_sequences_msa(self, seq1: Union[str, List[str]],
                              seq2: Union[str, List[str]],
                              model: str = "rna-msm",
                              comparison_method: str = "embedding_similarity",
                              **kwargs) -> Dict[str, Any]:
        """Compare sequences using MSA-based features
        
        Args:
            seq1: First sequence or MSA
            seq2: Second sequence or MSA
            model: Model name to use (default: rna-msm)
            comparison_method: Method for comparison
            **kwargs: Additional parameters
            
        Returns:
            Comparison results with similarity scores
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.compare_sequences_msa(
            seq1=seq1,
            seq2=seq2,
            model=model,
            comparison_method=comparison_method,
            **kwargs
        )

    def extract_consensus_sequence(self, msa_sequences: List[str],
                                   model: str = "rna-msm",
                                   **kwargs) -> str:
        """Extract consensus sequence from MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use (default: rna-msm)
            **kwargs: Additional parameters
            
        Returns:
            Consensus sequence string
        """
        return self.msa_analyzer.extract_consensus_sequence(
            msa_sequences=msa_sequences,
            model=model,
            **kwargs
        )

    def calculate_conservation_scores(self, msa_sequences: List[str],
                                      **kwargs) -> List[float]:
        """Calculate conservation scores for each position in MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            **kwargs: Additional parameters
            
        Returns:
            List of conservation scores (0-1, higher = more conserved)
        """
        return self.msa_analyzer.calculate_conservation_scores(
            msa_sequences=msa_sequences,
            **kwargs
        )

    def batch_msa_analysis(self, msa_list: List[List[str]],
                           model: str = "rna-msm",
                           extract_consensus: bool = True,
                           extract_conservation: bool = True,
                           **kwargs) -> List[Dict[str, Any]]:
        """Batch analyze multiple MSAs
        
        Args:
            msa_list: List of MSA sequences (each MSA is a list of sequences)
            model: Model name to use (default: rna-msm)
            extract_consensus: Extract consensus for each MSA
            extract_conservation: Calculate conservation for each MSA
            **kwargs: Additional parameters
            
        Returns:
            List of MSA analysis results
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.batch_msa_analysis(
            msa_list=msa_list,
            model=model,
            extract_consensus=extract_consensus,
            extract_conservation=extract_conservation,
            **kwargs
        )

    def get_msa_statistics(self, msa_sequences: List[str]) -> Dict[str, Any]:
        """Get basic statistics for an MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            
        Returns:
            MSA statistics including length, depth, composition
        """
        return self.msa_analyzer.get_msa_statistics(msa_sequences=msa_sequences)

    def unload_model(self, model: str) -> None:
        """Unload model
        
        Args:
            model: Model name
        """
        if model in self._loaded_models:
            del self._loaded_models[model]

            # Update model references in interfaces
            self.structure_predictor.update_loaded_models(self._loaded_models)
            self.sequence_analyzer.update_loaded_models(self._loaded_models)
            self.msa_analyzer.update_loaded_models(self._loaded_models)

            self.logger.info(f"Unloaded model: {model}")
        else:
            self.logger.warning(f"Model {model} was not loaded")

    def set_device(self, device: str) -> None:
        """Set computing device
        
        Args:
            device: Device name ("cpu" or "cuda")
        """
        self.device = device

        # Move loaded models to new device
        for name, model in self._loaded_models.items():
            if hasattr(model, 'model') and model.model is not None:
                model.model = model.model.to(device)
                model.device = device
                self.logger.info(f"Moved model {name} to {device}")

    def _resolve_checkpoint_path(self, model_name: str, checkpoint_path: str = None,
                                 auto_download: bool = True) -> str:
        """Resolve checkpoint path with auto-download support
        
        Args:
            model_name: Model name
            checkpoint_path: Provided checkpoint path
            auto_download: Whether to auto-download if path not found
            
        Returns:
            Resolved checkpoint path
            
        Raises:
            ModelLoadError: If checkpoint cannot be resolved
        """
        # If explicit path provided, validate and return
        if checkpoint_path:
            if Path(checkpoint_path).exists():
                if verify_model_file(checkpoint_path):
                    self.logger.info(f"Using provided checkpoint: {checkpoint_path}")
                    return checkpoint_path
                else:
                    self.logger.warning(f"Provided checkpoint file appears invalid: {checkpoint_path}")
            else:
                self.logger.warning(f"Provided checkpoint path does not exist: {checkpoint_path}")

        # Try default path from registry
        default_path = get_default_model_path(model_name)
        if default_path and Path(default_path).exists():
            if verify_model_file(default_path):
                self.logger.info(f"Using default checkpoint: {default_path}")
                return default_path
            else:
                self.logger.warning(f"Default checkpoint file appears invalid: {default_path}")

        # Auto-download if enabled
        if auto_download or checkpoint_path is None:
            try:
                self.logger.info(f"Auto-downloading model: {model_name}")
                downloaded_path = auto_download_model(model_name)

                # Verify downloaded file
                if verify_model_file(downloaded_path):
                    return downloaded_path
                else:
                    raise ModelDownloadError(f"Downloaded model file appears invalid: {downloaded_path}")

            except (ValueError, ModelDownloadError) as e:
                self.logger.error(f"Auto-download failed: {str(e)}")
                raise ModelLoadError(f"Cannot resolve checkpoint for {model_name}: {str(e)}")

        # All options exhausted
        error_msg = f"Cannot find valid checkpoint for model '{model_name}'"
        if checkpoint_path:
            error_msg += f". Provided path '{checkpoint_path}' not found/invalid"
        if default_path:
            error_msg += f". Default path '{default_path}' not found/invalid"
        error_msg += f". Auto-download is {'disabled' if not auto_download else 'failed'}"

        raise ModelLoadError(error_msg)

    def _ensure_model_loaded(self, model: str) -> None:
        """Ensure model is loaded"""
        if model not in self._loaded_models:
            raise ModelLoadError(f"Model {model} is not loaded. Call load_model() first.")

    def _setup_logging(self, level: str = "INFO"):
        """Setup logging"""
        logging.basicConfig(
            level=getattr(logging, level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def list_available_datasets(self):
        """List available example datasets"""
        return self.dataset_downloader.list_available_datasets()

    def download_dataset(self, dataset_name: str, download_dir: Optional[str] = None, max_workers: int = 1) -> None:
        """Download example datasets

        Args:
            dataset_name: Name of the dataset to download (e.g., 'pdb', 'rfam')
            download_dir: Directory to save the dataset
            max_workers: Number of parallel workers for downloading files
        Returns:
            Path to downloaded dataset directory
        """
        self.dataset_downloader.download_datasets(dataset_name, download_dir=download_dir, max_workers=max_workers)

    def calculate_lddt(self,
                       reference_structure: str,
                       predicted_structure: str,
                       radius: float = 15.0,
                       distance_thresholds: Union[str, Sequence[float]] = (0.5, 1.0, 2.0, 4.0),
                       return_column_scores: bool = False) -> Dict[str, Any]:
        """Calculate LDDT between reference and predicted structures."""
        if isinstance(distance_thresholds, str):
            thresholds: Union[str, Sequence[float]] = distance_thresholds
        else:
            thresholds = tuple(distance_thresholds)
        return lddt_calculate(
            reference_structure=reference_structure,
            predicted_structure=predicted_structure,
            radius=radius,
            distance_thresholds=thresholds,
            return_column_scores=return_column_scores,
        )

    def calculate_rmsd(self,
                       file_a: str,
                       file_b: str,
                       rotation: str = "kabsch",
                       file_format: Optional[str] = None,
                       output_aligned_structure: bool = False,
                       print_only_rmsd_atoms: bool = False,
                       reorder: bool = False,
                       reorder_method: str = "inertia-hungarian",
                       use_reflections: bool = False,
                       use_reflections_keep_stereo: bool = False,
                       only_alpha_carbons: bool = False,
                       ignore_hydrogen: bool = False,
                       remove_idx: Optional[List[int]] = None,
                       add_idx: Optional[List[int]] = None,
                       gzip_format: bool = False) -> Union[float, str]:
        """Calculate RMSD between two structures using the embedded rmsd tool.

        Returns float when output_aligned_structure=False, otherwise XYZ string.
        """
        # Mutual exclusivity mirrors CLI behavior
        if output_aligned_structure and reorder and (ignore_hydrogen or (add_idx is not None) or (remove_idx is not None)):
            raise ValueError("Cannot reorder/atom-filter and print structure simultaneously")
        if (use_reflections or use_reflections_keep_stereo) and output_aligned_structure and (ignore_hydrogen or (add_idx is not None) or (remove_idx is not None)):
            raise ValueError("Cannot use reflections on atoms and print when excluding atoms")
        if print_only_rmsd_atoms and not output_aligned_structure:
            raise ValueError("print_only_rmsd_atoms requires output_aligned_structure=True")

        args: List[str] = []
        # Rotation method
        if rotation:
            args.extend(["--rotation", rotation])
        # Reorder
        if reorder:
            args.append("--reorder")
        if reorder_method:
            args.extend(["--reorder-method", reorder_method])
        # Reflections
        if use_reflections:
            args.append("--use-reflections")
        if use_reflections_keep_stereo:
            args.append("--use-reflections-keep-stereo")
        # Filtering (mutually exclusive by design; user ensures not conflicting)
        if only_alpha_carbons:
            args.append("--only-alpha-carbons")
        elif ignore_hydrogen:
            args.append("--ignore-hydrogen")
        elif remove_idx:
            args.extend(["--remove-idx", *[str(i) for i in remove_idx]])
        elif add_idx:
            args.extend(["--add-idx", *[str(i) for i in add_idx]])
        # Format
        if file_format:
            args.extend(["--format", file_format])
        if gzip_format:
            args.append("--format-is-gzip")
        # Output
        if output_aligned_structure:
            args.append("--output")
            if print_only_rmsd_atoms:
                args.append("--print-only-rmsd-atoms")
        # Positional files
        args.extend([file_a, file_b])

        result = rmsd_main(args)
        if output_aligned_structure:
            return result
        try:
            return float(result)
        except Exception as exc:
            raise RuntimeError(f"Unexpected RMSD result: {result}") from exc

    def calculate_tm_score(self,
                          structure_1: str,
                          structure_2: str,
                          mol: str = "all",
                          score_type: str = "t",
                          use_multithreading: bool = False,
                          ncpu: Optional[int] = None,
                          d0: Optional[float] = None,
                          da: str = "n",
                          ia: Optional[str] = None,
                          ri: str = "n",
                          sid: float = 0.7,
                          wt: str = "n",
                          odis: str = "n",
                          mode: str = "normal",
                          atom_nuc: str = " C3'",
                          atom_res: str = " CA ",
                          nit: int = 20,
                          nLinit: int = 6,
                          clig: str = "y",
                          output_aligned: Optional[str] = None,
                          save_rotation_matrix: Optional[str] = None,
                          save_superposition: Optional[str] = None) -> Dict[str, Any]:
        """Calculate TM-score between two structures.
        
        Args:
            structure_1: Path to first structure (reference)
            structure_2: Path to second structure (prediction)
            mol: Molecule types to superimpose (all, prt, dna, rna, lig, p+d, p+r, etc.)
            score_type: Use TM-score ('t') or rTM-score ('r')
            use_multithreading: Use multi-threading version
            ncpu: Number of CPU threads
            d0: Custom d0 value for TM-score scaling
            da: Use molecule order from files ('y') or auto-generate ('n')
            ia: Path to molecule mapping file
            ri: Use matched residue/nucleotide indexes ('y' or 'n')
            sid: Global sequence identity cutoff (0-1)
            wt: Load water molecules ('y' or 'n')
            odis: Output distance details ('y' or 'n')
            mode: Computation mode ('fast' or 'normal')
            atom_nuc: Atom name for nucleotides (default " C3'")
            atom_res: Atom name for residues (default " CA ")
            nit: Maximum iteration number
            nLinit: Maximum L_init number
            clig: Re-map ligand atoms ('y' or 'n')
            output_aligned: Path to save aligned structure
            save_rotation_matrix: Path to save rotation matrix
            save_superposition: Path to save superposition info
            
        Returns:
            Dictionary containing TM-score results
        """
        return tm_score_calculate(
            structure_1=structure_1,
            structure_2=structure_2,
            mol=mol,
            score_type=score_type,
            use_multithreading=use_multithreading,
            ncpu=ncpu,
            d0=d0,
            da=da,
            ia=ia,
            ri=ri,
            sid=sid,
            wt=wt,
            odis=odis,
            mode=mode,
            atom_nuc=atom_nuc,
            atom_res=atom_res,
            nit=nit,
            nLinit=nLinit,
            clig=clig,
            output_aligned=output_aligned,
            save_rotation_matrix=save_rotation_matrix,
            save_superposition=save_superposition
        )

    def convert_cif_to_pdb(self, cif_file: str, pdb_file: str, use_multithreading: bool = False) -> bool:
        """Convert CIF file to PDB format using TM-score tool.
        
        Args:
            cif_file: Input CIF file path
            pdb_file: Output PDB file path
            use_multithreading: Use multi-threading version
            
        Returns:
            True if conversion successful
        """
        return convert_cif_to_pdb(cif_file, pdb_file, use_multithreading)

    def __repr__(self) -> str:
        loaded_models = list(self._loaded_models.keys())
        available_models = self.model_factory.list_models()

        return f"""RNAToolkit(
                device='{self.device}',
                loaded_models={loaded_models},
                available_models={available_models}
            )"""
