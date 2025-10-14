"""RNA-MSM provider configuration"""

from pathlib import Path
from typing import Tuple
from pydantic import Field, field_validator

from ...core.config import BaseConfig


class RnaMSMConfig(BaseConfig):
    """RNA-MSM model config - Multiple Sequence Alignment Transformer"""

    # Model metadata
    model_name: str = Field(default="rna-msm", description="Model name")
    model_type: str = Field(default="rna_msm", description="Model type")
    
    # Model architecture parameters
    embed_dim: int = Field(default=768, ge=1, description="Embedding dimension")
    num_attention_heads: int = Field(default=12, ge=1, description="Number of attention heads")
    num_layers: int = Field(default=10, ge=1, description="Number of transformer layers")
    embed_positions_msa: bool = Field(default=True, description="Use positional embeddings for MSA")
    dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="Dropout rate")
    attention_dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="Attention dropout rate")
    activation_dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="Activation dropout rate")
    
    # Data processing parameters
    architecture: str = Field(default="rna language", description="Model architecture type")
    max_seqlen: int = Field(default=1024, ge=1, description="Maximum sequence length")
    max_tokens: int = Field(default=16384, ge=1, description="Maximum tokens per MSA")
    max_seqs_per_msa: int = Field(default=512, ge=1, description="Maximum sequences per MSA")
    sample_method: str = Field(default="hhfilter", description="MSA sampling method")
    
    # Inference parameters
    extract_layer: int = Field(default=-1, description="Layer to extract features from (-1 for last layer)")
    extract_attention: bool = Field(default=True, description="Extract attention maps")
    extract_embeddings: bool = Field(default=True, description="Extract sequence embeddings")
    
    # I/O parameters
    MSA_path: str = Field(default="results", description="MSA data path")
    MSA_list: str = Field(default="rna_id.txt", description="RNA ID list file")
    output_format: str = Field(default="numpy", description="Output format: numpy, json")
    
    @field_validator('sample_method')
    def validate_sample_method(cls, v):
        """Validate MSA sampling method"""
        valid_methods = ['hhfilter', 'random', 'clustal']
        if v not in valid_methods:
            raise ValueError(f"Invalid sample method: {v}. Must be one of {valid_methods}")
        return v
    
    @field_validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format"""
        valid_formats = ['numpy', 'json', 'pickle']
        if v not in valid_formats:
            raise ValueError(f"Invalid output format: {v}. Must be one of {valid_formats}")
        return v
    
    @field_validator('extract_layer')
    def validate_extract_layer(cls, v):
        """Validate extraction layer"""
        if v < -1:
            raise ValueError(f"Invalid extract layer: {v}. Must be >= -1")
        return v


def get_rna_msm_config(**kwargs) -> RnaMSMConfig:
    """Get RNA-MSM config with optional parameter overrides"""
    return RnaMSMConfig(**kwargs) 