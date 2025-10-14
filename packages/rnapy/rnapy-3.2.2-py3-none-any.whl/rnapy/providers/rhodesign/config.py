"""RhoDesign provider configuration"""

from pydantic import Field, field_validator

from ...core.config import BaseConfig


class RhoDesignConfig(BaseConfig):
    """RhoDesign model config - RNA inverse folding"""

    # Model metadata
    model_name: str = Field(default="rhodesign", description="Model name")
    model_type: str = Field(default="rhodesign", description="Model type")

    # Model architecture parameters
    encoder_embed_dim: int = Field(default=512, ge=64, description="Encoder embedding dimension")
    decoder_embed_dim: int = Field(default=512, ge=64, description="Decoder embedding dimension")
    dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="Dropout rate")

    # GVP parameters
    gvp_top_k_neighbors: int = Field(default=15, ge=1, description="GVP top-k neighbors")
    gvp_node_hidden_dim_vector: int = Field(default=256, ge=64, description="GVP node hidden dim (vector)")
    gvp_node_hidden_dim_scalar: int = Field(default=512, ge=64, description="GVP node hidden dim (scalar)")
    gvp_edge_hidden_dim_scalar: int = Field(default=32, ge=8, description="GVP edge hidden dim (scalar)")
    gvp_edge_hidden_dim_vector: int = Field(default=1, ge=1, description="GVP edge hidden dim (vector)")
    gvp_num_encoder_layers: int = Field(default=3, ge=1, description="GVP encoder layers")
    gvp_dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="GVP dropout rate")

    # Transformer parameters
    encoder_layers: int = Field(default=3, ge=1, description="Transformer encoder layers")
    encoder_attention_heads: int = Field(default=4, ge=1, description="Encoder attention heads")
    attention_dropout: float = Field(default=0.1, ge=0.0, le=1.0, description="Attention dropout rate")
    encoder_ffn_embed_dim: int = Field(default=512, ge=64, description="Encoder FFN embedding dimension")

    decoder_layers: int = Field(default=3, ge=1, description="Decoder layers")
    decoder_attention_heads: int = Field(default=4, ge=1, description="Decoder attention heads")
    decoder_ffn_embed_dim: int = Field(default=512, ge=64, description="Decoder FFN embedding dimension")

    # Sampling parameters
    temperature: float = Field(default=1e-5, gt=0.0, description="Sampling temperature")
    use_secondary_structure: bool = Field(default=True, description="Use secondary structure information")

    # Model variants
    model_variant: str = Field(default="with_2d", description="Model variant: with_2d, without_2d")

    @field_validator('model_variant')
    def validate_model_variant(cls, v):
        """Validate model variant"""
        valid_variants = ['with_2d', 'without_2d']
        if v not in valid_variants:
            raise ValueError(f"Invalid model variant: {v}. Must be one of {valid_variants}")
        return v


def get_rhodesign_config(**kwargs) -> RhoDesignConfig:
    """Get RhoDesign config"""
    return RhoDesignConfig(**kwargs)