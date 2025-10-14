"""RiboDiffusion provider for RNA inverse folding"""

__all__ = ['RiboDiffusionAdapter']


def __getattr__(name):
    if name == 'RiboDiffusionAdapter':
        from .adapter import RiboDiffusionAdapter
        return RiboDiffusionAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
