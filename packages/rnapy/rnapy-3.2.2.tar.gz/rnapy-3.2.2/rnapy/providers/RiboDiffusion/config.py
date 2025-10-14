"""RiboDiffusion provider configuration"""

import ml_collections
import torch
from pydantic import Field, field_validator

from ...core.config import BaseConfig


class RiboDiffusionConfig(BaseConfig):
    """RiboDiffusion model config - RNA sequence design"""

    # Model metadata
    model_name: str = Field(default="ribodiffusion", description="Model name")
    model_type: str = Field(default="ribodiffusion", description="Model type")

    # Sampling parameters
    n_samples: int = Field(default=1, ge=1, description="Number of samples to generate")
    sampling_steps: int = Field(default=200, ge=1, description="Diffusion sampling steps")
    cond_scale: float = Field(default=-1.0, description="Condition scale (-1.0 means no scaling)")
    dynamic_threshold: bool = Field(default=False, description="Enable dynamic thresholding")
    dynamic_thresholding_percentile: float = Field(
        default=0.95, ge=0.0, le=1.0, description="Dynamic thresholding percentile"
    )
    deterministic: bool = Field(default=True, description="Use deterministic random seed")

    # Data processing parameters
    num_posenc: int = Field(default=16, ge=1, description="Number of positional encodings")
    num_rbf: int = Field(default=16, ge=1, description="Number of radial basis functions")
    knn_num: int = Field(default=10, ge=1, description="k-nearest neighbors (k)")

    # Output settings
    save_intermediate: bool = Field(default=False, description="Save intermediate results")

    # Diffusion model parameters
    diffusion_schedule: str = Field(default="cosine", description="Diffusion schedule: cosine, linear")
    continuous_beta_0: float = Field(default=0.1, ge=0.0, description="Continuous beta start")
    continuous_beta_1: float = Field(default=20.0, ge=0.0, description="Continuous beta end")

    @field_validator('diffusion_schedule')
    def validate_diffusion_schedule(cls, v):
        """Validate diffusion schedule"""
        valid_schedules = ['cosine', 'linear']
        if v not in valid_schedules:
            raise ValueError(f"Invalid diffusion schedule: {v}. Must be one of {valid_schedules}")
        return v


def get_ribodiffusion_config(**kwargs) -> RiboDiffusionConfig:
    """Get RiboDiffusion config"""
    return RiboDiffusionConfig(**kwargs)


# Backward compatibility: keep original ml_collections config
def get_config():
    """Get original ml_collections config (backward compatible)"""
    config = ml_collections.ConfigDict()

    # Misc config
    config.exp_type = 'vpsde'
    config.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    config.seed = 42
    config.save = True

    # Data config
    config.data = data = ml_collections.ConfigDict()
    data.seq_centered = True
    data.radius = 4.5
    data.top_k = 10
    data.num_rbf = 16
    data.num_posenc = 16
    data.num_conformers = 1
    data.add_noise = -1.0
    data.knn_num = 10

    # SDE
    config.sde = sde = ml_collections.ConfigDict()
    sde.schedule = 'cosine'  # 'linear', 'cosine'
    sde.continuous_beta_0 = 0.1
    sde.continuous_beta_1 = 20.

    # sampling
    config.sampling = sampling = ml_collections.ConfigDict()
    sampling.method = 'ancestral'
    ## set smaller for faster eval
    sampling.steps = 200

    # Model config
    config.model = model = ml_collections.ConfigDict()
    model.geometric_data_parallel = False
    model.ema_decay = 0.999
    model.pred_data = True
    model.self_cond = True
    model.name = 'GVPTransCond'
    model.node_in_dim = (8, 4)
    model.node_h_dim = (512, 128)
    model.edge_in_dim = (32, 1)
    model.edge_h_dim = (128, 1)
    model.num_layers = 4
    model.drop_rate = 0.1
    model.out_dim = 4
    model.time_cond = True
    model.dihedral_angle = True
    model.num_trans_layer = 8
    model.drop_struct = -1.

    model.trans = trans = ml_collections.ConfigDict()
    trans.encoder_embed_dim = 512
    trans.encoder_attention_heads = 16
    trans.attention_dropout = 0.1
    trans.dropout = 0.1
    trans.encoder_ffn_embed_dim = 1024

    # optimization
    config.optim = optim = ml_collections.ConfigDict()
    optim.weight_decay = 0
    optim.optimizer = 'AdamW'
    optim.lr = 2e-4
    optim.beta1 = 0.9
    optim.eps = 1e-8
    optim.warmup = 20000
    optim.grad_clip = 20.
    optim.disable_grad_log = True

    # Evaluation config
    config.eval = eval = ml_collections.ConfigDict()
    eval.model_path = ''
    eval.test_perplexity = False
    eval.test_recovery = True
    eval.n_samples = 1
    eval.sampling_steps = 50
    eval.cond_scale = -1.
    eval.dynamic_threshold = False
    eval.dynamic_thresholding_percentile = 0.95

    return config


def convert_to_ml_collections(ribo_config: RiboDiffusionConfig) -> ml_collections.ConfigDict:
    """Convert new config to ml_collections format"""
    ml_config = get_config()  # Get default config

    # Update key parameters
    ml_config.device = torch.device(ribo_config.device)
    ml_config.data.num_rbf = ribo_config.num_rbf
    ml_config.data.num_posenc = ribo_config.num_posenc
    ml_config.data.knn_num = ribo_config.knn_num
    ml_config.sde.schedule = ribo_config.diffusion_schedule
    ml_config.sde.continuous_beta_0 = ribo_config.continuous_beta_0
    ml_config.sde.continuous_beta_1 = ribo_config.continuous_beta_1
    ml_config.sampling.steps = ribo_config.sampling_steps
    ml_config.eval.n_samples = ribo_config.n_samples
    ml_config.eval.sampling_steps = ribo_config.sampling_steps
    ml_config.eval.cond_scale = ribo_config.cond_scale
    ml_config.eval.dynamic_threshold = ribo_config.dynamic_threshold
    ml_config.eval.dynamic_thresholding_percentile = ribo_config.dynamic_thresholding_percentile
    
    return ml_config
