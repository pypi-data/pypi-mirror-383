"""RNAPy - RNA Analysis Toolkit

RNAPy is a comprehensive toolkit for RNA sequence analysis and structure prediction. It leverages state-of-the-art machine learning models to provide accurate and efficient analysis of RNA sequences.

Main Features:
- Load and utilize pre-trained RNA models such as RNA-FM.
- Analyze RNA sequences for various properties.
- Predict RNA secondary and tertiary structures.


Example Usage:
    >>> import rnapy
    >>> 
    >>> # Initialize the toolkit
    >>> toolkit = rnapy.RNAToolkit(device="cpu")
    >>> 
    >>> # Load a pre-trained RNA model
    >>> toolkit.load_model("rna-fm", "path/to/RNA-FM_pretrained.pth")
    >>> 
    >>> # Analyze an RNA sequence
    >>> sequence = "GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCA"
    >>> result = toolkit.analyze_sequence(sequence)
    >>> 
    >>> # Predict secondary structure
    >>> structure = toolkit.predict_secondary_structure(sequence)
"""

from .toolkit import RNAToolkit
from .core import *
from . import interfaces
from . import providers

# Package metadata
__version__ = "3.1.0"
__author__ = "RNA Analysis Team"
__email__ = "contact@rnapy.org"

__all__ = [
    'RNAToolkit',

    'ModelFactory',
    'ConfigManager',

    'interfaces',
    'providers',
]
