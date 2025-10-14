"""RNA-FM provider configuration"""

from pydantic import Field, field_validator

from ...core.config import BaseConfig


class RnaFmConfig(BaseConfig):
    """RNA-FM model configuration"""

    # Model metadata
    model_name: str = Field(default="rna_fm", description="Model name")
    model_type: str = Field(default="rna_fm", description="Model type")

    # Architecture parameters
    num_layers: int = Field(default=12, ge=1, description="Number of layers")
    embed_dim: int = Field(default=640, ge=1, description="Embedding dimension")
    attention_heads: int = Field(default=20, ge=1, description="Number of attention heads")
    ffn_embed_dim: int = Field(default=2560, ge=1, description="Feed-forward network dimension")
    arch: str = Field(default="roberta_large", description="Model architecture")
    max_positions: int = Field(default=1026, ge=1, description="Maximum positional encoding")

    # Prediction parameters
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Prediction threshold")
    allow_noncanonical_pairs: bool = Field(default=True, description="Allow non-canonical base pairs")
    repr_layer: int = Field(default=12, ge=1, description="Representation layer")

    # Data preprocessing parameters
    add_special_tokens: bool = Field(default=True, description="Add special tokens")
    padding: bool = Field(default=True, description="Enable padding")
    truncation: bool = Field(default=True, description="Enable truncation")
    tokenize_on_load: bool = Field(default=True, description="Tokenize on load")

    # Output settings
    save_embeddings: bool = Field(default=False, description="Save embeddings")
    save_contacts: bool = Field(default=True, description="Save contact maps")
    save_attention: bool = Field(default=False, description="Save attention")
    embedding_format: str = Field(default="raw", description="Embedding format: raw, numpy")

    # Runtime settings
    use_half_precision: bool = Field(default=False, description="Use half precision")
    use_fast_tokenizer: bool = Field(default=True, description="Use fast tokenizer")
    enable_caching: bool = Field(default=True, description="Enable caching")

    @field_validator('embedding_format')
    def validate_embedding_format(cls, v):
        """Validate embedding format"""
        valid_formats = ['raw', 'numpy']
        if v not in valid_formats:
            raise ValueError(f"Invalid embedding format: {v}. Must be one of {valid_formats}")
        return v
    
    @field_validator('arch')
    def validate_arch(cls, v):
        """Validate model architecture"""
        valid_archs = ['roberta_base', 'roberta_large']
        if v not in valid_archs:
            raise ValueError(f"Invalid architecture: {v}. Must be one of {valid_archs}")
        return v


class MrnaFmConfig(RnaFmConfig):
    """mRNA-FM model configuration, inheriting from RNA-FM configuration"""

    model_name: str = Field(default="mrna_fm", description="Model name")
    model_type: str = Field(default="mrna_fm", description="Model type")

    # mRNA-FM specific parameters
    embed_dim: int = Field(default=1280, ge=1, description="Embedding dimension")
    ffn_embed_dim: int = Field(default=5120, ge=1, description="Feed-forward network dimension")
    vocab_size: int = Field(default=32, ge=1, description="Vocabulary size")


def get_rna_fm_config(**kwargs) -> RnaFmConfig:
    """Get RNA-FM config"""
    return RnaFmConfig(**kwargs)


def get_mrna_fm_config(**kwargs) -> MrnaFmConfig:
    """Get mRNA-FM config"""
    return MrnaFmConfig(**kwargs)
