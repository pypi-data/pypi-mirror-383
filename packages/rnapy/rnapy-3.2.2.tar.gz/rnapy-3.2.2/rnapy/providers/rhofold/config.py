"""RhoFold provider configuration"""

from typing import Optional, Dict, Any, Union
from pathlib import Path
from pydantic import field_validator, Field
from ...core.config import BaseConfig


class RhoFoldConfig(BaseConfig):
    """RhoFold model configuration - RNA 3D structure prediction"""

    # Model metadata
    model_name: str = Field(default="rhofold", description="Model name")
    model_type: str = Field(default="rhofold", description="Model type")
    description: str = Field(
        default="RhoFold - RNA 3D structure prediction using language model-based deep learning",
        description="Model description"
    )
    
    # Path settings (inherits checkpoint_path from BaseConfig)
    database_path: Optional[Path] = Field(default=None, description="Sequence database path for MSA generation")
    binary_path: Optional[Path] = Field(default=None, description="External binaries path (e.g., blastn)")

    # MSA settings
    use_msa: bool = Field(default=True, description="Whether to use MSA for prediction")
    single_seq_pred: bool = Field(default=False, description="Single-sequence mode (faster but less accurate)")
    max_msa_clusters: int = Field(default=512, ge=1, description="Maximum number of MSA sequences")
    max_extra_msa: int = Field(default=1024, ge=1, description="Maximum number of extra MSA sequences")

    # Structure relaxation settings
    relax_steps: int = Field(default=1000, ge=0, description="Amber relaxation steps (0 disables)")
    enable_relaxation: bool = Field(default=True, description="Enable structure relaxation")

    # Output settings
    save_unrelaxed: bool = Field(default=True, description="Save unrelaxed structure")
    save_relaxed: bool = Field(default=True, description="Save relaxed structure")
    save_secondary_structure: bool = Field(default=True, description="Save secondary structure in CT format")
    save_distogram: bool = Field(default=True, description="Save distogram and contact predictions")
    save_confidence_scores: bool = Field(default=True, description="Save per-residue confidence scores")

    # Advanced settings
    chunk_size: Optional[int] = Field(default=None, ge=1, description="Chunk size for memory management")
    check_steric_clashes: bool = Field(default=False, description="Check steric clashes (slower)")

    @field_validator('database_path', 'binary_path', mode="before")
    @classmethod
    def convert_paths(cls, v):
        """Convert string to Path object"""
        if v is None:
            return v
        return Path(v)


class RhoFoldDatabaseInfo:
    """RhoFold database info"""

    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Get database information"""
        return {
            'rnacentral': {
                'description': 'RNAcentral database for MSA generation',
                'size_gb': 50,
                'url': 'https://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/'
            },
            'rfam': {
                'description': 'Rfam database for RNA families',
                'size_gb': 10,
                'url': 'https://ftp.ebi.ac.uk/pub/databases/Rfam/'
            },
            'nt': {
                'description': 'NCBI nucleotide database',
                'size_gb': 400,
                'url': 'https://ftp.ncbi.nlm.nih.gov/blast/db/'
            }
        }
    
    @staticmethod
    def get_model_urls() -> Dict[str, str]:
        """Get model download URLs"""
        return {
            'rhofold_pretrained': 'https://huggingface.co/cuhkaih/rhofold/resolve/main/rhofold_pretrained_params.pt',
            'rhofold_latest': 'https://huggingface.co/cuhkaih/rhofold/resolve/main/RhoFold_pretrained.pt'
        }


def convert_rhofold_config_to_model_config(rhofold_config: RhoFoldConfig) -> Dict[str, Any]:
    """
    Convert RhoFoldConfig to the model configuration format required by RhoFold.__init__

    Args:
        rhofold_config: RhoFoldConfig object containing user-level configuration

    Returns:
        Dict containing the nested configuration structure expected by RhoFold model
    """

    # Default model configuration structure based on the original RhoFold architecture
    default_model_config = {
        "globals": {
            "c_z": 128,
            "c_m": 256,
            "c_t": 64,
            "c_e": 64,
            "c_s": 384,
            'msa_depth': rhofold_config.max_msa_clusters if rhofold_config.use_msa else 1,
            'frame_version': 'v5.0',
            "eps": 1e-8,
        },
        "model": {
            "input_embedder": {
                "tf_dim": 22,
                "msa_dim": 49,
                "c_z": 128,
                "c_m": 256,
                "relpos_k": 32,
            },
            'msa_embedder': {
                "c_z": 128,
                "c_m": 256,
                'rna_fm': {
                    'enable': True,
                },
            },
            "recycling_embedder": {
                'recycles': 10,
                "c_z": 128,
                "c_m": 256,
                "min_bin": 2,
                "max_bin": 40,
                "no_bins": 40,
            },
            "e2eformer_stack": {
                "blocks_per_ckpt": 1,
                "c_m": 256,
                "c_z": 128,
                "c_hidden_msa_att": 32,
                "c_hidden_opm": 32,
                "c_hidden_mul": 128,
                "c_hidden_pair_att": 32,
                "c_s": 384,
                "no_heads_msa": 8,
                "no_heads_pair": 4,
                "no_blocks": 12,
                "transition_n": 4,
            },
            "structure_module": {
                "c_s": 384,
                "c_z": 128,
                "c_ipa": 16,
                "c_resnet": 128,
                "no_heads_ipa": 12,
                "no_qk_points": 4,
                "no_v_points": 8,
                "no_blocks": 8,
                "no_transition_layers": 1,
                "no_resnet_blocks": 2,
                "no_angles": 6,
                "trans_scale_factor": 10,
                'refinenet': {
                    'enable': True,
                    'dim': 64,
                    'is_pos_emb': True,
                    'n_layer': 4,
                }
            },
            "heads": {
                "plddt": {
                    "c_in": 384,
                    "no_bins": 50,
                },
                "dist": {
                    "c_in": 128,
                    "no_bins": 40,
                },
                "ss": {
                    "c_in": 128,
                    "no_bins": 1,
                },
            },
        }
    }

    # Apply user configuration adjustments
    if not rhofold_config.use_msa:
        # Single sequence mode adjustments - reduce MSA depth to 1
        default_model_config["globals"]["msa_depth"] = 1

    # Adjust chunk size if specified (add to globals if needed)
    if rhofold_config.chunk_size is not None:
        default_model_config["globals"]["chunk_size"] = rhofold_config.chunk_size

    # Adjust MSA parameters
    if rhofold_config.max_msa_clusters != 512:  # If different from default
        default_model_config["globals"]["msa_depth"] = rhofold_config.max_msa_clusters

    return default_model_config


def create_rhofold_model_config(rhofold_config: Union[RhoFoldConfig, Dict[str, Any], None] = None) -> object:
    """
    Create a configuration object for RhoFold model initialization

    Args:
        rhofold_config: RhoFoldConfig object, dict, or None for default

    Returns:
        Configuration object that can be passed to RhoFold.__init__
    """

    # Convert to RhoFoldConfig if needed
    if rhofold_config is None:
        rhofold_config = RhoFoldConfig()
    elif isinstance(rhofold_config, dict):
        rhofold_config = RhoFoldConfig(**rhofold_config)
    elif not isinstance(rhofold_config, RhoFoldConfig):
        raise ValueError(f"Invalid config type: {type(rhofold_config)}")

    # Get the model configuration dict
    model_config_dict = convert_rhofold_config_to_model_config(rhofold_config)

    # Create a configuration object that supports both attribute access and dict unpacking
    class ConfigNamespace:
        def __init__(self, config_dict):
            self._config_dict = config_dict
            # Recursively convert all nested dictionaries to ConfigNamespace objects
            for key, value in config_dict.items():
                if isinstance(value, dict):
                    setattr(self, key, ConfigNamespace(value))
                else:
                    setattr(self, key, value)

        def __getattr__(self, name):
            # Check if the attribute exists in the original config dict
            if hasattr(self, '_config_dict') and name in self._config_dict:
                value = self._config_dict[name]
                if isinstance(value, dict):
                    return ConfigNamespace(value)
                return value
            # Raise AttributeError for truly missing attributes instead of returning None
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def __iter__(self):
            """Make the object iterable for dict unpacking"""
            if hasattr(self, '_config_dict'):
                return iter(self._config_dict)
            return iter([])

        def __getitem__(self, key):
            """Support dict-like access for unpacking"""
            if hasattr(self, '_config_dict'):
                value = self._config_dict[key]
                # Return ConfigNamespace for nested dicts to maintain consistency
                if isinstance(value, dict):
                    return ConfigNamespace(value)
                return value
            raise KeyError(key)

        def keys(self):
            """Support dict.keys() for unpacking"""
            if hasattr(self, '_config_dict'):
                return self._config_dict.keys()
            return []

        def values(self):
            """Support dict.values() for unpacking"""
            if hasattr(self, '_config_dict'):
                # Convert nested dicts to ConfigNamespace for consistent access
                for value in self._config_dict.values():
                    if isinstance(value, dict):
                        yield ConfigNamespace(value)
                    else:
                        yield value
            return []

        def items(self):
            """Support dict.items() for unpacking"""
            if hasattr(self, '_config_dict'):
                # Convert nested dicts to ConfigNamespace for consistent access
                for key, value in self._config_dict.items():
                    if isinstance(value, dict):
                        yield key, ConfigNamespace(value)
                    else:
                        yield key, value
            return []

        def get(self, key, default=None):
            """Support dict.get() method"""
            if hasattr(self, '_config_dict') and key in self._config_dict:
                value = self._config_dict[key]
                if isinstance(value, dict):
                    return ConfigNamespace(value)
                return value
            return default

    return ConfigNamespace(model_config_dict)


def get_clean_rhofold_config(rhofold_config: RhoFoldConfig) -> Dict[str, Any]:
    """
    Get a clean configuration dict that only contains fields accepted by RhoFold model
    
    This function filters out any extra fields from the RhoFoldConfig that are not
    part of the original RhoFold model configuration structure.
    
    Args:
        rhofold_config: RhoFoldConfig object containing user-level configuration
        
    Returns:
        Dict containing only the configuration fields that RhoFold model expects
    """
    # Use the conversion function to get the proper model config
    return convert_rhofold_config_to_model_config(rhofold_config)


def get_rhofold_config(config: Union[Dict[str, Any], RhoFoldConfig] = None, **kwargs) -> RhoFoldConfig:
    """Get RhoFold config"""
    if config is None:
        return RhoFoldConfig(**kwargs)

    if isinstance(config, RhoFoldConfig):
        # If config is already a RhoFoldConfig object, return it as is
        # or create a new one with updated kwargs if any
        if kwargs:
            # Convert existing config to dict and merge with kwargs
            config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()
            merged_config = {**config_dict, **kwargs}
            return RhoFoldConfig(**merged_config)
        return config

    if isinstance(config, dict):
        # Merge config dict with any additional kwargs
        merged_config = {**config, **kwargs}
        return RhoFoldConfig(**merged_config)

    # Fallback - treat as kwargs
    return RhoFoldConfig(**kwargs)


# Keep backward-compatible functions
def get_default_rhofold_config() -> Dict[str, Any]:
    """Get default RhoFold config (backward compatible)"""
    config = RhoFoldConfig()
    return config.dict()


def validate_rhofold_config(config: Union[Dict[str, Any], RhoFoldConfig]) -> None:
    """Validate RhoFold config (backward compatible)"""
    try:
        if isinstance(config, RhoFoldConfig):
            # If already a RhoFoldConfig object, it's already validated
            return
        elif isinstance(config, dict):
            # Try to create RhoFoldConfig from dict to validate
            RhoFoldConfig(**config)
        else:
            raise ValueError(f"Config must be a dictionary or RhoFoldConfig object, got {type(config)}")
    except Exception as e:
        raise ValueError(f"Invalid RhoFold configuration: {e}")


def get_model_urls() -> Dict[str, str]:
    """Get model URLs (backward compatible)"""
    return RhoFoldDatabaseInfo.get_model_urls()


def get_database_info() -> Dict[str, Any]:
    """Get database info (backward compatible)"""
    return RhoFoldDatabaseInfo.get_database_info()
