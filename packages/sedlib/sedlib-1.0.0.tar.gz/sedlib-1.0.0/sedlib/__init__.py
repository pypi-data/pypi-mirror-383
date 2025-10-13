#!/usr/bin/env python

"""
sedlib: A Python library for Spectral Energy Distribution (SED) analysis

This module provides tools for managing photometric data, performing SED analysis,
and modeling stellar energy distributions with interstellar extinction correction.

Features:
    - Catalog class for organizing photometric data
    - Filter class for managing photometric filters
    - SED class for SED analysis and fitting
    - Integration with astronomical libraries like astropy and dust_extinction
    - Advanced optimization tools for interstellar extinction correction
    - BolometricCorrection class for computing bolometric corrections and radii

Author:
    Oğuzhan OKUYAN
    ookuyan@gmail.com, oguzhan.okuyan@tubitak.gov.tr

Version:
    1.0.0

License:
    Apache License 2.0
"""

__author__ = 'Oğuzhan OKUYAN'
__license__ = 'Apache License 2.0'
__version__ = '1.0.0'
__maintainer__ = 'Oğuzhan OKUYAN'
__email__ = 'ookuyan@gmail.com, oguzhan.okuyan@tubitak.gov.tr'
__description__ = "A Python library for Spectral Energy Distribution analysis"
__url__ = "https://github.com/ookuyan/sedlib"


__all__ = [
    'Filter',
    'Catalog',
    'SED',
    'BolometricCorrection'
]

from .filter import Filter
from .catalog import Catalog
from .core import SED
from .bol2rad import BolometricCorrection
