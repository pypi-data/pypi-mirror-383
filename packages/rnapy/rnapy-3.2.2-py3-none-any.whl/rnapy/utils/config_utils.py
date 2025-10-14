from typing import cast

from rnapy.core import config_loader
from rnapy.core.config import GlobalConfig, BaseConfig
from rnapy.providers.rna_fm.config import RnaFmConfig
from rnapy.providers.rhofold.config import RhoFoldConfig
from rnapy.providers.RiboDiffusion.config import RiboDiffusionConfig

def load_config(provider: str, **kwargs) -> BaseConfig:
    """
    Convenience function: load configuration

    Args:
        provider: Provider name
        **kwargs: Configuration parameters

    Returns:
        Configuration instance
    """
    return config_loader.load_provider_config(provider, **kwargs)


def get_rna_fm_config(**kwargs) -> RnaFmConfig:
    """Convenience function: get RNA-FM configuration"""
    return cast(RnaFmConfig, config_loader.load_provider_config('rna_fm', **kwargs))


def get_rhofold_config(**kwargs) -> RhoFoldConfig:
    """Convenience function: get RhoFold configuration"""
    return cast(RhoFoldConfig, config_loader.load_provider_config('rhofold', **kwargs))


def get_ribodiffusion_config(**kwargs) -> RiboDiffusionConfig:
    """Convenience function: get RiboDiffusion configuration"""
    return cast(RiboDiffusionConfig, config_loader.load_provider_config('ribodiffusion', **kwargs))


def get_global_config(**kwargs) -> GlobalConfig:
    """Convenience function: get global configuration"""
    return cast(GlobalConfig, config_loader.load_global_config(**kwargs))