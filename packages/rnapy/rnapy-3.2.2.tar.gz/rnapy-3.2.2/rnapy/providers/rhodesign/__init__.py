"""RhoDesign Provider for RNA Inverse Folding"""

__all__ = ['RhoDesignAdapter', 'RhoDesignConfig', 'get_rhodesign_config']


def __getattr__(name):
    if name == 'RhoDesignAdapter':
        from .adapter import RhoDesignAdapter  # Imported lazily to avoid heavy deps at import time
        return RhoDesignAdapter
    if name == 'RhoDesignConfig':
        from .config import RhoDesignConfig
        return RhoDesignConfig
    if name == 'get_rhodesign_config':
        from .config import get_rhodesign_config
        return get_rhodesign_config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}") 