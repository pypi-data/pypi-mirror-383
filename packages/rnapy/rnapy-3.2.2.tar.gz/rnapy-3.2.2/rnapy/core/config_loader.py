from typing import Dict, Type, Optional, Union, cast
from pathlib import Path
import logging
from .config import BaseConfig, GlobalConfig, config_manager
from ..providers.rhodesign import RhoDesignConfig
from ..providers.rna_fm.config import RnaFmConfig, MrnaFmConfig
from ..providers.rhofold.config import RhoFoldConfig
from ..providers.RiboDiffusion.config import RiboDiffusionConfig
from ..providers.rna_msm import RnaMSMConfig


class ConfigLoader:
    """Configuration loader"""

    # Registered configuration classes
    _config_registry: Dict[str, Type[BaseConfig]] = {
        'global': GlobalConfig,
        'rna_fm': RnaFmConfig,
        'mrna_fm': MrnaFmConfig,
        'rhofold': RhoFoldConfig,
        'ribodiffusion': RiboDiffusionConfig,
        'rhodesign': RhoDesignConfig,
        'rna_msm': RnaMSMConfig,
    }
    
    def __init__(self, config_dir: Union[str, Path] = "configs"):
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @classmethod
    def register_config(cls, name: str, config_class: Type[BaseConfig]):
        cls._config_registry[name] = config_class
        
    @classmethod
    def list_available_configs(cls) -> Dict[str, Type[BaseConfig]]:
        return cls._config_registry.copy()
    
    def load_provider_config(
        self,
        provider: str,
        config_file: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> BaseConfig:
        """
        Load a provider-specific configuration

        Args:
            provider: Provider name (e.g., 'rna_fm', 'rhofold', 'ribodiffusion')
            config_file: Optional path to configuration file
            **kwargs: Additional configuration parameters

        Returns:
            Configuration instance

        Raises:
            ValueError: If the provider is not registered
        """
        if provider not in self._config_registry:
            available = list(self._config_registry.keys())
            raise ValueError(f"Unknown provider: {provider}. Available: {available}")
        
        config_class = self._config_registry[provider]
        
        # If no config file is specified, try the default path
        if config_file is None:
            default_file = self.config_dir / f"{provider}.yaml"
            if default_file.exists():
                config_file = default_file
        
        # If there's no config file, use default settings
        if config_file is None:
            self.logger.info(f"No config file found for {provider}, using default configuration")
            config_instance = config_class(**kwargs)
            config_manager._configs[provider] = config_instance
            return config_instance
        
        return config_manager.load_config(
            config_class=config_class,
            config_name=provider,
            config_file=config_file,
            **kwargs
        )
    
    def load_global_config(
        self,
        config_file: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> GlobalConfig:
        """Load global configuration"""
        return cast(GlobalConfig, self.load_provider_config('global', config_file, **kwargs))

    def create_example_configs(self):
        """Create example configuration files"""
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Global config
        global_config = GlobalConfig()
        config_manager.save_config("global", global_config)
        
        # RNA-FM config
        rna_fm_config = RnaFmConfig(
            checkpoint_path=Path("./models/rna_fm/RNA-FM_pretrained.pth"),
            max_sequence_length=1024,
            save_contacts=True
        )
        config_manager.save_config("rna_fm", rna_fm_config)
        
        # mRNA-FM config
        mrna_fm_config = MrnaFmConfig(
            checkpoint_path=Path("./models/rna_fm/mRNA-FM_pretrained.pth"),
            max_sequence_length=1024,
            embed_dim=1280,
            ffn_embed_dim=5120
        )
        config_manager.save_config("mrna_fm", mrna_fm_config)
        
        # RhoFold config
        rhofold_config = RhoFoldConfig(
            checkpoint_path=Path("./models/rhofold/rhofold_pretrained_params.pt"),
            max_sequence_length=1000,
            use_msa=True,
            relax_steps=1000,
            save_relaxed=True,
            save_unrelaxed=True
        )
        config_manager.save_config("rhofold", rhofold_config)
        
        # RiboDiffusion config
        ribodiffusion_config = RiboDiffusionConfig(
            checkpoint_path=Path("./models/ribodiffusion/exp_inf.pth"),
            sampling_steps=200,
            n_samples=1,
            diffusion_schedule="cosine"
        )
        config_manager.save_config("ribodiffusion", ribodiffusion_config)

        # RhoDesign config
        rhodesign_config = RhoDesignConfig(
            checkpoint_path=Path("./models/rhodesign/rhodesign_best.pth"),
            max_sequence_length=300,
            temperature=1e-5
        )
        config_manager.save_config("rhodesign", rhodesign_config)

        # RnaMsM config
        rna_msm_config = RnaMSMConfig(
            checkpoint_path=Path("./models/rna_msm/rna_msm_pretrained.pth"),
            max_sequence_length=1024
        )
        config_manager.save_config("rna_msm", rna_msm_config)

        
        self.logger.info(f"Example configs created in {self.config_dir}")


config_loader = ConfigLoader()
