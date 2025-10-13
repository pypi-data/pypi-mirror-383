#!/usr/bin/env python

"""
Stellar Spectral Energy Distribution Analysis.
"""

__all__ = ['SED']

# Standard library imports
import copy
import logging
import warnings
import zipfile
import traceback
from io import BytesIO
from pathlib import Path
from time import time
from datetime import datetime
from typing import Optional, Union, List
from urllib.parse import urlencode

# Third party imports
from dill import load, dump
from IPython import get_ipython
from joblib import Parallel, delayed

# Plotting
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import corner
from bokeh.plotting import figure, show as bokeh_show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool

# Scientific computing
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import simpson

# Astronomy packages
from astropy import units as u
from astropy.io import votable
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.utils.data import download_file
from astropy.utils.exceptions import AstropyWarning
from astropy.modeling.physical_models import BlackBody
from astroquery.simbad import Simbad
from dust_extinction.parameter_averages import G23, BaseExtRvModel, F99

# Local imports
from .filter import Filter
from .catalog import Catalog
from .bol2rad import BolometricCorrection
from .helper import (
    VIZIER_PHOTOMETRY_API_URL,
    get_pattern,
    _init_simbad, 
    query_gaia_parameters,
    select_preferred_filters
)
from .utils import tqdm, tqdm_joblib, InMemoryHandler


# set up warnings
warnings.simplefilter("ignore", category=AstropyWarning)
warnings.simplefilter("ignore", category=UserWarning)

# Set up logging
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
DEFAULT_LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.DEBUG

def setup_logger(
    name: str,
    log_file: Optional[Union[str, Path]] = 'sed.log',
    log_level: int = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_datefmt: str = DEFAULT_LOG_DATEFMT,
    use_file_handler: bool = False,
    use_memory_handler: bool = True,
    memory_capacity: Optional[int] = None
) -> tuple[logging.Logger, Optional[InMemoryHandler]]:
    """Set up a logger with optional file and memory handlers.
    
    Parameters
    ----------
    name : str
        Logger name
    log_file : Optional[Union[str, Path]]
        Path to log file. If None, file logging is disabled
    log_level : int
        Logging level
    log_format : str
        Log message format
    log_datefmt : str
        Date format for log messages
    use_file_handler : bool
        Whether to enable file logging
    use_memory_handler : bool
        Whether to enable in-memory logging
    memory_capacity : Optional[int]
        Maximum number of log records to store in memory (if enabled)
        If None, no limit is applied
    
    Returns
    -------
    tuple[logging.Logger, Optional[InMemoryHandler]]
        Configured logger and memory handler (if enabled)
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=log_datefmt)
    
    # Set up file handler if requested
    if use_file_handler and log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    # Set up memory handler if requested
    memory_handler = None
    if use_memory_handler:
        memory_handler = InMemoryHandler(capacity=memory_capacity)
        memory_handler.setLevel(log_level)
        memory_handler.setFormatter(formatter)
        logger.addHandler(memory_handler)
    
    return logger, memory_handler


class SED(object):
    """
    Spectral Energy Distribution (SED) analysis.

    Parameters
    ----------
    name : str, optional
        The name of the astronomical object.
    ra : str or float, optional
        The right ascension of the object.
    dec : str or float, optional
        The declination of the object.
    search_radius : `astropy.units.Quantity`, optional
        The search radius for querying the object. Default is 1 arcsecond.
    coord : `astropy.coordinates.SkyCoord`, optional
        The coordinates of the object.
    frame : str, optional
        The reference frame for the coordinates. Default is 'icrs'.
    auto_search : bool, optional
        If True, automatically performs a search for the object upon
        initialization. Default is True.
    cache : bool, optional
        If True, the data is cached. Default is True.
    timeout : int, optional
        The timeout for the query. Default is 10 seconds.
    find_basic_parameters : bool, optional
        If True, the basic parameters (distance, radius, temperature, etc.) are
        found from simbad and gaia catalogs. Default is True.
    info : bool, optional
        If True, a summary of the SED is printed. Default is True.
    log_to_file : bool, optional
        If True, log messages will be written to a file. Default is False.
    log_to_memory : bool, optional
        If True, log messages will be stored in memory. Default is True.
    log_level : int, optional
        The logging level. Default is logging.DEBUG.
    log_file : str or Path, optional
        The path to the log file. Default is 'sed.log'.
    **kwargs : dict, optional
        Additional keyword arguments to set custom attributes.

    Attributes
    ----------
    name : str
        The name of the astronomical object.
    ra : float
        The right ascension of the object in degrees.
    dec : float
        The declination of the object in degrees.
    coord : `astropy.coordinates.SkyCoord`
        The coordinates of the object.
    parallax : `astropy.units.Quantity`
        The parallax of the object.
    parallax_error : `astropy.units.Quantity`
        The error in the parallax of the object.
    distance : `astropy.units.Quantity`
        The distance to the object.
    distance_error : `astropy.units.Quantity`
        The error in the distance to the object.
    radius : `astropy.units.Quantity`
        The radius of the object.
    radius_error : `astropy.units.Quantity`
        The error in the radius of the object.
    teff : `astropy.units.Quantity`
        The temperature of the object.
    teff_error : `astropy.units.Quantity`
        The error in the temperature of the object.
    ebv : float
        The extinction of the object.
    ebv_error : float
        The error in the extinction of the object.
    ext_model : `sedlib.extinction.ExtinctionModel`
        The extinction model used.
    catalog : `sedlib.catalog.Catalog`
        The catalog of the object.

    Methods
    -------
    add_photometry()
        Add photometric data to the SED.
    filter_outliers()
        Filter outlier points from the SED using sigma clipping.
    estimate_radius()
        Estimate the radius of the object.
    estimate_ebv()
        Estimate the extinction of the object.
    compute_A_lambda()
        Compute the extinction at a given wavelength.
    compute_absolute_magnitude()
        Compute the absolute magnitude of the object.
    plot()
        Plot the SED with blackbody and/or extinction.
    save()
        Save the SED to a file.
    load()
        Load the SED from a file.
    get_logs()
        Get all stored log records.
    dump_logs()
        Dump all stored log records to a file.
    clear_logs()
        Clear all stored log records.
    run()
        Run the SED analysis.
    export_result()
        Export the SED analysis results as a dictionary.

    Raises
    ------
    TypeError
        If the input parameters have incorrect types.
    ValueError
        If `search_radius` is greater than 30 arcseconds or if only one of `ra`
        or `dec` is provided.
    FileNotFoundError
        If the specified file in `load` parameter does not exist.
    OSError
        If there are issues reading the file specified in `load` parameter.
    ConnectionError
        If there are network connectivity issues during auto-search.
    TimeoutError
        If the query times out during auto-search.
    astroquery.exceptions.RemoteServiceError
        If there are issues with remote service during catalog queries.
    AttributeError
        If the object has no name or coordinates.

    Examples
    --------
    >>> from astropy import units as u
    >>>
    >>> from sedlib import SED
    >>> from sedlib import BolometricCorrection
    >>>
    >>> sed = SED(name='Vega')
    >>> sed.teff = 10070 * u.K
    >>> sed.teff_error = sed.teff * 0.01
    >>>
    >>> # filter the catalog from missing or bad data
    >>> sed.filter_outliers(sigma_threshold=3.0, over_write=True, plot=True)
    >>> sed.catalog.delete_missing_data_rows('filter')
    >>> sed.catalog.delete_missing_data_rows('eflux')
    >>> sed.catalog.delete_rows({'eflux': '==0'})
    >>>
    >>> # combine the fluxes of the same filter
    >>> sed.catalog.combine_fluxes(method='mean', overwrite=True)
    >>>
    >>> # estimate the radius of the object
    >>> sed.estimate_radius(accept=True)
    >>>
    >>> # Plot the SED with blackbody
    >>> sed.plot(with_blackbody=True, show=True)
    >>>
    >>> # estimate the extinction
    >>> sed.estimate_ebv()
    >>>
    >>> # Plot the SED with extinction
    >>> sed.plot(with_blackbody=True, with_extinction=True, show=True)
    >>>
    >>> # Calculate the bolometric correction and find refined radius
    >>> bc = BolometricCorrection(sed)
    >>> bc.run()
    >>>
    >>> # Plot the SED with blackbody and extinction
    >>> sed.plot(with_blackbody=True, with_extinction=True, show=True)
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ra: Optional[Union[str, float]] = None,
        dec: Optional[Union[str, float]] = None,
        search_radius: u.Quantity = 1 * u.arcsec,
        coord: Optional[SkyCoord] = None,
        frame: str = 'icrs',
        auto_search: bool = True,
        cache: bool = True,
        find_basic_parameters: bool = True,
        timeout: int = 10,
        info: bool = True,
        log_to_file: bool = False,
        log_to_memory: bool = True,
        log_level: int = DEFAULT_LOG_LEVEL,
        log_file: Optional[Union[str, Path]] = 'sed.log',
        **kwargs
    ):
        # Set up logging
        self._logger, self._memory_handler = setup_logger(
            f"{__name__}.{id(self)}",
            log_file=log_file,
            use_file_handler=log_to_file,
            use_memory_handler=log_to_memory,
            log_level=log_level
        )

        self._logger.info(
            f"BEGIN - Initializing SED object with name: {name}, "
            f"ra: {ra}, dec: {dec}, search_radius: {search_radius}"
        )

        # Type checking for input parameters
        type_checks = {
            'name': (str, type(None)),
            'ra': (str, float, type(None)),
            'dec': (str, float, type(None)),
            'search_radius': u.Quantity,
            'coord': (SkyCoord, type(None)),
            'frame': str,
            'auto_search': bool,
            'cache': bool,
            'find_basic_parameters': bool,
            'timeout': int,
            'info': bool,
        }

        self._logger.debug(
            "Validating input parameter types for all constructor arguments"
        )
        for param, expected_type in type_checks.items():
            value = locals()[param]
            if not isinstance(value, expected_type):
                self._logger.error(
                    f"Type validation failed for {param} - expected "
                    f"{expected_type}, got {type(value)}"
                )
                raise TypeError(f'`{param}` must be {expected_type} object.')

        if search_radius > 30 * u.arcsec:
            self._logger.error(
                f"Search radius validation failed - {search_radius} exceeds "
                "maximum allowed value of 30 arcsec"
            )
            raise ValueError('`radius` must be lower than 30 arcsecond')

        # identifier
        self._name = name
        self._user_provided_name = name

        # coordinates
        self._ra = ra
        self._dec = dec
        self._search_radius = search_radius
        self._coord = coord
        self._frame = frame

        # Attributes
        self._parallax = None
        self._parallax_error = None
        self._distance = None
        self._distance_error = None
        self._radius = None
        self._initial_radius = None
        self._radius_error = None
        self._initial_radius_error = None
        self._radius_lower = None
        self._radius_upper = None
        self._ext_model = None
        self._ebv = None
        self._ebv_error = None
        self._ebv_rms = None
        self._logg = None
        self._logg_error = None
        self._teff = None
        self._initial_teff = None
        self._teff_error = None
        self._initial_teff_error = None
        self._teff_gaia = None
        self._teff_gaia_error = None
        self._teff_lower = None
        self._teff_upper = None
        self._fbol = None
        self._fbol_error = None
        self._mbol = None
        self._mbol_error = None
        self._Mbol = None
        self._Mbol_error = None
        self._Lbol = None
        self._Lbol_error = None

        self._catalog = None
        self._result = None
        self._simbad_result = None
        self._bc = None

        # internal attributes
        self._find_basic_parameters = find_basic_parameters
        self._cache = cache
        self._timeout = timeout
        self._info = info

        # for plotting results
        self._radius_grid_search_results_for_plotting = None
        self._radius_mc_results_for_plotting = None
        self._ebv_mc_results_for_plotting = None

        # units
        self._wavelength_unit = u.um
        self._flux_unit = u.erg / u.s / u.cm**2 / u.AA
        # self._flux_unit = u.erg / (u.cm ** 2 * u.AA * u.s * u.sr)

        self._selected_filters_for_radius_estimation = [
            "2MASS:H", "2MASS:J", "2MASS:Ks",
            "Johnson:J", "Johnson:H", "Johnson:K",
            "WISE:W1", "WISE:W2"
        ]

        self._logger.debug(
            "Setting default wavelength and flux units for SED calculations"
        )

        for key, val in kwargs.items():
            self.__dict__[key] = val

        if (self._ra is not None) != (self._dec is not None):  # xor :)
            self._logger.error(
                "Coordinate validation failed - RA and DEC must both be provided "
                "or both be None"
            )
            raise ValueError('`ra` and `dec` must be defined together.')

        # Convert RA and DEC to SkyCoord if provided
        if (self._ra is not None) and (self._dec is not None):
            self._logger.debug(
                f"Converting RA ({self._ra}) and DEC ({self._dec}) to SkyCoord "
                f"with frame {self._frame}"
            )
            unit = [u.hourangle, u.deg]

            if isinstance(self._ra, u.Quantity):
                unit[0] = self._ra.unit

            if isinstance(self._dec, u.Quantity):
                unit[1] = self._dec.unit

            self._coord = SkyCoord(
                self._ra, self._dec, unit=unit, frame=self._frame
            )

        # Extract RA and DEC from SkyCoord if provided
        if self._coord is not None:
            self._logger.debug(
                f"Extracting RA and DEC from provided SkyCoord object: "
                f"{self._coord}"
            )
            self._ra = self._coord.icrs.ra.deg
            self._dec = self._coord.icrs.dec.deg

        # Determine if the object is searchable
        is_searchable = False
        for key in ['_name', '_ra', '_dec', '_coord']:
            if self.__dict__[key] is not None:
                is_searchable = True
                break
        
        # Perform auto search if enabled and object is searchable
        if auto_search and is_searchable:
            self._logger.info(
                f"Performing auto search for object with auto_search={auto_search}"
                f" and find_basic_parameters={find_basic_parameters}"
            )
            self._init_query()

        self._logger.info("END - SED object initialization complete")

    @property
    def name(self):
        """
        str: The name of the astronomical object.
        """
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError(f'"{value}" must be str object')

        self._name = value
        self._init_query()

    @property
    def ra(self):
        """
        `astropy.units.Quantity`: The right ascension of the object in degrees.
        """
        return self._ra

    @ra.setter
    def ra(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`ra` must be `Quantity` object.')

        self._ra = value

    @property
    def dec(self):
        """
        `astropy.units.Quantity`: The declination of the object in degrees.
        """
        return self._dec

    @dec.setter
    def dec(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`dec` must be `Quantity` object.')

        self._dec = value
    
    @property
    def parallax(self):
        """
        `astropy.units.Quantity`: The parallax of the object.
        """
        return self._parallax

    @property
    def parallax_error(self):
        """
        `astropy.units.Quantity`: The error in the parallax of the object.
        """
        return self._parallax_error

    @parallax.setter
    def parallax(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`parallax` must be `Quantity` object.')

        self._parallax = value
        
        try:
            self._catalog.parallax = value
        except Exception as e:
            self._logger.warning(f"parallax is not set in the catalog")

    @parallax_error.setter
    def parallax_error(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`parallax_error` must be `Quantity` object.')

        self._parallax_error = value
        
        try:
            self._catalog.parallax_error = value
        except Exception as e:
            self._logger.warning(f"parallax_error is not set in the catalog")

    @property
    def distance(self):
        """
        `astropy.units.Quantity`: The distance to the object.
        """
        return self._distance

    @property
    def distance_error(self):
        """
        `astropy.units.Quantity`: The error in the distance to the object.
        """
        return self._distance_error

    @distance_error.setter
    def distance_error(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`distance_error` must be `Quantity` object.')

        self._distance_error = value
        
        try:
            self._catalog.distance_error = value
        except Exception as e:
            self._logger.warning(f"distance_error is not set in the catalog")

    @distance.setter
    def distance(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`distance` must be `Quantity` object.')

        if not (
            value.unit.is_equivalent(u.pc)
            or value.unit.is_equivalent(u.km)
        ):
            raise ValueError(
                "'distance' must have units of parsecs or kilometers."
            )

        self._distance = value
        
        try:
            self._catalog.distance = value
        except Exception as e:
            self._logger.warning(f"distance is not set in the catalog")

    @property
    def teff(self):
        """
        `astropy.units.Quantity`: The temperature of the object.
        """
        return self._teff

    @teff.setter
    def teff(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`teff` must be `Quantity` object.')
        
        if not value.unit.is_equivalent(u.K):
            raise ValueError('`teff` must have units of Kelvin.')

        self._initial_teff = value
        self._teff = value

        try:
            self._catalog.teff = value
        except Exception as e:
            self._logger.warning(f"teff is not set in the catalog")

    @property
    def teff_error(self):
        """
        `astropy.units.Quantity`: The error in the temperature of the object.
        """
        return self._teff_error

    @teff_error.setter
    def teff_error(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`teff_error` must be `Quantity` object.')

        self._initial_teff_error = value
        self._teff_error = value

        try:
            self._catalog.teff_error = value
        except Exception as e:
            self._logger.warning(f"teff_error is not set in the catalog")
    
    @property
    def teff_lower(self):
        """
        `astropy.units.Quantity`: The lower limit of the temperature of the 
        object.
        """
        return self._teff_lower

    @teff_lower.setter
    def teff_lower(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`teff_lower` must be `Quantity` object.')

        self._teff_lower = value

    @property
    def teff_upper(self):
        """
        `astropy.units.Quantity`: The upper limit of the temperature of the 
        object.
        """
        return self._teff_upper

    @teff_upper.setter
    def teff_upper(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`teff_upper` must be `Quantity` object.')

        self._teff_upper = value

    @property
    def radius(self):
        """
        `astropy.units.Quantity`: The radius of the object.
        """
        return self._radius

    @property
    def radius_error(self):
        """
        `astropy.units.Quantity`: The radius error of the object.
        """
        return self._radius_error

    @radius.setter
    def radius(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`radius` must be `Quantity` object.')

        self._initial_radius = value
        self._radius = value
        try:
            self._catalog.radius = value
        except Exception as e:
            self._logger.warning(f"radius is not set in the catalog")
        
    @radius_error.setter
    def radius_error(self, value):
        if not isinstance(value, u.Quantity):
            raise TypeError('`radius_error` must be `Quantity` object.')

        self._initial_radius_error = value
        self._radius_error = value

        try:
            self._catalog.radius_error = value
        except Exception as e:
            self._logger.warning(f"radius_error is not set in the catalog")
    
    @property
    def ebv(self):
        """
        float or None: extinction in E(B-V)
        """
        return self._ebv
    
    @ebv.setter
    def ebv(self, value):
        if not isinstance(value, (float, type(None))):
            raise TypeError('`ebv` must be float or None object.')
        
        self._ebv = value
    
    @property
    def ebv_error(self):
        """
        float or None: error in E(B-V)
        """
        return self._ebv_error
    
    @ebv_error.setter
    def ebv_error(self, value):
        if not isinstance(value, (float, type(None))):
            raise TypeError('`ebv_error` must be float or None object.')
        
        self._ebv_error = value

    @property
    def ext_model(self):
        """
        `dust_extinction.baseclasses.BaseExtRvModel`: The extinction model.
        """
        return self._ext_model
    
    @ext_model.setter
    def ext_model(self, value):
        if not isinstance(value, BaseExtRvModel):
            raise TypeError('`ext_model` must be `BaseExtRvModel` object.')
        
        self._ext_model = value

    @property
    def coord(self):
        """
        `astropy.coordinates.SkyCoord`: The coordinates of the object.
        """
        return self._coord

    @coord.setter
    def coord(self, c):
        if not isinstance(c, SkyCoord):
            raise TypeError('`coord` must be `SkyCoord` object.')

        self._coord = c
        self._init_query()

    @property
    def search_radius(self):
        """
        `astropy.units.Quantity`: The search radius for querying the object.
        """
        return self._search_radius

    @search_radius.setter
    def search_radius(self, r):
        if not isinstance(r, u.Quantity):
            raise TypeError('`search_radius` must be `Quantity` object.')

        if r > 30 * u.arcsec:
            raise ValueError('`search_radius` must be lower than 30 arcsecond')

        self._search_radius = r
        self._init_query()

    @property
    def catalog(self):
        """
        `astropy.table.Table`: The photometry catalog of the object.
        """
        return self._catalog

    @property
    def result(self):
        """
        `dict`: The result of SED analysis pipeline.
        """
        return self._result

    def _init_query(self):
        """
        Initialize the query process for retrieving object data.

        Warning
        -------
        Internal method only, not suitable for direct use.

        This internal method sets up the initial query to SIMBAD and optionally Gaia,
        populating basic parameters of the object. It is called automatically when
        coordinates or search radius are updated.
        """
        self._logger.info(
            f"BEGIN - Initializing query process for object: {self._name}"
        )

        _init_simbad()
        self._logger.debug("Initialized SIMBAD connection for astronomical queries")

        # Query SIMBAD by name or coordinates
        target = self._name
        if target:
            self._logger.debug(f"Querying SIMBAD database by object name: {target}")
            self._simbad_result = Simbad.query_object(target)

        if (self._ra is not None) and (self._dec is not None):
            target = f'{self._ra},{self._dec}'
            self._logger.debug(
                f"Querying SIMBAD database by coordinates: "
                f"RA={self._ra}, DEC={self._dec}, radius={self._search_radius}"
            )
            self._simbad_result = Simbad.query_region(
                self._coord, radius=self._search_radius
            )

        # check if object not found in SIMBAD
        if len(self._simbad_result) == 0:
            self._logger.error(
                f"SIMBAD query failed - Object '{self._name}' not found in SIMBAD "
                "database"
            )

        # Handle multiple SIMBAD results
        if len(self._simbad_result) > 1:
            self._logger.warning(
                f"Found {len(self._simbad_result)} SIMBAD results. "
                "Using the first match by default."
            )
            self._simbad_result = self._simbad_result[0]

        # check if object found in SIMBAD
        if len(self._simbad_result) == 1:
            # Extract relevant SIMBAD attributes if available
            simbad_attrs = {
                '_name': 'main_id',
                '_parallax': 'plx_value',
                '_parallax_error': 'plx_err',
                '_ra': 'ra',
                '_dec': 'dec'
            }
            for attr, key in simbad_attrs.items():
                try:
                    setattr(self, attr, self._simbad_result[key][0])
                except (KeyError, IndexError):
                    self._logger.debug(
                        f"No value found in SIMBAD for attribute {attr} (key={key})"
                    )

        # Query Gaia for more accurate parameters
        if self._find_basic_parameters:
            self._logger.debug(
                f"Querying Gaia DR3 database for additional parameters for object: "
                f"{self._name}"
            )
            gaia_params = query_gaia_parameters(
                self._name,
                search_simbad=(len(self._simbad_result) == 1)
            )

            if gaia_params is None:
                self._logger.warning(
                    "Gaia DR3 query returned no results or failed. "
                    "Unable to retrieve parameters from Gaia."
                )
                self._logger.info("Falling back to SIMBAD parallax values if available.")
            else:
                self._logger.debug(
                    f"Successfully retrieved parameters from Gaia DR3: "
                    f"{list(gaia_params.keys())}"
                )
                if 'parallax' in gaia_params:
                    self._logger.debug(
                        f"Setting parallax from Gaia: {gaia_params['parallax']} ± "
                        f"{gaia_params['parallax_error']} mas"
                    )
                    self._parallax = gaia_params['parallax'] * u.mas
                    self._parallax_error = gaia_params['parallax_error'] * u.mas
                
                if 'ra' in gaia_params:
                    self._logger.debug(
                        f"Setting RA from Gaia: {gaia_params['ra']} deg"
                    )
                    self._ra = gaia_params['ra'] * u.deg
                
                if 'dec' in gaia_params:
                    self._logger.debug(
                        f"Setting DEC from Gaia: {gaia_params['dec']} deg"
                    )
                    self._dec = gaia_params['dec'] * u.deg

                if 'teff' in gaia_params:
                    self._logger.debug(
                        f"Setting effective temperature from Gaia: "
                        f"{gaia_params['teff']} K (range: "
                        f"{gaia_params['teff_lower']}-{gaia_params['teff_upper']} K)"
                    )
                    self._teff = gaia_params['teff'] * u.K
                    self._initial_teff = gaia_params['teff'] * u.K

                    self._teff_lower = gaia_params['teff_lower'] * u.K
                    self._teff_upper = gaia_params['teff_upper'] * u.K
                    # symmetric temperature error
                    self._teff_error = (self._teff_upper - self._teff_lower) / 2
                    self._initial_teff_error = (
                        self._teff_upper - self._teff_lower
                    ) / 2
                if 'radius' in gaia_params:
                    self._logger.debug(
                        f"Setting radius from Gaia: {gaia_params['radius']} Rsun "
                        f"(range: {gaia_params['radius_lower']}-"
                        f"{gaia_params['radius_upper']} Rsun)"
                    )
                    self._radius = gaia_params['radius'] * u.Rsun
                    self._initial_radius = gaia_params['radius'] * u.Rsun

                    self._radius_lower = gaia_params['radius_lower'] * u.Rsun
                    self._radius_upper = gaia_params['radius_upper'] * u.Rsun
                    # symmetric radius error
                    self._radius_error = (
                        self._radius_upper - self._radius_lower
                    ) / 2
                    self._initial_radius_error = (
                        self._radius_upper - self._radius_lower
                    ) / 2
        else:
            self._logger.debug(
                "Skipping Gaia query as find_basic_parameters=False. "
            )
            if len(self._simbad_result) == 0:
                self._logger.warning(
                    "Without continue simbad query. "
                    "User must provide basic parameters manually."
                )
        
        if self._parallax is not None:
            self._logger.debug(f"Computing distance from parallax: {self._parallax}")
            self._parallax *= (
                u.mas if not isinstance(self._parallax, u.Quantity) else 1
            )
            self._distance = self._parallax.to(
                u.pc, equivalencies=u.parallax()
            )

            if self._parallax_error is not None:
                self._logger.debug(
                    f"Computing distance error from parallax error: "
                    f"{self._parallax_error}"
                )
                self._parallax_error *= (
                    u.mas if not isinstance(self._parallax_error, u.Quantity) else 1
                )
                rel_plx_err = (
                    self._parallax_error / self._parallax
                ).decompose()
                self._distance_error = self._distance * rel_plx_err
            else:
                self._logger.debug(
                    "No parallax error available from SIMBAD or Gaia. "
                    "Distance error will be None."
                )
        else:
            self._logger.warning(
                "No parallax data found in either SIMBAD or Gaia. "
                "Unable to compute distance."
            )
            self._distance = None
            self._distance_error = None

        self._logger.debug(
            f"Final parameter values - parallax: {self._parallax} ± "
            f"{self._parallax_error}, distance: {self._distance} ± "
            f"{self._distance_error}"
        )
        if self._teff is not None:
            self._logger.debug(
                f"Final effective temperature: {self._teff} ± {self._teff_error}"
            )
        if self._radius is not None:
            self._logger.debug(
                f"Final stellar radius: {self._radius} ± {self._radius_error}"
            )

        # Query VizieR (photometry) if the object is found in SIMBAD
        self._logger.info(
            f"Starting VizieR photometry query for target: {target}, "
            f"search radius: {self._search_radius}"
        )
        query_params = {
            '-c': target if self._find_basic_parameters else self._name,
            '-c.rs': self._search_radius.to(u.arcsec).value
        }
        url = f'{VIZIER_PHOTOMETRY_API_URL}?{urlencode(query_params)}'
        self._logger.debug(f"VizieR query URL constructed: {url}")

        try:
            # Download and parse the VizieR data
            self._logger.debug(
                f"Downloading data from VizieR with timeout={self._timeout}s, "
                f"cache={self._cache}"
            )
            path = download_file(
                url, cache=self._cache,
                timeout=self._timeout,
                allow_insecure=True
            )
            self._logger.info(
                f"Successfully downloaded photometry data from VizieR: {url}"
            )

            try:
                with open(path, 'r') as f:
                    text = f.read()

                self._logger.debug(
                    "Parsing VizieR VOTable data into Astropy table"
                )
                self._raw_catalog = votable.parse_single_table(
                    BytesIO(text.encode())
                ).to_table()
            except Exception as e:
                self._logger.warning(
                    f"Error parsing VizieR VOTable data: {e}"
                )
                self._logger.warning(
                    f"Trying to parse the file directly: {path}"
                )

                # Add missing XML closing tags
                text += "</TABLEDATA></DATA></TABLE></RESOURCE></VOTABLE>"
                self._logger.warning("Added missing XML closing tags")

                try:
                    self._raw_catalog = votable.parse_single_table(
                        BytesIO(text.encode())
                    ).to_table()
                except Exception as e:
                    self._logger.error(
                        f"Error parsing VizieR VOTable data: {e}"
                    )
                    raise

            self._logger.debug("Preparing catalog by organizing and standardizing data")
            self._catalog = self._prepare_catalog()
            self._catalog.flux_to_magnitude()

            self._logger.debug("Assigning stellar parameters to catalog")
            self._catalog.teff = self._teff
            self._catalog.teff_error = self._teff_error
            self._catalog.radius = self._radius
            self._catalog.radius_error = self._radius_error
            self._catalog.distance = self._distance
            self._catalog.distance_error = self._distance_error

            if self._info:
                self._logger.debug("Displaying summary information as info=True")
                self.summary()

            self._logger.info(
                "END - Query process complete with successful catalog "
                "preparation"
            )

        except Exception as e:
            self._logger.error(f"Error during VizieR query for {target}: {str(e)}")
            self._raw_catalog = None
            self._catalog = None
            raise ValueError(f'{target} not found!')

    def initialize_with_user_data(self, raw_catalog=None):
        """
        Initialize an SED object with user-provided stellar parameters.
        
        This method validates user-supplied parameters and retrieves photometry data
        from VizieR without performing additional queries to astronomical databases
        like SIMBAD or Gaia. It should be called after manually setting all required
        parameters on an SED instance that was initialized with auto_search=False.
        
        Required parameters:
            - name, ra, dec
            - Either (parallax, parallax_error) or (distance, distance_error)
            - radius, radius_error
            - teff, teff_error
        
        If only one of the distance/parallax pairs is provided, the missing pair
        will be calculated automatically.
        
        Warning
        -------
        This method is for use only when auto_search=False was set during initialization.
        For normal usage (auto_search=True), the standard initialization process is
        automatically performed during object creation.

        Parameters
        ----------
        raw_catalog : astropy.table.Table, optional
            The raw catalog to use for the SED object.
        
        Example
        -------
        >>> sed = SED(name="Vega", auto_search=False)
        >>> sed.ra = 279.23473479 * u.deg
        >>> sed.dec = 38.78368896 * u.deg
        >>> sed.teff = 9600 * u.K
        >>> sed.teff_error = 100 * u.K
        >>> sed.distance = 7.68 * u.pc
        >>> sed.distance_error = 0.02 * u.pc
        >>> sed.radius = 2.72 * u.Rsun
        >>> sed.radius_error = 0.05 * u.Rsun
        >>> sed.initialize_with_user_data()
        """
        self._logger.info(
            "BEGIN - Processing user-provided parameters "
            "and retrieving photometry"
        )
        
        # Check if user provided the required parameters
        # 1. Basic identification parameters
        required_params = {
            'name': self._name,
            'ra': self._ra,
            'dec': self._dec
        }
        
        missing_ids = [
            param for param, value in required_params.items() if value is None
        ]
        if missing_ids:
            self._logger.error(
                f"Missing required identification parameters: "
                f"{', '.join(missing_ids)}"
            )
            raise ValueError(
                f"User must provide all of the following parameters: "
                f"{', '.join(missing_ids)}"
            )
        
        # 2. Check coordinates have proper units
        if not isinstance(self._ra, u.Quantity) and not isinstance(
            self._ra, (int, float)
        ):
            self._logger.error(f"Invalid RA type: {type(self._ra).__name__}")
            raise TypeError("RA must be a Quantity or a numeric value.")
            
        if not isinstance(self._dec, u.Quantity) and not isinstance(
            self._dec, (int, float)
        ):
            self._logger.error(f"Invalid DEC type: {type(self._dec).__name__}")
            raise TypeError("DEC must be a Quantity or a numeric value.")
        
        # Ensure we have a SkyCoord object
        if self._coord is None:
            self._logger.debug("Creating SkyCoord from provided RA and DEC")
            unit = [u.deg, u.deg]
            
            if isinstance(self._ra, u.Quantity):
                unit[0] = self._ra.unit
                
            if isinstance(self._dec, u.Quantity):
                unit[1] = self._dec.unit
                
            self._coord = SkyCoord(
                self._ra, self._dec, unit=unit, frame=self._frame
            )
            
        # 3. Check temperature parameters
        if self._teff is None or self._teff_error is None:
            self._logger.error("Missing required temperature parameters")
            raise ValueError("User must provide both teff and teff_error")
            
        # Verify temperature has proper units
        if not isinstance(self._teff, u.Quantity):
            self._logger.debug("Converting teff to Quantity with K unit")
            self._teff = self._teff * u.K
            
        if not isinstance(self._teff_error, u.Quantity):
            self._logger.debug("Converting teff_error to Quantity with K unit")
            self._teff_error = self._teff_error * u.K
        
        # 4. Check radius parameters
        if self._radius is None or self._radius_error is None:
            self._logger.error("Missing required radius parameters")
            raise ValueError("User must provide both radius and radius_error")
            
        # Verify radius has proper units
        if not isinstance(self._radius, u.Quantity):
            self._logger.debug("Converting radius to Quantity with Rsun unit")
            self._radius = self._radius * u.Rsun
            
        if not isinstance(self._radius_error, u.Quantity):
            self._logger.debug("Converting radius_error to Quantity with Rsun unit")
            self._radius_error = self._radius_error * u.Rsun
        
        # 5. Check distance/parallax parameters
        has_distance = (
            self._distance is not None and self._distance_error is not None
        )
        has_parallax = (
            self._parallax is not None and self._parallax_error is not None
        )
        
        if not (has_distance or has_parallax):
            self._logger.error("Missing required distance information")
            raise ValueError(
                "User must provide either (distance and distance_error) or "
                "(parallax and parallax_error)"
            )
        
        # Convert between distance and parallax if one pair is missing
        if has_parallax and not has_distance:
            self._logger.debug("Computing distance from user-provided parallax")
            
            # Ensure parallax has proper units
            if not isinstance(self._parallax, u.Quantity):
                self._parallax = self._parallax * u.mas
                
            if not isinstance(self._parallax_error, u.Quantity):
                self._parallax_error = self._parallax_error * u.mas
            
            # Convert parallax to distance
            self._distance = self._parallax.to(
                u.pc, equivalencies=u.parallax()
            )
            
            # Compute distance error from parallax error
            rel_plx_err = (self._parallax_error / self._parallax).decompose()
            self._distance_error = self._distance * rel_plx_err
            
            self._logger.debug(
                f"Calculated distance: {self._distance} ± {self._distance_error}"
            )
        elif has_distance and not has_parallax:
            self._logger.debug("Computing parallax from user-provided distance")
            
            # Ensure distance has proper units
            if not isinstance(self._distance, u.Quantity):
                self._distance = self._distance * u.pc
                
            if not isinstance(self._distance_error, u.Quantity):
                self._distance_error = self._distance_error * u.pc
            
            # Convert distance to parallax
            self._parallax = self._distance.to(
                u.mas, equivalencies=u.parallax()
            )
            
            # Compute parallax error from distance error
            rel_dist_err = (self._distance_error / self._distance).decompose()
            self._parallax_error = self._parallax * rel_dist_err
            
            self._logger.debug(
                f"Calculated parallax: {self._parallax} ± {self._parallax_error}"
            )
        
        # Ensure all parameters have appropriate units
        if not isinstance(self._distance, u.Quantity):
            self._distance = self._distance * u.pc
            
        if not isinstance(self._distance_error, u.Quantity):
            self._distance_error = self._distance_error * u.pc
        
        # Log all parameters that will be used
        self._logger.debug(
            f"Using user-provided parameters - Name: {self._name}, "
            f"Coordinates: RA={self._ra}, DEC={self._dec}, "
            f"Temperature: {self._teff} ± {self._teff_error}, "
            f"Radius: {self._radius} ± {self._radius_error}, "
            f"Distance: {self._distance} ± {self._distance_error}, "
            f"Parallax: {self._parallax} ± {self._parallax_error}"
        )
        
        # Query VizieR for photometry data
        target = self._name
        self._logger.error(f"Starting VizieR photometry query for {target}")
        # target = f"{self._coord.icrs.ra.deg},{self._coord.icrs.dec.deg}"
        # self._logger.info(
        #     f"Starting VizieR photometry query for coordinates: {target}, "
        #     f"search radius: {self._search_radius}"
        # )
        
        if raw_catalog is None:
            query_params = {
                '-c': target,
                '-c.rs': self._search_radius.to(u.arcsec).value
            }
            url = f'{VIZIER_PHOTOMETRY_API_URL}?{urlencode(query_params)}'
            self._logger.debug(f"VizieR query URL constructed: {url}")
        
        try:
            if raw_catalog is None:
                # Download and parse the VizieR data
                self._logger.debug(
                    f"Downloading data from VizieR with timeout={self._timeout}s, "
                    f"cache={self._cache}"
                )
                path = download_file(
                    url,
                    cache=self._cache,
                    timeout=self._timeout,
                    allow_insecure=True
                )
                self._logger.info(
                    f"Successfully downloaded photometry data from VizieR: {url}"
                )
                
                with open(path, 'r') as f:
                    text = f.read()
                
                try:
                    self._logger.debug(
                        "Parsing VizieR VOTable data into Astropy table"
                    )
                    self._raw_catalog = votable.parse_single_table(
                        BytesIO(text.encode())
                    ).to_table()
                except Exception as e:
                    self._logger.warning(
                        f"Error parsing VizieR VOTable data: {e}"
                    )
                    # Add missing XML closing tags
                    text += "</TABLEDATA></DATA></TABLE></RESOURCE></VOTABLE>"
                    self._logger.warning("Added missing XML closing tags")

                    try:
                        self._raw_catalog = votable.parse_single_table(
                            BytesIO(text.encode())
                        ).to_table()
                    except Exception as e:
                        self._logger.error(
                            f"Error parsing VizieR VOTable data: {e}"
                        )
                        raise
            else:
                self._raw_catalog = raw_catalog

            self._logger.debug(
                "Preparing catalog by organizing and standardizing data"
            )
            self._catalog = self._prepare_catalog()
            self._catalog.flux_to_magnitude()
            
            # Assign user-provided stellar parameters to catalog
            self._logger.debug(
                "Assigning user-provided stellar parameters to catalog"
            )

            self._catalog.teff = self._teff
            self._catalog.teff_error = self._teff_error
            self._catalog.radius = self._radius
            self._catalog.radius_error = self._radius_error
            self._catalog.distance = self._distance
            self._catalog.distance_error = self._distance_error
            
            # Display summary if info is enabled
            if self._info:
                self._logger.debug("Displaying summary information as info=True")
                self.summary()
                
            self._logger.info(
                "END - Successfully retrieved photometry "
                "data using user-provided parameters"
            )
            
        except Exception as e:
            self._logger.error(
                f"Error during VizieR query for {target}: {str(e)}"
            )
            self._raw_catalog = None
            self._catalog = None
            raise RuntimeError(
                f"Failed to retrieve photometry data: {str(e)}"
            )

    def _prepare_catalog(self):
        """
        Prepare the catalog.

        Warning
        -------
        Internal method only, not suitable for direct use.

        Returns
        -------
        `astropy.table.Table`
            The table with prepared catalog.
        """
        self._logger.info(
            "BEGIN - Preparing photometric catalog data"
        )

        t = self._raw_catalog.copy()
        self._logger.debug(
            "Created copy of raw catalog data to preserve original"
        )

        # Create a lookup dictionary for filters
        lookup = dict()
        self._logger.debug(
            "Initializing Filter object for photometric system identification"
        )
        f = Filter()
        self._logger.debug("Initialized Filter object")
        
        fts = {tuple(row.split(':')) for row in set(t['sed_filter'].tolist())}
        self._logger.debug(f"Found {len(fts)} unique filters")

        for item in tqdm(fts, desc="Fetching filter data from SVO", disable=not self._info):
            try:
                system, filter_name = item
                pattern = get_pattern(system, filter_name)
            except ValueError:
                continue

            result = f.search(pattern)
            len_result = len(result)
    
            if len_result == 1:
                lookup[f'{system}:{filter_name}'] = Filter(name=result[0])

        self._logger.debug(f"Created lookup dictionary with {len(lookup)} filters")

        for column_name in t.colnames:
            if '_tab1_' in column_name:
                t.remove_column(column_name)
        self._logger.debug("Removed unnecessary columns")

        columns = {
            '_RAJ2000': 'RA', '_DEJ2000': 'DEC',
            '_tabname': 'vizier_table', '_ID': 'vizier_record',
            'sed_freq': 'frequency', 'sed_flux': 'flux',
            'sed_eflux': 'eflux', 'sed_filter': 'vizier_filter'
        }

        t.rename_columns(list(columns.keys()), list(columns.values()))
        self._logger.debug("Renamed columns")

        # Add filter and wavelength information to the catalog
        t['filter'] = np.full(len(t), None, dtype=object)
        t['wavelength'] = t['frequency'].to(
            self._wavelength_unit, equivalencies=u.spectral()
        )
        t['wavelength'].description = 'Wavelength in Micrometers'
        self._logger.debug("Added wavelength column")

        # Sort the table by wavelength in ascending order
        t.sort('wavelength')
        self._logger.debug("Sorted table by wavelength")

        # Convert flux and eflux to the specified unit
        t['flux'] = t['flux'].to(
            self._flux_unit,
            equivalencies=u.spectral_density(
                t['wavelength'].value*t['wavelength'].unit
            )
        )
        t['flux'].description = (
            f'Flux in {self._flux_unit.to_string("unicode")}'
        )

        t['eflux'] = t['eflux'].to(
            self._flux_unit,
            equivalencies=u.spectral_density(
                t['wavelength'].value*t['wavelength'].unit
            )
        )
        t['eflux'].description = (
            f'Error in {self._flux_unit.to_string("unicode")}'
        )
        self._logger.debug("Converted flux units")

        for vizier_filter, filter_obj in lookup.items():
            idx = np.where(t['vizier_filter'] == vizier_filter)
            t['filter'][idx] = filter_obj
        self._logger.debug("Mapped filters to catalog entries")

        self._logger.info("END - Preparing photometric catalog data")

        return Catalog(
            table=t, name=self._name, ra=self._ra, dec=self._dec,
            radius=self._search_radius, coord=self._coord, logger=self._logger
        )

    def add_photometry(self, filter_name, mag, mag_error=None, final_table=False):
        """
        Add a photometric measurement to the catalog.
        
        This method allows manual addition of photometric data points to the 
        star's catalog. The magnitude is converted to flux using the specified
        filter's response function, and the data is automatically sorted by
        wavelength after insertion.
        
        Parameters
        ----------
        filter_name : str
            Name of the photometric filter (e.g., 'V', 'J', 'WISE.W1').
            Must be a valid filter name recognized by the Filter class.
        mag : float
            Magnitude value in the specified filter.
        mag_error : float, optional
            Uncertainty in the magnitude. If None, the flux error will be 
            set to NaN. Default is None.
        final_table : bool, optional
            If True, the photometry is added to the final table. Default is False.
            
        Raises
        ------
        TypeError
            If filter_name is not a string, or if mag/mag_error are not numeric.
        ValueError
            If mag is NaN or infinite, or if mag_error is negative.
        
        Warnings
        --------
        This method should only be called after the SED class is initialized but 
        BEFORE starting any analysis (e.g., before calling `run()`, 
        `estimate_radius()`, `estimate_ebv()`, etc.). Once analysis begins, the 
        catalog table structure and content are completely transformed, and adding 
        photometry at that point will cause errors. Always add custom photometric 
        data immediately after creating the SED object and before running any 
        analysis methods.
            
        Notes
        -----
        - The flux is calculated using the filter's magnitude-to-flux conversion
        - Flux errors are computed using standard photometric error propagation
        - The catalog is automatically sorted by wavelength after each addition
        - Coordinates (RA/Dec) from the SED object are included in each row
        """
        # Validate input arguments
        if not isinstance(filter_name, str):
            raise TypeError("filter_name must be a string")
        
        if not isinstance(mag, (int, float)) or not np.isfinite(mag):
            raise ValueError("mag must be a finite numeric value")
            
        if mag_error is not None:
            if not isinstance(mag_error, (int, float)):
                raise TypeError("mag_error must be numeric or None")
            if mag_error < 0:
                raise ValueError("mag_error cannot be negative")
        
        self._logger.info(f"BEGIN - Adding photometry to catalog")

        # Set default mag_error if not provided
        if mag_error is None:
            mag_error = np.nan

        # Create filter object and convert magnitude to flux
        f = Filter(filter_name)
        flux = f.mag_to_flux(mag, unit=u.erg / u.s / u.cm**2 / u.AA)

        # Calculate flux error using standard photometric error propagation
        if not np.isnan(mag_error):
            # df/f = 0.4 * ln(10) * dm for magnitude errors
            flux_error = 0.4 * np.log(10) * flux * mag_error
        else:
            flux_error = np.nan * flux.unit

        self._logger.info(
            f"Adding photometry to catalog: {filter_name}, {mag}, {mag_error}"
        )

        # Prepare new catalog row with all required columns
        if not final_table:
            new_row = [
                self._ra.to(u.deg).value,          # RA in degrees
                self._dec.to(u.deg).value,         # Dec in degrees
                # hack for TESS/TESS:Red
                'TESS/TESS:Red' if filter_name == 'TESS/TESS.Red' else filter_name,
                f,                                 # Filter object
                # Frequency
                f.WavelengthCen.to(
                    u.GHz, 
                    equivalencies=u.spectral()
                ).value,
                f.WavelengthCen.to(u.micrometer).value,  # Wavelength in microns 
                flux.value,                        # Flux value
                flux_error.value,                  # Flux error
                mag,                               # Original magnitude
                mag_error                          # Original magnitude error
            ]
        else:
            new_row = [
                f.WavelengthCen.to(u.micrometer).value,  # Wavelength in microns 
                f.WavelengthCen.to(
                    u.GHz, 
                    equivalencies=u.spectral()
                ).value,
                flux.value,
                flux_error.value,
                'TESS/TESS:Red' if filter_name == 'TESS/TESS.Red' else filter_name,
                f,
                None,
                None,
                None,
                None,
                None,
                None,
            ]
        
        # Add row to catalog and sort by wavelength
        self.catalog.table.add_row(new_row)
        self.catalog.table.sort('wavelength')

        self._logger.info(f"END - Adding photometry to catalog")

    def summary(self):
        """
        Display a dashboard summary of the star's parameters and photometric 
        catalog details.

        This internal method gathers key star parameters (effective temperature 
        and its error, radius and its error, distance and its error, parallax 
        and its error, coordinates, and extinction if available) along with 
        photometric catalog statistics. It then generates a descriptive summary 
        sentence immediately under the main title, e.g.:

        "For Vega (RA: 279.2345 deg, Dec: 38.7837 deg) with a search radius of 
        1.0 arcsec, a total of 120 photometric measurements were compiled from 
        the literature, covering 8 unique bands."

        Below the summary sentence, two tables are arranged side by side using a 
        flex layout:
        - The left table lists the star parameters (with Astropy units).
        - The right table provides a scrollable breakdown of unique filters, 
            sorted from most to least.
        
        An SED plot with the blackbody fit is also generated and embedded in the 
        dashboard. In a Jupyter Notebook environment the output is rendered as 
        styled HTML; in a console environment, a plain text summary is printed.
        
        Finally, the full photometric catalog (self.catalog.table) is shown below
        the SED plot in a scrollable container.
        
        Returns
        -------
        None
        """
        try:
            from IPython.display import display, HTML
        except ImportError:
            display = None

        params = {}
        if self.teff is not None:
            params['Teff'] = (
                f"{self.teff.value:.1f} {self.teff.unit.to_string()}"
            )
            if getattr(self, 'teff_error', None) is not None:
                params['Teff Error'] = (
                    f"{self.teff_error.value:.1f} "
                    f"{self.teff_error.unit.to_string()}"
                )

        if self.radius is not None:
            params['Radius'] = f"{self.radius.to('Rsun').value:.3f} Rsun"
            if getattr(self, 'radius_error', None) is not None:
                params['Radius Error'] = (
                    f"{self.radius_error.to('Rsun').value:.3f} Rsun"
                )

        if self.distance is not None:
            params['Distance'] = f"{self.distance.to('pc').value:.2f} pc"
            if getattr(self, 'distance_error', None) is not None:
                params['Distance Error'] = (
                    f"{self.distance_error.to('pc').value:.2f} pc"
                )

        if getattr(self, 'parallax', None) is not None:
            params['Parallax'] = f"{self.parallax.to('mas').value:.2f} mas"
            if getattr(self, 'parallax_error', None) is not None:
                params['Parallax Error'] = (
                    f"{self.parallax_error.to('mas').value:.2f} mas"
                )

        if getattr(self, '_ra', None) is not None:
            params['RA'] = f"{self._ra:.4f} deg"

        if getattr(self, '_dec', None) is not None:
            params['Dec'] = f"{self._dec:.4f} deg"

        if getattr(self, 'ebv', None) is not None:
            params['E(B-V)'] = f"{self.ebv:.3f}"
            if getattr(self, '_ebv_error', None) is not None:
                params['E(B-V) Error'] = f"{self._ebv_error:.3f}"

        total_points = "N/A"
        unique_bands = "N/A"
        filt_col = None
        if self.catalog.table is not None:
            table = self.catalog.table
            total_points = len(table)
            filt_col = table['vizier_filter']

            if filt_col is not None:
                filters_str = [str(f) for f in filt_col]
                unique_bands = len(np.unique(filters_str))
        
        star_name = (
            self.name if hasattr(self, 'name') and self.name is not None 
            else "the target star"
        )
        coord_str = ""
        if self._ra is not None and self._dec is not None:
            coord_str = (
                f"(RA: {self._ra:.4f} deg, Dec: {self._dec:.4f} deg)"
            )
        
        search_radius_str = ""
        if self.search_radius is not None:
            search_radius_str = (
                f"with a search radius of "
                f"{self.search_radius.to(u.arcsec).value:.1f} arcsec, "
            )
        
        summary_sentence = (
            f"For {star_name} {coord_str}, {search_radius_str}<u>a total of "
            f"<b>{total_points}</b> photometric measurements</u> were compiled "
            f"from the literature, <u>covering <b>{unique_bands}</b> unique "
            f"bands</u>."
        )

        # Generate the SED Plot and Encode as Base64
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO
            fig, ax = plt.subplots(figsize=(8, 6))
            self.plot(
                ax=ax,
                with_blackbody=True if self.teff is not None else False,
                with_outliers=(
                    True if self.catalog.rejected_data is not None else False
                ),
                with_extinction=True if self.ebv is not None else False,
                show=False,
                save=False
            )
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            import base64
            img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            img_html = (
                f'<img src="data:image/png;base64,{img_base64}" '
                f'alt="SED Plot" style="max-width:100%;">'
            )
        except Exception as e:
            img_html = (
                "<p>[SED plot unavailable! Please provide temperature and "
                "radius]</p>"
            )

        # Create HTML dashboard
        dashboard_html = f"""
        <div style="font-family: Arial, sans-serif; margin: 10px;">
        <h2 style="text-align: center; color: #2e6c80;">SED Summary</h2>
        <p style="text-align: center; font-size: 16px; color: #333;">
            {summary_sentence}
        </p>
        """
        
        dashboard_html += """
        <div style="display: flex; justify-content: space-around; 
                    margin-bottom: 20px;">
        """

        # Star Parameters Table
        dashboard_html += """
            <div style="width: 45%; border: 1px solid #ccc; padding: 10px; 
                        border-radius: 5px;">
            <h3 style="text-align: center; color: #333;">Star Parameters</h3>
            <table style="width: 100%; border-collapse: collapse;">
        """
        for key, val in params.items():
            dashboard_html += f"""
                <tr>
                <th style="text-align: left; border-bottom: 1px solid #ddd; 
                        padding: 4px;">{key}</th>
                <td style="border-bottom: 1px solid #ddd; padding: 4px;">
                    {val}
                </td>
                </tr>
            """
        dashboard_html += """
            </table>
            </div>
        """
        
        # Unique Filters Table
        if filt_col is not None:
            filters_str = [
                str(f) if f is not None else "Unknown" for f in filt_col
            ]
            unique_filters = {}
            for filt in np.unique(filters_str):
                unique_filters[filt] = int(np.sum(np.array(filters_str) == filt))
            sorted_filters = sorted(
                unique_filters.items(), key=lambda x: x[1], reverse=True
            )
            dashboard_html += """
            <div style="width: 45%; border: 1px solid #ccc; padding: 10px; 
                        border-radius: 5px;">
            <h3 style="text-align: center; color: #333;">
                Unique Filters
            </h3>
            <div style="max-height: 200px; overflow-y: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th style="text-align: left; border-bottom: 1px solid #ddd; 
                            padding: 4px;">Filter</th>
                    <th style="text-align: left; border-bottom: 1px solid #ddd; 
                            padding: 4px;">Data Points</th>
                </tr>
            """
            for filt, count in sorted_filters:
                dashboard_html += f"""
                <tr>
                    <td style="border-bottom: 1px solid #ddd; padding: 4px;">
                        {filt}
                    </td>
                    <td style="border-bottom: 1px solid #ddd; padding: 4px;">
                        {count}
                    </td>
                </tr>
                """
            dashboard_html += """
                </table>
            </div>
            </div>
            """
        
        dashboard_html += """
        </div>
        """
        
        # SED Plot
        dashboard_html += f"""
        <div style="text-align: center; margin-bottom: 20px; 
                    border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h3 style="color: #333;">SED Plot</h3>
            {img_html}
        </div>
        """

        # Append the Photometric Catalog Table in a scrollable container
        try:
            from io import StringIO
            table_io = StringIO()
            self.catalog.table.write(table_io, format='html')
            catalog_table_html = table_io.getvalue()
            catalog_table_html = f"""
            <div style="max-height: 400px; overflow-y: auto; 
                        border: 1px solid #ccc; padding: 10px; margin-top: 20px;">
                <h3 style="text-align: center; color: #333;">
                    Photometric Catalog
                </h3>
                {catalog_table_html}
            </div>
            """
        except Exception as e:
            catalog_table_html = "<p>[Catalog table unavailable]</p>"
        
        dashboard_html += catalog_table_html
        
        dashboard_html += """
        </div>
        """
        
        # Output the dashboard
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell' and display is not None:
                display(HTML(dashboard_html))
            else:
                raise NameError("Not Jupyter")
        except NameError:
            print("SED Summary")
            print("---------------------")
            print(summary_sentence)
            print("\nStar Parameters:")
            for key, val in params.items():
                print(f"  {key}: {val}")
            if filt_col is not None:
                print("\nUnique Filters:")
                for filt, count in sorted_filters:
                    print(f"  {filt}: {count} data points")

    def save(self, path, compression=True):
        """Save the SED project to a file.

        This method serializes the entire SED object, including all its attributes,
        catalog data, and analysis results, to a binary file using dill 
        serialization. The saved file can later be loaded using the `SED.load()` 
        class method. The data can optionally be compressed using zip.

        Parameters
        ----------
        path : str
            The file path where the SED project will be saved.
            The file extension can be anything (e.g., '.sed', '.dat', '.bin').
            When compression is True and path doesn't end with '.zip', it will be
            automatically appended.
            Example: 'my_star.sed' or '/path/to/analysis.dat'
        compression : bool, optional
            Whether to compress the saved file using zip compression.
            Default is True.

        Returns
        -------
        str
            The path to the saved SED project file.

        Raises
        ------
        OSError
            If there are issues writing to the specified file path.
        TypeError
            If the path is not a string.
        PermissionError
            If the process lacks permission to write to the specified location.
        
        Examples
        --------
        >>> from sedlib import SED
        >>> 
        >>> # Create and analyze an SED
        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun
        >>> 
        >>> # Save the analysis with compression (default)
        >>> # Will be saved as 'vega_analysis.sed.zip'
        >>> sed.save('vega_analysis.sed')
        >>> 
        >>> # Save without compression
        >>> sed.save('vega_analysis.sed', compression=False)
        """
        # If compression is enabled and path doesn't end with '.zip', append it
        if compression and not path.endswith('.zip'):
            path = f"{path}.zip"

        self._logger.info(
            f"BEGIN - Saving SED project to {path} "
            f"{'with' if compression else 'without'} compression"
        )

        # Save the SED project
        try:
            if compression:
                # First serialize the object to a bytes buffer
                buffer = BytesIO()
                dump(self, buffer, recurse=True)
                buffer.seek(0)
                
                # Create a zip file and add the serialized data
                with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('sed_data', buffer.getvalue())
            else:
                # Save without compression
                with open(path, 'wb') as f:
                    dump(self, f, recurse=True)
                    
            self._logger.info("END - SED project saved successfully")
        except Exception as e:
            self._logger.error(f"Error saving SED project to file: {e}")
            print(f"Error saving SED project to file: {e}")
            raise
        
        return path
    
    @staticmethod
    def load(path):
        """Load a previously saved SED project from a file.

        This class method deserializes a binary file created by the `save()` 
        method back into a complete SED object, restoring all attributes, catalog 
        data, and analysis results. It automatically detects whether the file
        is compressed (zip) or not.

        Parameters
        ----------
        path : str
            The path to the saved SED project file.
            The file extension does not matter as long as it matches what was used
            in save(). Example: 'my_star.sed' or '/path/to/analysis.dat'

        Returns
        -------
        SED
            The reconstructed SED object with all its original attributes and data.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        OSError
            If there are issues reading the file.
        TypeError
            If the path is not a string.
        ValueError
            If the file is corrupted or not a valid SED project file.
        
        Examples
        --------
        >>> from sedlib import SED
        >>> 
        >>> # Load a previously saved analysis (works with both compressed and
        >>> # uncompressed files)
        >>> sed = SED.load('vega_analysis.sed')
        >>> 
        >>> # Continue analysis with loaded data
        >>> sed.plot(with_blackbody=True, show=True)
        """
        try:
            # Try to open as a zip file first
            try:    
                with zipfile.ZipFile(path, 'r') as zf:
                    data = zf.read('sed_data')
                    buffer = BytesIO(data)
                    sed = load(buffer)
            except zipfile.BadZipFile:
                # If not a zip file, try loading as regular file
                with open(path, 'rb') as f:
                    sed = load(f)
            return sed
        except Exception as e:
            print(f"Error loading SED project from file: {e}")

    def get_logs(self, log_type: str = 'all') -> Optional[List[str]]:
        """Get all stored log records for this filter instance.
        if in-memory logging is enabled, return the log records,
        otherwise return None
        
        Parameters
        ----------
        log_type : str
            log type to get
            possible values are 'all', 'info', 'debug', 'warning', 'error'
            (default: 'all')
        
        Returns
        -------
        Optional[List[str]]
            List of formatted log records if in-memory logging is enabled,
            None otherwise
        """
        self._logger.info("BEGIN - Getting logs")
        if self._memory_handler:
            return self._memory_handler.get_logs(log_type)
        self._logger.info("END - memory handler not found")
        return None

    def dump_logs(self, filename: str) -> None:
        """Dump all stored log records for this filter instance to a file.
        if in-memory logging is enabled, dump the log records to a file,
        otherwise do nothing
        """
        self._logger.info("BEGIN - Dumping logs")
        if self._memory_handler:
            self._memory_handler.dump_logs(filename)
        self._logger.info("END - Dumping logs")
    
    def clear_logs(self) -> None:
        """Clear all stored log records for this filter instance.
        if in-memory logging is enabled, clear the log records,
        otherwise do nothing
        """
        self._logger.info("BEGIN - Clearing logs")
        if self._memory_handler:
            self._memory_handler.clear()
        self._logger.info("END - Clearing logs")

    def reset(self):
        """Reset the SED object to its initial state.

        This method resets all attributes of the SED object to their default values,
        effectively clearing all data and results.
        """
        self._logger.info("BEGIN - Resetting SED object")
        pass
        self._logger.info("END - Resetting SED object")

    def plot(
        self,
        with_blackbody=False,
        with_outliers=False,
        with_extinction=False,
        blackbody_wavelength_range=(0.1, 1000),
        figsize=(8, 6),
        ax=None,
        show=False,
        save=False,
        save_path="sed.png",
        dpi=300,
        interactive=False,
        **kwargs
    ):
        """Plot the spectral energy distribution (SED) as a log-log plot of flux 
        versus wavelength.

        Parameters
        ----------
        with_blackbody : bool, optional
            If True, plots observed SED with blackbody model fit.
            If teff, radius, and distance are set, blackbody model is fitted and 
            plotted.
            Default is False.
        with_outliers : bool, optional
            If True, plots observed SED with outliers highlighted.
            Default is False.
        with_extinction : bool, optional
            If True, plots observed SED with extinction correction.
            Default is False.
        blackbody_wavelength_range : tuple, optional
            The wavelength range to fit the blackbody model.
            Default is (0.1, 1000) micrometers.
        figsize : tuple, optional
            The figure size. Default is (8, 6).
        ax : `matplotlib.axes.Axes`, optional
            The axes to plot on. If None, a new figure is created.
        show : bool, optional
            If True, displays the plot. Set to False if using %matplotlib inline.
            Default is False.
        save : bool, optional
            If True, saves the plot to the specified path. Default is False.
        save_path : str, optional
            The file path to save the plot. Default is "sed.png".
        dpi : int, optional
            The resolution in dots per inch for saving the plot. Default is 300.
        interactive : bool, optional
            If True, creates an interactive plot using Bokeh instead of Matplotlib.
            Default is False.
        **kwargs : dict, optional
            Additional keyword arguments for the plot.

        This method uses the catalog data to plot the flux values against the 
        wavelength.

        Examples
        --------
        >>> from sedlib import SED

        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun

        >>> # Plot observed data only
        >>> sed.plot(show=True)

        >>> # Plot with blackbody model fit
        >>> sed.plot(with_blackbody=True, show=True)

        >>> # Plot with extinction correction
        >>> sed.compute_ebv()
        >>> sed.plot(with_blackbody=True, with_extinction=True, show=True)
        """
        self._logger.info("Starting SED plot generation")

        if self._catalog is None:
            self._logger.error("No catalog data available for plotting")
            raise ValueError("No catalog data available for plotting.")

        # check input types
        if not isinstance(with_blackbody, bool):
            raise TypeError("`with_blackbody` must be bool object.")
        if not isinstance(with_extinction, bool):
            raise TypeError("`with_extinction` must be bool object.")
        if not isinstance(blackbody_wavelength_range, tuple):
            raise TypeError("`blackbody_wavelength_range` must be tuple object.")
        if not isinstance(figsize, tuple):
            raise TypeError("`figsize` must be tuple object.")
        if ax is not None and not isinstance(ax, Axes):
            raise TypeError("`ax` must be `matplotlib.axes.Axes` object.")
        if not isinstance(show, bool):
            raise TypeError("`show` must be bool object.")
        if not isinstance(save, bool):
            raise TypeError("`save` must be bool object.")
        if not isinstance(save_path, str):
            raise TypeError("`save_path` must be str object.")
        if not isinstance(dpi, int):
            raise TypeError("`dpi` must be int object.")
        if not isinstance(interactive, bool):
            raise TypeError("`interactive` must be bool object.")

        self._logger.debug("Input parameter validation completed")

        if with_blackbody and (
            self.teff is None or self.radius is None or self.distance is None
        ):
            self._logger.warning("Missing parameters for blackbody model")
            raise UserWarning(
                "Temperature (teff), radius, and distance must be set to plot "
                "the blackbody model. Example for Vega:\n"
                "sed.teff = 10070 * u.K\n"
                "sed.radius = 2.726 * u.Rsun\n"
                "sed.distance = 7.68 * u.pc"
            )
            with_blackbody = False
        
        if (
            with_blackbody and with_extinction and 
            self.ebv is None and self.ext_model is None
        ):
            self._logger.warning("Missing parameters for extinction correction")
            raise UserWarning(
                "E(B-V) and extinction model must be set to apply extinction "
                "corrections. Example:\n"
                "sed.ebv = 0.1\n"
                "sed.ext_model = G23 (Rv: 3.1)"
            )
            with_extinction = False

        if with_outliers and self.catalog.rejected_data is None:
            self._logger.warning("No outliers found in the catalog")
            with_outliers = False

        self._logger.debug("Parameter checks completed")

        # Determine units for labels based on astropy Quantity units
        wavelength_unit = (
            self._catalog["wavelength"].unit
            if isinstance(self._catalog["wavelength"], u.Quantity)
            else self._wavelength_unit
        )
        flux_unit = (
            self._catalog["flux"].unit
            if isinstance(self._catalog["flux"], u.Quantity)
            else self._flux_unit
        )

        if with_blackbody:
            self._logger.info("Calculating blackbody model")
            dR = (self.distance.to(u.cm) / self.radius.to(u.cm)) ** 2

            wavelengths = np.logspace(
                np.log10(blackbody_wavelength_range[0]),
                np.log10(blackbody_wavelength_range[1]),
                1000
            ) * wavelength_unit

            blackbody_flux = BlackBody(
                temperature=self.teff,
                scale=1.0 * u.erg / (u.cm ** 2 * u.AA * u.s * u.sr)
            )(wavelengths) * np.pi / dR
        
        if with_extinction:
            self._logger.info("Applying extinction correction")
            w1 = (1 / self.ext_model.x_range[-1]) * u.um
            w2 = (1 / self.ext_model.x_range[0]) * u.um

            mask = (w1 <= wavelengths) & (wavelengths <= w2)

            synth_ext_wavelengths = wavelengths[mask]
            synth_ext_flux = blackbody_flux[mask] * self.ext_model.extinguish(
                synth_ext_wavelengths, Ebv=self.ebv
            )

        # Interactive plot with Bokeh
        if interactive:
            self._logger.info("Creating interactive Bokeh plot")
            output_notebook()
            bokeh_fig = figure(
                title=f"{self._name} - Spectral Energy Distribution",
                x_axis_label=(
                    f'Wavelength [{wavelength_unit.to_string("unicode")}]'
                ),
                y_axis_label=f'Flux [{flux_unit.to_string("unicode")}]',
                x_axis_type="log",
                y_axis_type="log",
                width=int(figsize[0] * 100),
                height=int(figsize[1] * 100),
            )

            # Remove Bokeh logo
            bokeh_fig.toolbar.logo = None

            # Plot observed flux
            source = ColumnDataSource(
                data=dict(
                    wavelength=self._catalog["wavelength"].value,
                    flux=self._catalog["flux"].value,
                    eflux=self._catalog["eflux"].value,
                    filter=self._catalog["vizier_filter"]
                )
            )
            bokeh_fig.scatter(
                x="wavelength", y="flux", source=source, size=12,
                color="black", marker="cross", legend_label="Observed Flux"
            )
            
            # Add error bars
            err_xs = []
            err_ys = []
            for x, y, yerr in zip(
                self._catalog["wavelength"].value,
                self._catalog["flux"].value,
                self._catalog["eflux"].value
            ):
                err_xs.append([x, x])
                err_ys.append([y - yerr, y + yerr])
            bokeh_fig.multi_line(err_xs, err_ys, color="gray", alpha=0.5)

            if with_outliers and len(self.catalog.rejected_data) > 0:
                outlier_source = ColumnDataSource(
                    data=dict(
                        outlier_wavelength=(
                            self.catalog.rejected_data["wavelength"].value
                        ),
                        outlier_flux=self.catalog.rejected_data["flux"].value
                    )
                )

                bokeh_fig.scatter(
                    x="outlier_wavelength",
                    y="outlier_flux",
                    source=outlier_source,
                    size=12,
                    color="magenta",
                    marker="x",
                    legend_label=(
                        f"Outliers: σ > {self.catalog._rejected_sigma_threshold:.1f}"
                    )
                )

            if with_blackbody:
                bb_source = ColumnDataSource(
                    data=dict(
                        bb_wavelength=wavelengths.value,
                        bb_flux=blackbody_flux.value,
                    )
                )
                bokeh_fig.line(
                    x="bb_wavelength",
                    y="bb_flux", 
                    source=bb_source,
                    color="blue",
                    line_width=2,
                    legend_label=(
                        "Blackbody Model:\n"
                        f"    Teff = {self.teff:.0f},\n"
                        f"    R = {self.radius.to(u.Rsun):.2f},\n"
                        f"    d = {self.distance.to(u.pc):.2f}"
                    )
                )
            
            if with_extinction:
                ext_source = ColumnDataSource(
                    data=dict(
                        ext_wavelength=synth_ext_wavelengths.value,
                        ext_flux=synth_ext_flux.value,
                    )
                )
                bokeh_fig.line(
                    x="ext_wavelength",
                    y="ext_flux",
                    source=ext_source,
                    color="red",
                    line_width=2,
                    legend_label=(
                        "Reddened Blackbody:\n"
                        f"    Model: {self.ext_model.__class__.__name__} "
                        f"(Rv = {self.ext_model.parameters[0]:.2f})\n"
                        f"    E(B-V) = {self.ebv:.2f}\n"
                        f"    E(B-V) Error = {self._ebv_error:.2e}"
                    )
                )

            # Add hover tool
            hover = HoverTool()
            hover.tooltips = [
                ("Wavelength", "@x"),
                ("Flux", "@y"),
                # ("Flux Error", "@eflux"),
                # ("Filter", "@filter"),
            ]
            bokeh_fig.add_tools(hover)
            bokeh_fig.legend.click_policy = "hide"
            bokeh_fig.legend.location = "bottom_left"

            bokeh_show(bokeh_fig, notebook_handle=True)
            self._logger.info("Interactive plot displayed successfully")

            self._logger.info("END - interactive plot completed")

            return

        # Static plot with Matplotlib
        self._logger.info("Creating static Matplotlib plot")
        fig = None

        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot()

        ax.set_title(
            f"{self._name} - Spectral Energy Distribution",
            fontsize=13, fontweight="bold"
        )

        ax.set_xlabel(
            f'Wavelength [{wavelength_unit.to_string("latex_inline")}]',
            fontsize=10, style='italic'
        )

        ax.set_ylabel(
            f'Flux [{flux_unit.to_string("latex_inline")}]',
            fontsize=10, style='italic'
        )

        ax.set_xscale("log")
        ax.set_yscale("log")

        # Plot data with error bars
        ax.errorbar(
            self._catalog["wavelength"],
            self._catalog["flux"],
            yerr=self._catalog["eflux"],
            fmt="k+",
            ms=8,
            label="Observed Flux",
            capsize=3,
            elinewidth=1,
            capthick=1
        )

        if with_blackbody:
            ax.plot(
                wavelengths.value,
                blackbody_flux.value,
                color="blue",
                linestyle="-",
                linewidth=1,
                label=(
                    f"Blackbody Model:\n"
                    f"    Teff = {self.teff:.0f},\n"
                    f"    R = {self.radius.to(u.Rsun):.2f},\n"
                    f"    d = {self.distance.to(u.pc):.2f}"
                ),
            )
        
        if with_outliers and len(self.catalog.rejected_data) > 0:
            ax.errorbar(
                self.catalog.rejected_data["wavelength"],
                self.catalog.rejected_data["flux"],
                yerr=self.catalog.rejected_data["eflux"],
                fmt="k+",
                ms=8,
                capsize=3,
                elinewidth=1,
                capthick=1
            )

            ax.scatter(
                self.catalog.rejected_data["wavelength"],
                self.catalog.rejected_data["flux"],
                label=(
                    f"Outliers: σ > {self.catalog._rejected_sigma_threshold:.1f}"
                ),
                color="magenta", 
                marker="x",
                s=100,
                alpha=0.8,
                zorder=10,
                linewidth=2,
                edgecolor="darkred"
            )

        if with_extinction:
            ax.plot(
                synth_ext_wavelengths.to(u.um),
                synth_ext_flux.value,
                color="red",
                linestyle="-",
                label=(
                    f"Reddened Blackbody:\n"
                    f"    Model: {self.ext_model.__class__.__name__}"
                    f"(Rv={self.ext_model.parameters[0]:.2f})\n"
                    f"    E(B-V) = {self.ebv:.2f}\n"
                    f"    E(B-V) Error = {self._ebv_error:.2e}\n"
                ),
            )

        # Create the top axis
        top_ax = ax.secondary_xaxis('top')
        top_ax.set_xticks(ax.get_xticks())

        # Create the right axis
        right_ax = ax.secondary_yaxis('right')
        right_ax.set_yticks(ax.get_yticks())

        # add legend
        ax.legend(loc="best", fontsize=10)

        # Save plot to disk
        if save:
            fig.savefig(
                save_path,
                dpi=dpi,
                format=save_path.split(".")[-1]
            )
            self._logger.info(f"SED plot saved to {save_path} with dpi={dpi}")

        # Show plot if in non-notebook environments or if explicitly desired
        if show:
            plt.show()
            self._logger.info("Plot displayed successfully")

        self._logger.info("END - plot method completed")

    def plot_results(
        self,
        radius_chi2=False,
        radius_mc=False,
        ebv_mc=False,
        save=False,
        filename=None,
        dpi=300,
        figsize=(8, 5)
    ):
        """
        Generate visualization plots for radius and extinction estimation results.
        
        This method creates various diagnostic plots based on the results of previous
        analysis steps. It can generate chi-square minimization plots for radius estimation,
        Monte Carlo posterior distribution plots for radius, and corner plots for E(B-V)
        extinction estimation.
        
        Parameters
        ----------
        radius_chi2 : bool, optional
            Whether to plot chi-square curve from radius grid search (default: False)
        radius_mc : bool, optional
            Whether to plot Monte Carlo posterior distribution for radius (default: False)
        ebv_mc : bool, optional
            Whether to plot Monte Carlo corner plot for E(B-V) estimation (default: False)
        save : bool, optional
            Whether to save the plot to disk (default: False)
        filename : str, optional
            Custom filename for the saved plot. If None, a default name will be generated
            based on the plot type and object name (default: None)
        dpi : int, optional
            Resolution in dots per inch for saved plots (default: 300)
        figsize : tuple, optional
            Figure dimensions (width, height) in inches (default: (8, 5))
            
        Returns
        -------
        None
            The method displays the plot and optionally saves it to disk
            
        Raises
        ------
        ValueError
            If the requested plot type requires results that haven't been computed yet
        
        Examples
        --------
        >>> from sedlib import SED
        >>> sed = SED(name="Vega")
        >>>
        >>> # Run pipeline with default settings
        >>> sed.run()
        >>>
        >>> # Plot the E(B-V) Monte Carlo results
        >>> sed.plot_results(ebv_mc=True, save=True, filename="ebv_mc.png")
        """
        self._logger.info("BEGIN - Plotting results")

        if radius_chi2:
            self._logger.info("Plotting refined chi-square curve")

            if self._radius_grid_search_results_for_plotting is None:
                raise ValueError(
                    "No grid search results available. "
                    "Run estimate_radius with method='grid' first."
                )

            results = self._radius_grid_search_results_for_plotting
            R_refined = results['R_refined']
            chi2_refined = results['chi2_refined']
            chi2_min_refined = results['chi2_min_refined']
            R_best_refined = results['R_best_refined']
            R_lower = results['R_lower']
            R_upper = results['R_upper']

            # Create figure for visualizing chi-square minimization results
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)
            
            # Plot chi-square curve with high-resolution sampling
            ax.plot(
                R_refined, chi2_refined, 'k-', linewidth=1.5, 
                label=r'$\chi^2(R)$'
            )
            
            # Indicate statistical significance threshold
            ax.axhline(
                chi2_min_refined + 1, color='0.5', linestyle='--', 
                label=r'$\chi^2_{min} + \Delta\chi^2_{1\sigma}$'
            )
            
            # Mark best-fit radius
            ax.axvline(
                R_best_refined, color='#d62728', linestyle='--',
                label=r'$R_{best} = %.2f\ R_\odot$' % R_best_refined
            )
            
            # Show confidence interval bounds if available
            if R_lower is not None and R_upper is not None:
                ax.axvspan(
                    R_lower, R_upper, alpha=0.2, color='#2ca02c',
                    label=r'$1\sigma$ Confidence Region'
                )
                
            # Configure axes
            ax.set_xlabel(r'Stellar Radius $(R_\odot)$', fontsize=12)
            ax.set_ylabel(r'$\chi^2$ Statistic', fontsize=12)
            ax.set_title(
                r'Maximum Likelihood Radius Estimation via $\chi^2$ Minimization',
                fontsize=14
            )
            
            # Add grid and legend
            ax.grid(True, alpha=0.3)
            ax.legend(frameon=True, fontsize=10, loc='upper right')
            
            # Use scientific notation for y-axis if values are large
            ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))

            if save:
                if filename is None:
                    filename = f"radius_chi2_{self._user_provided_name}.png"
                self._logger.info(f"Saving plot to {filename}")
                plt.savefig(filename, dpi=dpi, bbox_inches="tight")

            self._logger.info("Finished plotting refined chi-square curve")
            self._logger.info("END - Plotting results")

            return

        if radius_mc:
            # Generate corner plot visualization of the Monte Carlo distribution
            self._logger.info("Plotting radius Monte Carlo results")

            if self._radius_mc_results_for_plotting is None:
                raise ValueError(
                    "No Monte Carlo results available. "
                    "Run estimate_radius with method='mc' first."
                )
            
            R_values = self._radius_mc_results_for_plotting['R_values']

            # Construct posterior samples array for radius distribution analysis
            posterior_samples = R_values.reshape(-1, 1)
            
            # Generate corner plot with statistical quantiles
            figure = corner.corner(
                posterior_samples,
                labels=[r"$R_{\star}\,(R_{\odot})$"],  # Proper radius notation
                show_titles=True,
                quantiles=[0.16, 0.5, 0.84],  # 1σ credible intervals
                title_kwargs={"fontsize": 12},
                title_fmt=".2f",  # Two decimal precision
                hist_kwargs={"density": True}  # Normalized histogram
            )
            
            # Save high-resolution visualization if filename provided
            if save:
                if filename is None:
                    filename = f"radius_mc_{self._user_provided_name}.png"
                
                self._logger.info(f"Saving plot to {filename}")

                figure.savefig(
                    filename,
                    dpi=dpi,
                    bbox_inches="tight",
                    metadata={
                        "Creator": "SEDLib",
                        "Description": "Stellar radius posterior distribution"
                    }
                )

            self._logger.info("Finished plotting radius Monte Carlo results")
            self._logger.info("END - Plotting results")

            return

        if ebv_mc:
            self._logger.info("Plotting E(B-V) Monte Carlo results")

            if self._ebv_mc_results_for_plotting is None:
                raise ValueError(
                    "No Monte Carlo results available. "
                    "Run estimate_ebv with method='mc' first."
                )
            
            T_valid_with_units = self._ebv_mc_results_for_plotting[
                'T_valid_with_units']
            R_valid_with_units = self._ebv_mc_results_for_plotting[
                'R_valid_with_units']
            D_valid_with_units = self._ebv_mc_results_for_plotting[
                'D_valid_with_units']
            ebv_array = self._ebv_mc_results_for_plotting['ebv_array']

            self._logger.debug("Creating corner plot")
            data_for_corner = np.column_stack([
                T_valid_with_units, 
                R_valid_with_units, 
                D_valid_with_units, 
                ebv_array
            ])
            
            labels = [
                r"$T_\mathrm{eff}\,\mathrm{(K)}$",
                r"$R\,(\mathrm{R_\odot})$",
                r"$d\,(\mathrm{pc})$",
                r"$E(B-V)$"
            ]
            
            figure = corner.corner(
                data_for_corner,
                labels=labels,
                show_titles=True,
                quantiles=[0.16, 0.5, 0.84],
                title_kwargs={"fontsize": 10},
            )
            
            if save:
                if filename is None:
                    filename = f"ebv_mc_{self._user_provided_name}.png"
                
                self._logger.info(f"Saving plot to {filename}")

                figure.savefig(filename, dpi=dpi, bbox_inches="tight")
            
            self._logger.info("Finished plotting E(B-V) Monte Carlo results")
            self._logger.info("END - Plotting results")

            return
        
        self._logger.info("No plot requested")
        self._logger.info("END - Plotting results")

    def _estimate_radius_grid_search(
        self,
        radius_min=0.1,
        radius_max=50.0,
        coarse_steps=1000,
        refine_window=0.3,
        refine_steps=1000,
        n_jobs=-1,
        plot_chi2=False,
        chi2_filename=None,
        show_progress=True
    ):
        """Estimate the stellar radius using a hybrid method that combines a coarse
        grid search with a refined grid search in the promising region.

        .. warning::
            This is an internal method used by the public `estimate_radius()`
            method. Use with caution - this method assumes all required parameters
            are properly set and validated. For general radius estimation, use
            `estimate_radius()` instead.
        
        The predicted flux is modeled as:
            F_pred = (R / distance)^2 * π * B_λ(T_eff)
        where B_λ(T_eff) is the blackbody function evaluated at the effective 
        temperature.
        
        The method proceeds in two stages:
        
        1. Coarse Stage:
            - A coarse grid of candidate radii (in R_sun) is generated between 
              `radius_min` and `radius_max`.
            - For each candidate radius, the chi-square is computed comparing the 
              observed fluxes (from selected filters) to the predicted flux.
            - The candidate with the minimum chi-square is identified.
        
        2. Refined Stage:
            - A refined grid is constructed around the coarse best-fit value.
            - The refined grid spans ±(refine_window × R_best_coarse) around the 
              best-fit from the coarse stage.
            - A high-density grid search is performed in this interval.
            - The best-fit refined radius is determined, and the 1σ uncertainty is
              estimated by interpolating where χ² increases by 1 from its minimum.
        
        The method uses parallel processing (joblib) with tqdm to monitor progress.
        
        Parameters
        ----------
        radius_min : float, optional
            Minimum stellar radius to consider (in solar radii).
            Default is 0.1 R☉.
        radius_max : float, optional
            Maximum stellar radius to consider (in solar radii). 
            Default is 50.0 R☉.
        coarse_steps : int, optional
            Number of radius steps in the initial coarse grid search.
            Default is 1000.
        refine_window : float, optional
            Size of refinement window as fraction of best coarse radius.
            For example, 0.3 means ±30% around the coarse best-fit.
            Default is 0.3.
        refine_steps : int, optional
            Number of radius steps in the refined grid search.
            Default is 1000.
        n_jobs : int, optional
            Number of parallel jobs for the grid search (default -1 uses all
            cores).
        plot_chi2 : bool, optional
            If True, produces a plot of the chi-square versus radius for the 
            refined stage.
        chi2_filename : str, optional
            If provided, saves the chi-square plot to the given filename.
        show_progress : bool, optional
            If True, shows progress bars during the grid search stages.
            Default is True.
        
        Returns
        -------
        tuple (R_est, R_err)
            The estimated stellar radius and its 1σ uncertainty (both in R_sun).
        """
        self._logger.info("BEGIN - Estimating radius using grid search method")
        # Ensure required parameters are set.
        if self.teff is None or self.distance is None:
            raise ValueError(
                "Effective temperature and distance must be set to estimate "
                "radius."
            )

        t_start = time()

        # Retrieve catalog data.
        wavelength_unit = self.catalog.table['wavelength'].unit
        flux_unit = self.catalog.table['flux'].unit

        catalog_waves = []
        catalog_fluxes = []
        catalog_flux_errs = []
        for row in self.catalog.table:
            if row['vizier_filter'] in self._selected_filters_for_radius_estimation:
                catalog_waves.append(row['wavelength'])
                catalog_fluxes.append(row['flux'])
                catalog_flux_errs.append(row['eflux'])
        if len(catalog_waves) == 0:
            raise ValueError(
                "No data found for the selected filters in the catalog."
            )

        # Convert to numpy arrays with proper units.
        catalog_waves = np.array(catalog_waves) * wavelength_unit
        catalog_fluxes = np.array(catalog_fluxes) * flux_unit
        catalog_flux_errs = np.array(catalog_flux_errs) * flux_unit

        # Define the blackbody model using the object's effective temperature.
        scale = 1.0 * u.erg / (u.cm**2 * u.AA * u.s * u.sr)
        bb_model = BlackBody(temperature=self.teff, scale=scale)
        # Precompute distance in cm.
        d_cm = self.distance.to(u.cm).value

        # Define a function to compute chi-square for a given candidate radius R
        # (in R_sun).
        def compute_chi2(R_val):
            R_quantity = R_val * u.R_sun
            R_cm = R_quantity.to(u.cm).value
            S_val = (R_cm / d_cm)**2  # Unitless dilution factor.
            # Predicted flux: F_pred = S * π * B_bb(wavelength)
            predicted = S_val * np.pi * bb_model(catalog_waves)
            predicted_vals = predicted.value  # Pure float array.
            residuals = (
                catalog_fluxes.value - predicted_vals
            ) / catalog_flux_errs.value
            return np.sum(residuals**2)

        self._logger.info("starting coarse grid search stage")
        # === Coarse Grid Search Stage ===
        R_coarse = np.linspace(radius_min, radius_max, coarse_steps)
        chi2_coarse = Parallel(n_jobs=n_jobs)(
            delayed(compute_chi2)(R) for R in tqdm(
                R_coarse, desc="Coarse Grid Search", disable=not show_progress
            )
        )
        chi2_coarse = np.array(chi2_coarse)
        best_index_coarse = np.argmin(chi2_coarse)
        R_best_coarse = R_coarse[best_index_coarse]
        chi2_min_coarse = chi2_coarse[best_index_coarse]
        self._logger.info("Finished coarse grid search stage")
        self._logger.info(
            f"Coarse best-fit radius: {R_best_coarse:.2f} R_sun "
            f"with χ² = {chi2_min_coarse:.2f}"
        )

        # Define refined search window: ±(refine_window × R_best_coarse).
        window = refine_window * R_best_coarse
        R_refined_min = max(R_best_coarse - window, radius_min)
        R_refined_max = min(R_best_coarse + window, radius_max)
        R_refined = np.linspace(R_refined_min, R_refined_max, refine_steps)

        self._logger.info("starting refined grid search stage")
        # === Refined Grid Search Stage ===
        chi2_refined = Parallel(n_jobs=n_jobs)(
            delayed(compute_chi2)(R) for R in tqdm(
                R_refined, desc="Refined Grid Search", disable=not show_progress
            )
        )
        chi2_refined = np.array(chi2_refined)
        best_index_refined = np.argmin(chi2_refined)
        R_best_refined = R_refined[best_index_refined]
        chi2_min_refined = chi2_refined[best_index_refined]
        self._logger.info("Finished refined grid search stage")

        self._logger.info("starting uncertainty estimation stage")
        # === Uncertainty Estimation ===
        # Identify lower and upper bounds where χ² = χ²_min + 1 via linear
        # interpolation.
        R_lower = None
        for i in range(best_index_refined, 0, -1):
            if chi2_refined[i] > chi2_min_refined + 1:
                # Interpolate between indices i and i+1.
                R1, R2 = R_refined[i], R_refined[i+1]
                chi1, chi2_val = chi2_refined[i], chi2_refined[i+1]
                frac = (chi2_min_refined + 1 - chi1) / (chi2_val - chi1)
                R_lower = R1 + frac * (R2 - R1)
                break

        R_upper = None
        for i in range(best_index_refined, len(R_refined) - 1):
            if chi2_refined[i] > chi2_min_refined + 1:
                R1, R2 = R_refined[i-1], R_refined[i]
                chi1, chi2_val = chi2_refined[i-1], chi2_refined[i]
                frac = (chi2_min_refined + 1 - chi1) / (chi2_val - chi1)
                R_upper = R1 + frac * (R2 - R1)
                break

        if (R_lower is None) or (R_upper is None):
            R_err = np.nan * u.R_sun
        else:
            err_lower = R_best_refined - R_lower
            err_upper = R_upper - R_best_refined
            R_err_value = 0.5 * (err_lower + err_upper)
            R_err = R_err_value * u.R_sun

        self._logger.info("Finished uncertainty estimation stage")

        # Final best-fit radius and uncertainty.
        R_est = R_best_refined * u.R_sun

        # Store the results for later visualization
        self._radius_grid_search_results_for_plotting = {
            'R_refined': R_refined,
            'chi2_refined': chi2_refined,
            'R_best_refined': R_best_refined,
            'chi2_min_refined': chi2_min_refined,
            'R_lower': R_lower,
            'R_upper': R_upper,
        }

        # Optionally plot the refined chi-square curve.
        if plot_chi2:
            self.plot_results(
                radius_chi2=True,
                save=True if chi2_filename else False,
                filename=chi2_filename
            )

        elapsed = time() - t_start
        self._logger.info(f"elapsed time: {elapsed:.2f} seconds")

        self._logger.info(
            f"END - Radius estimation complete: {R_est:.2f} ± {R_err:.2f} R_sun"
        )

        results = {
            'method': 'grid_search',
            'radius': R_est,
            'radius_error': R_err,
            'elapsed_time': elapsed
        }

        return results

    def _estimate_radius_mc(
        self,
        n_samples=1000,
        n_jobs=-1,
        corner_plot=False,
        corner_filename=None,
        show_progress=True
    ):
        """Estimate the stellar radius using Monte Carlo simulation in parallel.

        .. warning::
            This is an internal method used by the public `estimate_radius()` 
            method. Use with caution - this method assumes all required parameters 
            are properly set and validated. For general radius estimation, use 
            `estimate_radius()` instead.
        
        For each Monte Carlo realization, the effective temperature, distance, 
        and observed fluxes are perturbed within their uncertainties. The best-fit
        radius is then found by minimizing:
            F_pred = (R / distance)^2 * π * B_λ(T_eff)
        where B_λ is the blackbody function.
        
        Parameters
        ----------
        n_samples : int, optional
            Number of Monte Carlo draws (default is 1000).
        n_jobs : int, optional
            Number of parallel jobs for the simulation (default -1 uses all cores).
        corner_plot : bool, optional
            If True, produces a corner plot of the Monte Carlo draws.
        corner_filename : str or None, optional
            If provided, saves the corner plot to this filename.
        show_progress : bool, optional
            If True, shows a progress bar during the Monte Carlo simulation.
            Default is True.
        
        Returns
        -------
        tuple (R_est, R_err)
            The estimated stellar radius and its uncertainty (in R_sun).
        """
        # Check required parameters.
        if self.teff is None or self.distance is None:
            raise ValueError("Effective temperature and distance must be set.")
        if self.teff_error is None or self.distance_error is None:
            raise ValueError("Both teff_error and distance_error must be set.")

        t_start = time()

        # Retrieve catalog data for the selected filters.
        wavelength_unit = self.catalog.table['wavelength'].unit
        flux_unit = self.catalog.table['flux'].unit

        catalog_waves = []
        catalog_fluxes = []
        catalog_flux_errs = []
        for row in self.catalog.table:
            if row['vizier_filter'] in self._selected_filters_for_radius_estimation:
                catalog_waves.append(row['wavelength'])
                catalog_fluxes.append(row['flux'])
                catalog_flux_errs.append(row['eflux'])
        if len(catalog_waves) == 0:
            raise ValueError(
                "No data found for the selected filters in the catalog."
            )

        # Convert lists to numpy arrays and attach units.
        catalog_waves = np.array(catalog_waves) * wavelength_unit
        catalog_fluxes = np.array(catalog_fluxes) * flux_unit
        catalog_flux_errs = np.array(catalog_flux_errs) * flux_unit
        
        # Extract needed values from self to avoid pickling issues with SED object
        teff_value = self.teff.value
        teff_unit = self.teff.unit
        teff_error_value = self.teff_error.value
        distance_value = self.distance.value
        distance_unit = self.distance.unit
        distance_error_value = self.distance_error.value

        # Define a worker function for a single MC draw.
        def worker(_):
            # Perturb T_eff and distance from Gaussian distributions.
            T_sample = np.random.normal(
                teff_value, teff_error_value
            ) * teff_unit
            d_sample = np.random.normal(
                distance_value, distance_error_value
            ) * distance_unit

            # Perturb the fluxes for each filter.
            flux_sample = np.random.normal(
                catalog_fluxes.value, catalog_flux_errs.value
            ) * flux_unit

            # Define the blackbody model for this realization.
            scale = 1.0 * u.erg / (u.cm**2 * u.AA * u.s * u.sr)
            bb_model = BlackBody(temperature=T_sample, scale=scale)

            # Define the objective function in terms of R (in R_sun).
            def objective(R_array):
                R_val = R_array[0] * u.R_sun
                # Compute geometric dilution factor S = (R/d)^2 using cm values.
                S_val = (R_val.to(u.cm).value / d_sample.to(u.cm).value)**2
                # Predicted flux at each wavelength: F_pred = S * π * B_bb(wave)
                predicted = S_val * np.pi * bb_model(catalog_waves)
                predicted_vals = predicted.value  # pure float array.
                residuals = (
                    flux_sample.value - predicted_vals
                ) / catalog_flux_errs.value
                return np.sum(residuals**2)

            try:
                R0 = [1.0]  # initial guess in R_sun.
                result = minimize(
                    objective, x0=R0, bounds=[(0, None)], method="L-BFGS-B"
                )
                return result.x[0]  # in R_sun (as a float)
            except Exception as e:
                return None

        # Parallel execution of MC draws with progress bar.
        if show_progress:
            results = Parallel(n_jobs=n_jobs)(
                delayed(worker)(i) for i in tqdm(range(n_samples), desc="MC Sampling")
            )
        else:
            results = Parallel(n_jobs=n_jobs)(
                delayed(worker)(i) for i in range(n_samples)
            )
        # Filter out failed draws.
        R_values = np.array([r for r in results if r is not None])
        if len(R_values) == 0:
            raise RuntimeError(
                "Monte Carlo simulation produced no valid radius estimates."
            )

        # Compute the median and standard deviation of the radius distribution.
        R_est_mean_value = np.mean(R_values)
        R_est_median_value = np.median(R_values)
        R_est_std_value = np.std(R_values, ddof=1)

        elapsed = time() - t_start
        self._logger.info(f"elapsed time: {elapsed:.2f} seconds")

        # Store the results for later visualization
        self._radius_mc_results_for_plotting = {
            'R_values': R_values
        }

        # Generate corner plot visualization of the Monte Carlo distribution
        if corner_plot:
            self.plot_results(
                radius_mc=True,
                save=True if corner_filename else False,
                filename=corner_filename
            )

        results = {
            "method": "mc",
            "n_samples": n_samples,
            "elapsed_time": elapsed,
            "radius_mean": R_est_mean_value * u.R_sun,
            "radius_median": R_est_median_value * u.R_sun,
            "radius_std": R_est_std_value * u.R_sun,
        }

        return results

    def estimate_radius(
        self,
        method="grid",
        accept=False,
        verbose=False,
        # Grid search parameters
        grid_min=0.1,
        grid_max=50.0,
        grid_points=10000,
        plot_chi2=False,
        refine_window=0.3,
        refine_steps=10000,
        # Monte Carlo parameters
        n_samples=1000,
        corner_plot=False,
        corner_filename=None,
        accept_method="median",
        # Common parameters
        n_jobs=-1,
        show_progress=True
    ):
        """
        Estimate the stellar radius using either grid search or Monte Carlo 
        simulation.

        This is a unified wrapper function that provides a single interface to two
        different methods for radius estimation. Both methods rely on the model:

            F_pred = (R / distance)^2 * π * B_λ(T_eff)

        where B_λ(T_eff) is the blackbody function evaluated at the effective
        temperature.

        Parameters
        ----------
        method : str, optional
            The method to use for radius estimation. Must be either 'grid' or 'mc'
            (default: 'grid').
        accept : bool, optional
            If True, updates the SED object with the estimated radius and its 
            error.
        verbose : bool, optional
            If True, prints additional information about the estimation process.

        Grid Search Parameters
        --------------------
        grid_min : float, optional
            Minimum candidate radius in solar radii for the grid search
            (default: 0.1).
        grid_max : float, optional
            Maximum candidate radius in solar radii for the grid search
            (default: 50.0).
        grid_points : int, optional
            Number of steps in the coarse grid search (default: 10000).
        refine_window : float, optional
            Fraction of the coarse best-fit value that defines the half-width of
            the refined search interval (default: 0.3).
        refine_steps : int, optional
            Number of steps in the refined grid search (default: 10000).
        plot_chi2 : bool, optional
            If True, plots the chi-square versus radius curve from the refined 
            grid search.

        Monte Carlo Parameters
        --------------------
        n_samples : int, optional
            Number of Monte Carlo draws (default: 1000).
        corner_plot : bool, optional
            If True, produces a corner plot of the Monte Carlo results.
        corner_filename : str or None, optional
            If provided, saves the corner plot to the specified filename.
        accept_method : str, optional
            The method to use for accepting the radius. Must be either 'median' or
            'mean' (default: 'median').

        Common Parameters
        ---------------
        n_jobs : int, optional
            Number of parallel jobs to use (-1 uses all processors; default: -1).
        show_progress : bool, optional
            If True, shows progress bars during the estimation process.
            Default is True.

        Returns
        -------
        tuple
            (R_est, R_err) where both are astropy.units.Quantity objects
            representing the estimated stellar radius and its 1σ uncertainty in
            solar radii.

        Raises
        ------
        ValueError
            If the 'method' parameter is not 'grid' or 'mc', or if required
            parameters are missing.

        Examples
        --------
        >>> # Estimate radius using grid search:
        >>> radius, radius_err = sed.estimate_radius(
        ...     method='grid',
        ...     accept=True,
        ...     verbose=True,
        ...     grid_min=1.0,
        ...     grid_max=5.0,
        ...     plot_chi2=True
        ... )
        >>> # Estimate radius using Monte Carlo:
        >>> radius, radius_err = sed.estimate_radius(
        ...     method='mc',
        ...     accept=True,
        ...     verbose=True,
        ...     n_samples=2000,
        ...     corner_plot=True,
        ...     corner_filename='radius_corner.png'
        ... )
        """
        self._logger.info(
            f"BEGIN - Estimating stellar radius using "
            f"method={method}, grid_min={grid_min}, grid_max={grid_max}, "
            f"n_samples={n_samples}"
        )
        
        # Validate grid search parameters
        self._logger.debug("Validating grid search parameters before radius "
                         "estimation")
        if grid_min <= 0.:
            self._logger.error(
                f"Invalid grid_min value: {grid_min} - must be positive"
            )
            raise ValueError("grid_min must be positive")
        if grid_max <= grid_min:
            self._logger.error(
                f"Invalid grid range: grid_max ({grid_max}) must be greater than "
                f"grid_min ({grid_min})"
            )
            raise ValueError("grid_max must be greater than grid_min")
        if not isinstance(grid_points, int) or grid_points < 2:
            self._logger.error(
                f"Invalid grid_points value: {grid_points} - must be an integer "
                ">= 2"
            )
            raise ValueError("grid_points must be an integer >= 2")

        # Validate Monte Carlo parameters
        self._logger.debug("Validating Monte Carlo parameters before radius "
                         "estimation")
        if not isinstance(n_samples, int) or n_samples < 1:
            self._logger.error(
                f"Invalid n_samples value: {n_samples} - must be a positive "
                "integer"
            )
            raise ValueError("n_samples must be a positive integer")
        if corner_filename is not None and not isinstance(corner_filename, str):
            self._logger.error(
                f"Invalid corner_filename type: {type(corner_filename)} - "
                "must be None or string"
            )
            raise ValueError("corner_filename must be None or a string")
        if accept_method not in ["median", "mean"]:
            self._logger.error(
                f"Invalid accept_method value: {accept_method} - must be "
                "'median' or 'mean'"
            )
            raise ValueError("accept_method must be either 'median' or 'mean'")

        # Validate common parameters
        self._logger.debug("Validating common parameters before radius estimation")
        if not isinstance(n_jobs, int):
            self._logger.error(
                f"Invalid n_jobs type: {type(n_jobs)} - must be integer"
            )
            raise ValueError("n_jobs must be an integer")
        if n_jobs == 0:
            self._logger.error("Invalid n_jobs value: cannot be 0")
            raise ValueError("n_jobs cannot be 0")
        if n_jobs < -1:
            self._logger.error(f"Invalid n_jobs value: {n_jobs} - must be >= -1")
            raise ValueError("n_jobs must be >= -1")

        # Validate boolean flags
        if not isinstance(accept, bool):
            self._logger.error(
                f"Invalid accept type: {type(accept)} - must be boolean"
            )
            raise ValueError("accept must be a boolean")
        if not isinstance(verbose, bool):
            self._logger.error(
                f"Invalid verbose type: {type(verbose)} - must be boolean"
            )
            raise ValueError("verbose must be a boolean")
        if not isinstance(plot_chi2, bool):
            self._logger.error(
                f"Invalid plot_chi2 type: {type(plot_chi2)} - must be boolean"
            )
            raise ValueError("plot_chi2 must be a boolean")
        if not isinstance(corner_plot, bool):
            self._logger.error(
                f"Invalid corner_plot type: {type(corner_plot)} - must be "
                "boolean"
            )
            raise ValueError("corner_plot must be a boolean")
        if not isinstance(show_progress, bool):
            self._logger.error(
                f"Invalid show_progress type: {type(show_progress)} - must be "
                "boolean"
            )
            raise ValueError("show_progress must be a boolean")
        

        # Validate method
        if method not in ["grid", "mc"]:
            self._logger.error(
                f"Invalid method: {method} - must be 'grid' or 'mc'"
            )
            raise ValueError("Method must be either 'grid' or 'mc'.")

        # Validate that effective temperature and distance are set
        self._logger.debug("Checking required stellar parameters are available")
        if self.teff is None or self.distance is None:
            self._logger.error(
                "Missing required parameters - effective temperature or distance "
                "not set"
            )
            raise ValueError(
                "Effective temperature and distance must be set to estimate the "
                "radius."
            )

        # Validate that effective temperature and distance errors are set
        if self.teff_error is None or self.distance_error is None:
            self._logger.error(
                "Missing required parameter errors - effective temperature error "
                "or distance error not set"
            )
            raise ValueError(
                "Effective temperature error and distance error must be set to "
                "estimate the radius."
            )

        self._logger.debug(
            f"Using stellar parameters: Teff={self.teff}±{self.teff_error}, "
            f"distance={self.distance}±{self.distance_error}"
        )
        
        # grid search method
        if method == "grid":
            self._logger.info(
                f"Using grid search method with {grid_points} points from "
                f"{grid_min} to {grid_max} Rsun"
            )
            result = self._estimate_radius_grid_search(
                radius_min=grid_min,
                radius_max=grid_max,
                coarse_steps=grid_points,
                refine_window=refine_window,
                refine_steps=refine_steps,
                n_jobs=n_jobs,
                plot_chi2=plot_chi2,
                show_progress=show_progress
            )
        # Monte Carlo method
        else:
            self._logger.info(f"Using Monte Carlo method with {n_samples} samples")
            result = self._estimate_radius_mc(
                n_samples=n_samples,
                n_jobs=n_jobs,
                corner_plot=corner_plot,
                corner_filename=corner_filename,
                show_progress=show_progress
            )
        
        # accept the radius
        if accept:
            if method == "mc":
                self._radius = result[
                    'radius_median' if accept_method == 'median' else 'radius_mean'
                ]
                self._radius_error = result['radius_std']
            else:
                self._radius = result['radius']
                self._radius_error = result['radius_error']
            self._logger.info("Radius accepted")
        
        if verbose:
            print("\nRadius Estimation Results:")
            print("--------------------------")
            print(f"Method: {method}")
            print(f"Elapsed time: {result['elapsed_time']:.2f} seconds")
            if method == "grid":
                print("\nGrid Search Results:")
                print(f"  Best-fit radius: {result['radius']}")
                print(f"  Uncertainty: ±{result['radius_error']}")
            else:
                print("\nMonte Carlo Statistics:")
                print(f"  Mean:   {result['radius_mean']}")
                print(f"  Median: {result['radius_median']}")
                print(f"  Std:    {result['radius_std']}")
                print(f"  N samples: {result['n_samples']}")
            print("--------------------------\n")
        
        if method == "mc":
            self._logger.info(
                f"END - Radius estimation complete: {result['radius_median']} ± "
                f"{result['radius_std']}"
            )
        else:
            self._logger.info(
                f"END - Radius estimation complete: {result['radius']} ± "
                f"{result['radius_error']}"
            )

        # Add success status based on radius value and error
        if method == "mc":
            result["success"] = (
                result["radius_median"].value != 0.0 and 
                not np.isnan(result["radius_std"].value)
            )
        else:  # grid method
            result["success"] = (
                result["radius"].value != 0.0 and 
                not np.isnan(result["radius_error"].value)
            )

        return result

    def _estimate_ebv_minimize(
        self,
        model="blackbody",
        ext_model=G23(Rv=3.1),
        ebv_initial=0.1,
        ebv_range=(0.0, 10.0),
        method="minimize",
        tol=1e-6,
        maxiter=1000,
        num_points=1000,
        show_progress=True,
        n_jobs=-1,
        optimization_method="L-BFGS-B"
    ):
        """Find the best-fit E(B-V) using blackbody fitting with interstellar
        extinction.
        
        Notes
        -----
        - Temperature, radius, and distance must be set in the SED object before 
          using this method.

        - The error in E(B-V) is approximated using the curvature of the
          residual function near the best-fit value. This assumes that the
          residual function is parabolic near the minimum.

        Parameters
        ----------
        model : str, optional
            The model to use for fitting.
            Currently, only "blackbody" is supported.
            (default: "blackbody").
        ext_model : `dust_extinction.BaseExtRvModel`, optional
            The extinction model to use (default: `G23(Rv=3.1)`).
        method : str, optional
            Method to find E(B-V), either "grid_search" or "minimize" 
            (default: "minimize").
        ebv_range : tuple, optional
            Range of E(B-V) values to search for (default: (0.0, 1.0)).
        num_points : int, optional
            Number of grid points for "grid_search" (default: 1000).
        ebv_initial : float, optional
            Initial guess for E(B-V) (default: 0.1, for "minimize").
        tol : float, optional
            Tolerance for optimization (default: 1e-6, for "minimize").
        maxiter : int, optional
            Maximum iterations for optimization (default: 1000, for "minimize").
        show_progress : bool, optional
            If True, show a progress bar (default: True, for "grid_search").
        n_jobs : int, optional
            Number of CPU cores for parallel computation (default: -1, for 
            "grid_search").
        optimization_method : str, optional
            Optimization method for scipy.optimize.minimize 
            (default: "L-BFGS-B").

        Returns
        -------
        dict
            Dictionary containing the following keys:
            
            ebv : float
                The best-fit E(B-V) value.
            ebv_error : float 
                Estimated error in the best-fit E(B-V) value.
            rms_error : float
                The root-mean-square error of the fit.
            elapsed_time : float
                Time taken for the method in seconds.
            method : str
                The method used to find E(B-V) ('grid_search' or 'minimize').
            residuals : array, optional
                Array of residuals at each grid point (only for 'grid_search' 
                method).
            ebvs : array, optional
                Array of E(B-V) values used in grid search (only for 'grid_search'
                method).
            optimization_result : OptimizeResult, optional
                Full optimization result object (only for 'minimize' method).
        
        Examples
        --------
        >>> from sedlib import SED
        
        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun

        >>> # find the E(B-V)
        >>> results = sed._estimate_ebv_minimize()
        >>> print(f"E(B-V): {results['ebv']:.3f}")
        >>> print(f"E(B-V) Error: {results['ebv_error']:.3f}")
        >>> print(f"RMS Error: {results['rms_error']:.4e}")
        >>> print(f"Elapsed Time: {results['elapsed_time']:.2f} seconds")
        """
        self._logger.info("BEGIN - Starting E(B-V) fitting")
        self._logger.debug(f"Method: {method}, E(B-V) range: {ebv_range}")

        if self.catalog is None or len(self.catalog) == 0:
            raise ValueError("Catalog data is required for fitting.")

        # check if the model is supported
        if model not in ["blackbody"]:
            raise ValueError(f"Model {model} is not supported.")

        # Validate extinction model and method
        if not isinstance(ext_model, BaseExtRvModel):
            raise ValueError(
                "ext_model must be an instance of dust_extinction.BaseExtRvModel."
            )
        if method not in ["grid_search", "minimize"]:
            raise ValueError(
                f"Invalid method {method}. Use 'grid_search' or 'minimize'."
            )

        # Validate ebv_range
        if (not isinstance(ebv_range, (tuple, list)) or len(ebv_range) != 2 or
                ebv_range[0] >= ebv_range[1]):
            raise ValueError(
                f"Invalid ebv_range {ebv_range}. "
                "Ensure it is a valid (min, max) tuple."
            )

        # Validate required attributes
        if self.teff is None or self.radius is None or self.distance is None:
            raise ValueError(
                "Temperature (teff), radius, and distance must be set in the SED "
                "object."
            )

        self._ext_model = ext_model
        self._logger.debug(
            f"Using extinction model: {ext_model.__class__.__name__}"
        )

        # Prepare observed data
        observed_wavelengths = self.catalog["wavelength"]
        observed_fluxes = self.catalog["flux"]
        self._logger.debug(f"Initial data points: {len(observed_wavelengths)}")

        # Check and filter data within extinction model range
        w1 = (1 / ext_model.x_range[-1]) * u.um
        w2 = (1 / ext_model.x_range[0]) * u.um
        mask = (w1 <= observed_wavelengths) & (observed_wavelengths <= w2)
        if not np.any(mask):
            raise ValueError(
                "No observed data within the extinction model's valid range."
            )

        observed_wavelengths = observed_wavelengths[mask]
        observed_fluxes = observed_fluxes[mask]
        self._logger.debug(
            f"Data points after filtering: {len(observed_wavelengths)}"
        )

        # Define the blackbody model
        scale = 1.0 * u.erg / (u.cm ** 2 * u.AA * u.s * u.sr)
        synth_model = BlackBody(temperature=self.teff, scale=scale)
        dR = (self.distance.to(u.cm) / self.radius.to(u.cm)) ** 2
        self._logger.debug(f"Blackbody model initialized with T={self.teff}")

        # Define the objective function
        def objective(ebv):
            # Suppress UserWarning when using grid_search method
            if method == "grid_search":
                warnings.filterwarnings("ignore", category=UserWarning)

            synth_ext_flux = (
                synth_model(observed_wavelengths) * np.pi / dR
            ) * ext_model.extinguish(observed_wavelengths, Ebv=ebv)

            var = np.abs(
                np.log10(synth_ext_flux.value) - np.log10(observed_fluxes.value)
            )

            return np.sum(var)

        # finding the best-fit E(B-V)
        start_time = time()
        self._logger.info("Starting E(B-V) optimization")

        if method == "grid_search":
            # Grid search implementation
            self._logger.debug(f"Grid search with {num_points} points")
            ebvs = np.linspace(ebv_range[0], ebv_range[1], num_points)
            residuals = Parallel(n_jobs=n_jobs)(
                delayed(objective)(ebv) for ebv in tqdm(
                    ebvs,
                    disable=not show_progress,
                    desc="Grid Search"
                )
            )
            residuals = np.array(residuals)
            best_index = np.argmin(residuals)
            best_ebv = ebvs[best_index]
            best_residual = residuals[best_index]
            self._logger.debug(
                f"Grid search completed, best E(B-V): {best_ebv:.4f}"
            )

        elif method == "minimize":
            # Minimization implementation
            self._logger.debug(f"Starting minimization with {optimization_method}")
            result = minimize(
                fun=objective,
                x0=[ebv_initial],
                bounds=[ebv_range],
                method=optimization_method,
                tol=tol,
                options={"maxiter": maxiter}
            )
            best_ebv = result.x[0]
            best_residual = result.fun
            self._logger.debug(
                f"Minimization completed, best E(B-V): {best_ebv:.4f}"
            )

        elapsed_time = time() - start_time
        self._logger.debug(
            f"Optimization completed in {elapsed_time:.2f} seconds"
        )

        # Calculate RMS error
        rms_error = np.sqrt(best_residual / len(observed_fluxes))
        self._logger.debug(f"RMS error: {rms_error:.4e}")

        # Estimate curvature-based error
        # perturbation: small step size for numerical curvature calculation
        # I found it by trial and error, it should be worked on in the future.
        perturbation = 1e-4
        perturbed_ebvs = [
            best_ebv - perturbation,
            best_ebv,
            best_ebv + perturbation
        ]
        residuals_around_min = [objective(ebv) for ebv in perturbed_ebvs]
        curvature_at_min = (
            residuals_around_min[2] -
            2 * residuals_around_min[1] +
            residuals_around_min[0]
        ) / (perturbation ** 2)

        if curvature_at_min <= 0:
            self._logger.warning(
                "Curvature near the minimum is non-positive; error estimation "
                "may not be reliable."
            )
            ebv_error = np.nan
        else:
            ebv_error = np.sqrt(2 / curvature_at_min)
            self._logger.debug(f"E(B-V) error estimate: {ebv_error:.4f}")

        results = {
            "ebv": best_ebv,
            "ebv_error": ebv_error,
            "rms_error": rms_error,
            "elapsed_time": elapsed_time,
            "method": method
        }

        if method == "grid_search":
            results["residuals"] = residuals
            results["ebvs"] = ebvs
        # remove this for sedhub compatibility
        #  elif method == "minimize":
        #     results["optimization_result"] = result

        self._logger.info("END - E(B-V) fitting completed successfully")

        return results

    def _estimate_ebv_mc(
        self,
        model="blackbody",
        ext_model=G23(Rv=3.1),
        ebv_range=(0.0, 10.0),
        ebv_initial=0.1,
        num_samples=1000,
        sampling="gaussian",
        tol=1e-6,
        maxiter=1000,
        optimization_method="L-BFGS-B",
        random_seed=None,
        n_jobs=-1,
        plot_corner=True,
        corner_filename=None,
        show_progress=True
    ):
        """
        E(B-V) estimation by Monte Carlo sampling.
        
        This method determines E(B-V) by sampling T, R, and distance from their
        respective error distributions, then optimizing E(B-V) for each draw.
        It uses parallelization, batch processing, and computational optimizations
        to maximize performance.

        Parameters
        ----------
        model : str, optional
            Model to use for fitting ("blackbody" by default).
        ext_model : dust_extinction.BaseExtRvModel, optional
            The extinction model. Default is G23(Rv=3.1). If None, uses 
            self.ext_model if set.
        ebv_range : tuple, optional
            Bounds for E(B-V) in optimization. Default = (0.0, 1.0).
        ebv_initial : float, optional
            Initial guess for E(B-V). Default = 0.1.
        num_samples : int, optional
            Number of Monte Carlo samples (draws) for T, R, d. Default = 1000.
        sampling : str, optional
            "gaussian" or "uniform". Default = "gaussian".
        tol : float, optional
            Tolerance for optimizer. Default = 1e-6.
        maxiter : int, optional
            Maximum iterations for optimizer. Default = 1000.
        optimization_method : str, optional
            scipy.optimize.minimize method. Default = "L-BFGS-B".
        random_seed : int, optional
            If set, fixes a seed for reproducible sampling. Default = None.
        n_jobs : int, optional
            Number of CPU cores for parallel draws. Default = -1 (use all cores).
        plot_corner : bool, optional
            If True, generates a corner plot of (T, R, distance, E(B-V)) for valid
            draws. Default = True.
        corner_filename : str or None, optional
            If provided, saves the corner plot to this filename (e.g.,
            "mycorner.png"). Otherwise just shows on screen if plot_corner=True.
        show_progress : bool, optional
            If True, shows a progress bar during fitting (default: True).

        Returns
        -------
        dict
            Dictionary containing keys: "ebv_mean", "ebv_std", "ebv_median",
            "method", "num_samples", "num_valid_samples", "elapsed_time".
        """
        self._logger.info(
            f"BEGIN - Estimating E(B-V) using optimized MC with {num_samples} "
            "samples"
        )
        
        # Validate catalog
        if self.catalog is None or len(self.catalog) == 0:
            self._logger.error(
                "Catalog data is missing, required for E(B-V) fitting"
            )
            raise ValueError("Catalog data is needed for fitting E(B-V).")

        # Model validation
        if model.lower() != "blackbody":
            self._logger.error(
                f"Unsupported model: {model}, only 'blackbody' is implemented"
            )
            raise ValueError("Only 'blackbody' model is currently implemented.")

        # Extinction model validation
        if ext_model is None:
            ext_model = self.ext_model
        if ext_model is None:
            self._logger.error("No extinction model provided or set in the object")
            raise ValueError("An extinction model is required.")

        # Check required parameters
        required_params = {
            'temperature': (self.teff, self.teff_error),
            'radius': (self.radius, self.radius_error),
            'distance': (self.distance, self.distance_error)
        }
        
        missing = [
            p for p, (val, err) in required_params.items() 
            if val is None or err is None
        ]
        if missing:
            self._logger.error(
                f"Missing required parameters: {', '.join(missing)}"
            )
            raise ValueError(
                f"Missing required parameters: {', '.join(missing)}"
            )

        # Extract values and convert to base units once 
        # (instead of repeated conversions)
        T_nom = self.teff.value
        T_err = self.teff_error.value
        R_nom = self.radius.to(u.cm).value
        R_err = self.radius_error.to(u.cm).value
        D_nom = self.distance.to(u.cm).value
        D_err = self.distance_error.to(u.cm).value
        
        self._logger.debug(
            f"Nominal values in base units - T: {T_nom:.1f}K, "
            f"R: {R_nom:.2e}cm, D: {D_nom:.2e}cm"
        )

        # Pre-compute geometric factors
        dR_nom = (D_nom / R_nom) ** 2
        self._logger.debug(f"Nominal geometric factor (d/R)^2: {dR_nom:.2e}")

        start_time = time()

        # Fix random seed if specified
        if random_seed is not None:
            np.random.seed(random_seed)

        # Pre-compute wavelength grid and filter within extinction model range
        observed_wavelengths = self.catalog["wavelength"]
        observed_fluxes = self.catalog["flux"]
        
        # Filter valid wavelengths only once
        w1 = (1 / ext_model.x_range[-1]) * self._wavelength_unit
        w2 = (1 / ext_model.x_range[0]) * self._wavelength_unit
        mask = (w1 <= observed_wavelengths) & (observed_wavelengths <= w2)
        
        if not np.any(mask):
            self._logger.error("No observed data within extinction model range")
            raise ValueError(
                "No observed data within the extinction model range."
            )
        
        # Convert to NumPy arrays and extract values to avoid repeated conversions
        wavelengths_values = observed_wavelengths[mask].value
        wavelengths_unit = observed_wavelengths[mask].unit
        flux_values = observed_fluxes[mask].value
        log_flux_values = np.log10(flux_values)  # Pre-compute logs
        
        self._logger.debug(
            f"Using {np.sum(mask)} data points within extinction model range"
        )
        
        # Pre-compute a grid of blackbody spectra for temperatures
        T_samples = np.empty(num_samples)
        R_samples = np.empty(num_samples)
        D_samples = np.empty(num_samples)
        
        # Draw parameters using vectorized operations (faster than loops)
        if sampling == "gaussian":
            T_samples = np.random.normal(
                loc=T_nom, scale=T_err, size=num_samples
            )
            R_samples = np.random.normal(
                loc=R_nom, scale=R_err, size=num_samples
            )
            D_samples = np.random.normal(
                loc=D_nom, scale=D_err, size=num_samples
            )
        else:  # uniform
            # For uniform sampling, use +/- 3 sigma range
            T_samples = np.random.uniform(
                low=T_nom-3*T_err, high=T_nom+3*T_err, size=num_samples
            )
            R_samples = np.random.uniform(
                low=R_nom-3*R_err, high=R_nom+3*R_err, size=num_samples
            )
            D_samples = np.random.uniform(
                low=D_nom-3*D_err, high=D_nom+3*D_err, size=num_samples
            )
        
        # Filter invalid samples immediately
        valid_mask = (T_samples > 0) & (R_samples > 0) & (D_samples > 0)
        T_samples = T_samples[valid_mask]
        R_samples = R_samples[valid_mask]
        D_samples = D_samples[valid_mask]
        valid_count = np.sum(valid_mask)
        
        self._logger.debug(
            f"Generated {valid_count} valid parameter sets out of {num_samples}"
        )
        
        # Create a faster objective function
        def make_fast_objective(TK, R_cm, D_cm):
            """Optimized objective function with minimized conversions"""
            # Pre-compute the geometric factor
            dR = (D_cm / R_cm) ** 2
            
            # Create blackbody model (converted to scalars to avoid repeated 
            # unit conversions)
            scale = 1.0 * u.erg / (u.cm**2 * u.AA * u.s * u.sr)
            bb_model = BlackBody(temperature=TK * u.K, scale=scale)
            
            # Pre-compute the blackbody flux (once per objective function instance)
            # Convert back to proper units just for the blackbody calculation
            wl_with_units = wavelengths_values * wavelengths_unit
            bb_flux = bb_model(wl_with_units).value * np.pi / dR
            
            # The actual objective function
            def objective(ebv):
                # Apply extinction without unit conversions
                extinction = ext_model.extinguish(wl_with_units, Ebv=ebv)
                flux_with_ext = bb_flux * extinction
                
                # Faster computation using pre-computed logs
                log_flux_ext = np.log10(flux_with_ext)
                return np.sum(np.abs(log_flux_ext - log_flux_values))
            
            return objective
        
        results_list = []
        
        # Determine optimal batch size based on wavelength points and valid samples
        batch_size = self._determine_optimal_batch_size(
            len(wavelengths_values), valid_count
        )
        
        n_batches = max(1, (valid_count + batch_size - 1) // batch_size)
        
        for batch_idx in range(n_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, valid_count)
            
            batch_T = T_samples[start_idx:end_idx]
            batch_R = R_samples[start_idx:end_idx]
            batch_D = D_samples[start_idx:end_idx]
            
            self._logger.debug(
                f"Processing batch {batch_idx+1}/{n_batches} with "
                f"{end_idx-start_idx} samples"
            )
            
            def worker(idx):
                """Worker function"""
                warnings.filterwarnings("ignore", category=UserWarning)
                
                # Get parameters for this sample
                T_i = batch_T[idx]
                R_i = batch_R[idx]
                D_i = batch_D[idx]
                
                # Create objective function
                obj_func = make_fast_objective(T_i, R_i, D_i)
                
                # Use Brent optimization for 1D problem 
                # (faster than L-BFGS-B for single param)
                method = ("Brent" if optimization_method == "L-BFGS-B" 
                         else optimization_method)
                
                try:
                    from scipy.optimize import minimize_scalar
                    
                    # Use minimize_scalar for 1D problems - much faster than 
                    # regular minimize
                    result = minimize_scalar(
                        fun=obj_func,
                        bounds=ebv_range,
                        method='bounded',
                        options={'xatol': tol, 'maxiter': maxiter}
                    )
                    ebv_val = result.x
                except:
                    # Fall back to regular minimize if minimize_scalar not 
                    # available or fails
                    result = minimize(
                        fun=obj_func,
                        x0=[ebv_initial],
                        bounds=[ebv_range],
                        method=optimization_method,
                        tol=tol,
                        options={"maxiter": maxiter}
                    )
                    ebv_val = result.x[0]
                    
                return (T_i, R_i, D_i, ebv_val)
            
            # Process this batch in parallel
            batch_size_actual = end_idx - start_idx
            indices = list(range(batch_size_actual))
            
            with tqdm_joblib(
                desc=f"Batch {batch_idx+1}/{n_batches}", 
                total=batch_size_actual,
                disable=not show_progress
            ):
                batch_results = Parallel(n_jobs=n_jobs)(
                    delayed(worker)(i) for i in indices
                )
            
            # Extend results list with valid results
            results_list.extend([r for r in batch_results if r[3] is not None])
        
        # Process results
        if not results_list:
            self._logger.warning("All MC draws invalid or no E(B-V) found")
            warnings.warn("All MC draws invalid or no E(B-V) found.")
            return None
        
        # Convert to numpy array for easier handling
        valid_records = np.array(results_list)
        T_valid = valid_records[:, 0]
        R_valid = valid_records[:, 1]
        D_valid = valid_records[:, 2]
        ebv_array = valid_records[:, 3]
        
        # Convert back to original units for corner plot and results
        T_valid_with_units = T_valid
        # Convert cm back to solar radii
        R_valid_with_units = R_valid / (u.R_sun.to(u.cm))  
        # Convert cm back to parsecs
        D_valid_with_units = D_valid / (u.pc.to(u.cm))     
        
        self._logger.debug(
            f"Using {len(valid_records)} valid records "
            f"({len(valid_records)/valid_count:.1%} of valid parameter sets)"
        )
        
        # Statistical computation
        ebv_mean = np.mean(ebv_array)
        ebv_median = np.median(ebv_array)
        ebv_std = np.std(ebv_array, ddof=1)
        
        end_time = time()
        elapsed = end_time - start_time
        
        self._logger.info(
            f"E(B-V) results - mean: {ebv_mean:.4f}, "
            f"median: {ebv_median:.4f}, std: {ebv_std:.4f}, "
            f"elapsed time: {elapsed:.2f} seconds"
        )
        
        results = {
            "ebv_mean": ebv_mean,
            "ebv_std": ebv_std,
            "ebv_median": ebv_median,
            "method": "mc",
            "num_samples": num_samples,
            "num_valid_samples": len(ebv_array),
            "elapsed_time": elapsed,
        }
        
        self._ebv_mc_results_for_plotting = {
            "T_valid_with_units": T_valid_with_units,
            "R_valid_with_units": R_valid_with_units,
            "D_valid_with_units": D_valid_with_units,
            "ebv_array": ebv_array
        }

        if plot_corner:
            self.plot_results(
                ebv_mc=True,
                save=True if corner_filename else False,
                filename=corner_filename
            )
        
        self._logger.debug("END - E(B-V) Monte Carlo estimation complete")

        return results

    def estimate_ebv(
        self,
        method="minimize",
        model="blackbody", 
        ext_model=G23(Rv=3.1),
        accept=True,
        verbose=False,
        # Grid search and minimize parameters
        ebv_range=(0.0, 10.0),
        ebv_initial=0.1,
        tol=1e-6,
        maxiter=1000,
        num_points=10000,
        optimization_method="L-BFGS-B",
        # Monte Carlo parameters
        n_samples=1000,
        sampling="gaussian",
        plot_corner=False,
        corner_filename=None,
        # Common parameters
        n_jobs=-1,
        random_seed=None,
        show_progress=True
    ):
        """
        Estimate interstellar extinction E(B-V) using blackbody fitting.

        This is a unified wrapper function that provides a single interface to three
        different methods for E(B-V) estimation: grid search, minimization, and
        Monte Carlo simulation.

        Parameters
        ----------
        method : str, optional
            The method to use for E(B-V) estimation. Must be one of:
            - 'minimize': Direct minimization of the objective function. Default.
            - 'grid_search': Grid search over E(B-V) range.
            - 'mc': Monte Carlo sampling of parameters
        model : str, optional
            The model to use for flux prediction. Currently only 'blackbody' is
            supported (default: 'blackbody').
        ext_model : dust_extinction.BaseExtRvModel, optional
            The extinction model to use (default: G23 with Rv=3.1).
        accept : bool, optional
            If True, updates the SED object with the estimated E(B-V) and its error
            (default: True).
        verbose : bool, optional
            If True, prints additional information during the fitting process
            (default: False).

        Grid Search and Minimize Parameters
        ---------------------------------
        ebv_range : tuple of float, optional
            The (min, max) range of E(B-V) values to consider (default: (0.0, 1.0))
        ebv_initial : float, optional
            The initial guess for E(B-V) when using 'minimize' method
            (default: 0.1).
        tol : float, optional
            The convergence tolerance for minimization (default: 1e-6).
        maxiter : int, optional
            The maximum number of iterations for minimization (default: 1000).
        num_points : int, optional
            The number of points to use in the grid search (default: 10000).
        optimization_method : str, optional
            The optimization method to use with scipy.optimize.minimize
            (default: 'L-BFGS-B').

        Monte Carlo Parameters
        -------------------
        n_samples : int, optional
            The number of Monte Carlo samples to use (default: 1000).
        sampling : str, optional
            The sampling method to use. Must be one of 'gaussian' or 'uniform'
            (default: 'gaussian').
        plot_corner : bool, optional
            If True, creates corner plot for MC results (default: False).
        corner_filename : str, optional
            Filename to save corner plot (default: None).

        Common Parameters
        ---------------
        n_jobs : int, optional
            Number of parallel jobs. -1 uses all cores (default: -1).
        random_seed : int, optional
            Random seed for reproducibility (default: None).
        show_progress : bool, optional
            If True, shows a progress bar during fitting (default: True).

        Returns
        -------
        tuple or dict
            By default, returns (ebv, ebv_err) where both are float values.

        Raises
        ------
        ValueError
            If required parameters are missing or invalid values are provided.

        Examples
        --------
        >>> from sedlib import SED
        >>> from astropy import units as u
        >>> 
        >>> # Create and set up SED object
        >>> sed = SED(name='Vega')
        >>> sed.teff = 9600 * u.K
        >>> sed.teff_error = sed.teff * 0.01
        >>> sed.radius = 2.818 * u.Rsun
        >>> sed.radius_error = sed.radius * 0.01
        >>> sed.distance = 7.68 * u.pc
        >>> sed.distance_error = sed.distance * 0.01
        >>> 
        >>> # Estimate using grid search
        >>> stats = sed.estimate_ebv(
        ...     method='grid',
        ...     verbose=True,
        ...     num_points=2000,
        ...     show_progress=True,
        ...     return_stats=True
        ... )
        >>> print(f"Grid Search RMS: {stats['rms_error']:.2e}")
        >>> 
        >>> # Monte Carlo estimation with corner plot
        >>> stats = sed.estimate_ebv(
        ...     method='mc',
        ...     n_samples=2000,
        ...     sampling='gaussian',
        ...     plot_corner=True,
        ...     corner_filename='ebv_corner.png',
        ...     return_stats=True
        ... )
        >>> print(f"MC mean E(B-V): {stats['ebv_mean']:.3f}")
        """
        self._logger.info(
            f"BEGIN - Estimating interstellar extinction using "
            f"method={method}, model={model}, "
            f"ext_model={ext_model.__class__.__name__}"
        )
        
        # Validate method
        self._logger.debug("Validating input parameters for E(B-V) estimation")
        if method not in ["grid_search", "minimize", "mc"]:
            self._logger.error(
                f"Invalid method: {method} - must be 'grid_search', 'minimize', "
                "or 'mc'"
            )
            raise ValueError(
                "Method must be one of 'grid_search', 'minimize', or 'mc'."
            )

        # Validate model
        if model not in ["blackbody"]:
            self._logger.error(
                f"Invalid model: {model} - currently only 'blackbody' is "
                "supported"
            )
            raise ValueError(
                "Model must be 'blackbody'. Other models not yet supported."
            )

        # Validate extinction model
        if not isinstance(ext_model, BaseExtRvModel):
            self._logger.error(
                f"Invalid extinction model type: {type(ext_model)} - "
                "must be a dust_extinction.BaseExtRvModel instance"
            )
            raise ValueError(
                "ext_model must be a dust_extinction.BaseExtRvModel instance."
            )

        # Check for required parameters
        if self.teff is None:
            self._logger.error(
                "Missing required parameter: effective temperature not set"
            )
            raise ValueError(
                "Effective temperature (teff) must be set to estimate E(B-V)."
            )
        
        if self.radius is None:
            self._logger.error("Missing required parameter: stellar radius not set")
            raise ValueError("Stellar radius must be set to estimate E(B-V).")
            
        if self.distance is None:
            self._logger.error("Missing required parameter: distance not set")
            raise ValueError("Distance must be set to estimate E(B-V).")

        # For minimize and grid search methods
        if method in ["minimize", "grid_search"]:
            self._logger.debug(
                f"Using {method} method for E(B-V) estimation with range "
                f"{ebv_range}"
            )
            if method == "minimize":
                self._logger.debug(
                    f"Optimization method: {optimization_method}, "
                    f"initial E(B-V): {ebv_initial}"
                )
            else:
                self._logger.debug(
                    f"Grid search with {num_points} points in range {ebv_range}"
                )
                
            result = self._estimate_ebv_minimize(
                model=model,
                ext_model=ext_model,
                ebv_initial=ebv_initial,
                ebv_range=ebv_range,
                method=method,
                tol=tol,
                maxiter=maxiter,
                num_points=num_points,
                show_progress=show_progress,
                n_jobs=n_jobs,
                optimization_method=optimization_method
            )
        # Monte Carlo method
        else:
            self._logger.debug(
                f"Using Monte Carlo method with {n_samples} samples, "
                f"sampling={sampling}"
            )
            
            result = self._estimate_ebv_mc(
                model=model,
                ext_model=ext_model,
                ebv_range=ebv_range,
                ebv_initial=ebv_initial,
                num_samples=n_samples,
                sampling=sampling,
                tol=tol,
                maxiter=maxiter,
                optimization_method=optimization_method,
                random_seed=random_seed,
                n_jobs=n_jobs,
                plot_corner=plot_corner,
                corner_filename=corner_filename,
                show_progress=show_progress
            )

        if verbose:
            print("\nE(B-V) Estimation Results")
            print("-" * 30)
            print(f"Method:         {result['method']}")
            print(f"Elapsed Time:   {result['elapsed_time']:.2f} s")
            
            if method in ["grid_search", "minimize"]:
                print(f"\nBest-fit Results:")
                print(f"  E(B-V):       {result['ebv']:.4f}")
                print(f"  Uncertainty:   ±{result['ebv_error']:.4f}")
                print(f"  RMS Error:     {result['rms_error']:.4e}")
            
            if method in ["mc"]:
                print("\nMonte Carlo Statistics:")
                print(f"  Mean:         {result['ebv_mean']:.4f}")
                print(f"  Std Dev:      {result['ebv_std']:.4f}")
                print(f"  Median:       {result['ebv_median']:.4f}")
                print(
                    f"\nValid Samples:  {result['num_valid_samples']} of "
                    f"{result['num_samples']}"
                )
                print("\nNote: Uncertainty estimated from Monte Carlo standard "
                      "deviation")
            
            print("-" * 30 + "\n")
        
        # accept the result
        if accept:
            if method in ["grid_search", "minimize"]:
                self.ebv = result['ebv']
                self.ebv_error = result['ebv_error']
                self.ext_model = ext_model
            if method in ["mc"]:
                self.ebv = result['ebv_mean']
                self.ebv_error = result['ebv_std']
                self.ext_model = ext_model
            
            self._logger.debug(
                f"Storing E(B-V) result in SED object: "
                f"{self.ebv:.4f} ± {self.ebv_error:.4f}"
            )

        self._logger.info(
            f"END - E(B-V) estimation complete: "
            f"{self.ebv:.4f} ± {self.ebv_error:.4f}"
        )

        # Success status based on E(B-V) value and error
        if method in ["grid_search", "minimize"]:
            result["success"] = (
                result["ebv"] != 0.0 and 
                not np.isnan(result["ebv"]) and
                not np.isnan(result["ebv_error"])
            )
        else:  # mc method
            result["success"] = (
                result["ebv_mean"] != 0.0 and 
                not np.isnan(result["ebv_mean"]) and
                not np.isnan(result["ebv_std"])
            )

        return result

    def compute_A_lambda(self):
        """Compute A_lambda values for all filters in the catalog and update the
        catalog.

        The method uses the `_calculate_A_lambda_for_filter` function to compute
        A_lambda for each filter and appends the calculated value to the
        respective rows in the catalog.

        Notes
        -----
        - Filters with a `None` value for `filterID` are skipped, and `None` is
          written to the corresponding A_lambda column.
        - The method creates or updates the `A_lambda` column in the catalog.

        Returns
        -------
        None
            Updates the catalog in place.

        Examples
        --------
        >>> from sedlib import SED
        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun
        >>> sed.distance = 7.68 * u.pc
        >>> sed.estimate_ebv()
        >>> sed.compute_A_lambda()
        """
        self._logger.info(
            "compute_A_lambda: begin - Computing extinction values for all filters"
        )

        if self.catalog is None:
            self._logger.error(
                "compute_A_lambda: Catalog data is missing for calculating "
                "A_lambda values"
            )
            raise ValueError(
                "Catalog data is required for calculating A_lambda values."
            )

        if (self.teff is None or self.radius is None or
                self.distance is None or self.ebv is None):
            self._logger.error(
                "compute_A_lambda: Missing required parameters (teff, radius, "
                "distance, or ebv)"
            )
            raise ValueError(
                "Temperature (teff), radius, distance, and E(B-V) must be set "
                "in the SED object."
            )

        if self.ext_model is None:
            self._logger.error("compute_A_lambda: Extinction model is not set")
            raise ValueError("Extinction model must be set in the SED object.")

        self._logger.debug(
            f"compute_A_lambda: Using teff={self.teff}, radius={self.radius}, "
            f"distance={self.distance}, ebv={self.ebv}"
        )

        # Ensure the catalog has `A_lambda` and `A_lambda_err` columns
        if "A_lambda" not in self.catalog.table.colnames:
            self._logger.debug(
                "compute_A_lambda: Creating A_lambda column in catalog"
            )
            self.catalog.table["A_lambda"] = [None] * len(self.catalog.table)
        if "A_lambda_err" not in self.catalog.table.colnames:
            self._logger.debug(
                "compute_A_lambda: Creating A_lambda_err column in catalog"
            )
            self.catalog.table["A_lambda_err"] = [None] * len(self.catalog.table)

        self._logger.info(
            f"compute_A_lambda: Processing {len(self.catalog.table)} filters in "
            "the catalog"
        )

        # Loop through each row in the catalog
        for i, row in enumerate(self.catalog.table):
            filter_object = row["filter"]
            if filter_object is None or filter_object.filterID is None:
                # Skip rows without valid filter information
                self._logger.warning(
                    f"compute_A_lambda: Skipping row {i}: Filter information is "
                    "missing"
                )
                self.catalog.table["A_lambda"][i] = None
                self.catalog.table["A_lambda_err"][i] = None
                continue

            try:
                # Calculate A_lambda and its error for the current filter
                self._logger.debug(
                    f"compute_A_lambda: Calculating extinction for filter "
                    f"'{filter_object.name}' (row {i})"
                )
                A_lambda, A_lambda_err = self._compute_A_lambda_for_filter(
                    filter_object
                )

                self.catalog.table["A_lambda"][i] = A_lambda
                self.catalog.table["A_lambda_err"][i] = A_lambda_err

                self._logger.info(
                    f"compute_A_lambda: Row {i}: Calculated A_lambda for filter "
                    f"'{filter_object.name}': {A_lambda:.4f} ± {A_lambda_err:.4f}"
                )
            except Exception as e:
                self._logger.error(
                    f"compute_A_lambda: Error calculating A_lambda for filter "
                    f"'{filter_object.name}' (row {i}): {e}"
                )
                self.catalog.table["A_lambda"][i] = None
                self.catalog.table["A_lambda_err"][i] = None
                continue

        self._logger.debug(
            "compute_A_lambda: Setting format for A_lambda and A_lambda_err "
            "columns"
        )
        self.catalog.table['A_lambda'].info.format = '.3f'
        self.catalog.table['A_lambda_err'].info.format = '.3f'

        self._logger.info(
            "compute_A_lambda: end - Completed calculating A_lambda values for "
            "all filters"
        )

    def _compute_A_lambda_for_filter(self, filter_object, delta_E=1e-4):
        """Compute the A_lambda value for a given filter and its uncertainty.

        Warning
        -------
        Internal method only, not suitable for direct use.

        This method computes the wavelength-dependent extinction A_λ for a
        specific photometric filter by comparing the integrated flux through the
        filter with and without extinction applied. The extinction is calculated
        using the relationship:

        A_λ = -2.5 log₁₀(F_ext/F_0)

        where F_ext is the extinguished flux and F_0 is the intrinsic flux.
        The fluxes are computed by integrating a blackbody spectrum weighted
        by the filter transmission curve:

        F = ∫ B_λ(T) × T_λ × e^(-τ_λ) dλ

        where B_λ(T) is the Planck function at temperature T,
        T_λ is the filter transmission, and τ_λ is the optical depth
        (τ_λ = 0 for F_0).

        The uncertainty in A_λ is estimated through numerical differentiation
        with respect to E(B-V), accounting for the propagation of the E(B-V)
        uncertainty.

        Parameters
        ----------
        filter_object : Filter
            The filter object for which to calculate A_lambda.
        delta_E : float, optional
            The perturbation in E(B-V) used for numerical differentiation.
            Default is 1e-4.

        Returns
        -------
        tuple
            A tuple (A_lambda, sigma_A_lambda) where A_lambda is the calculated
            extinction for the filter and sigma_A_lambda is its estimated
            uncertainty.

        Raises
        ------
        ValueError
            If required parameters (teff, radius, distance, ebv, ext_model) or
            E(B-V) error (_ebv_error) are not set in the SED object.

        Examples
        --------
        >>> sed = SED('Vega')
        >>> sed.teff = 9600 * u.K
        >>> sed.radius = 2.818 * u.R_sun  
        >>> sed.distance = 7.68 * u.pc
        >>> sed.estimate_ebv()
        >>> A_lambda, A_err = sed._compute_A_lambda_for_filter('GAIA/GAIA3.G')
        """
        self._logger.debug(
            f"BEGIN - Computing extinction for "
            f"filter '{filter_object.name}' with delta_E={delta_E}"
        )

        # Validate inputs
        if not isinstance(filter_object, Filter):
            self._logger.error(
                "_compute_A_lambda_for_filter: Invalid filter object type"
            )
            raise ValueError("filter_object must be a Filter object.")
        if self.teff is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: Temperature (teff) is not set"
            )
            raise ValueError("Temperature (teff) must be set in the SED object.")
        if self.radius is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: Radius is not set"
            )
            raise ValueError("Radius must be set in the SED object.")
        if self.distance is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: Distance is not set"
            )
            raise ValueError("Distance must be set in the SED object.")
        if self.ebv is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: E(B-V) is not set"
            )
            raise ValueError("E(B-V) must be set in the SED object.")
        if self._ebv_error is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: E(B-V) error is not set"
            )
            raise ValueError("E(B-V) error must be set in the SED object.")
        if self.ext_model is None:
            self._logger.error(
                "_compute_A_lambda_for_filter: Extinction model is not set"
            )
            raise ValueError("Extinction model must be set in the SED object.")

        # Number of wavelength points for integration
        num_points = 10000
        self._logger.debug(
            f"_compute_A_lambda_for_filter: Using {num_points} wavelength points "
            "for integration"
        )

        # Scale factor for blackbody flux units
        scale = 1.0 * u.erg / (u.cm ** 2 * u.AA * u.s * u.sr)
        # Calculate geometric dilution factor based on distance/radius ratio
        dR = (self.distance.to(u.cm) / self.radius.to(u.cm)) ** 2
        self._logger.debug(
            f"_compute_A_lambda_for_filter: Geometric dilution factor (d/r)^2 = "
            f"{dR}"
        )

        # Create blackbody object for intrinsic flux calculation
        blackbody = BlackBody(temperature=self.teff, scale=scale)
        self._logger.debug(
            f"_compute_A_lambda_for_filter: Created blackbody with T={self.teff}"
        )

        # Generate wavelength grid covering the filter bandpass
        filter_wavelengths = np.linspace(
            filter_object.WavelengthMin,
            filter_object.WavelengthMax,
            num_points
        )
        self._logger.debug(
            f"_compute_A_lambda_for_filter: Wavelength range: "
            f"{filter_object.WavelengthMin:.2f} to "
            f"{filter_object.WavelengthMax:.2f}"
        )

        # Get filter transmission at each wavelength
        filter_transmissions = filter_object(filter_wavelengths)
        # Calculate intrinsic blackbody flux, scaled by stellar radius and
        # distance
        filter_synth_flux = blackbody(filter_wavelengths) * np.pi / dR
        # Multiply by filter transmission to get filtered flux
        transmission_filter_synth_flux = filter_transmissions * filter_synth_flux
        self._logger.debug(
            "_compute_A_lambda_for_filter: Calculated intrinsic flux through "
            "filter"
        )

        def compute_extinction_for_ebv(ebv):
            # Apply extinction to synthetic spectrum using extinction model
            filter_synth_ext_flux = (
                filter_synth_flux *
                self.ext_model.extinguish(filter_wavelengths, Ebv=ebv)
            )
            # Apply filter transmission to extinguished spectrum
            transmission_filter_synth_ext_flux = (
                filter_transmissions * filter_synth_ext_flux
            )

            # Integrate over wavelength to get total filtered flux
            # For both intrinsic and extinguished spectra
            integrated_flux = simpson(
                y=transmission_filter_synth_flux,
                x=filter_wavelengths
            )
            integrated_ext_flux = simpson(
                y=transmission_filter_synth_ext_flux,
                x=filter_wavelengths
            )

            # Calculate extinction in magnitudes using flux ratio
            return 2.5 * np.log10(integrated_flux / integrated_ext_flux)

        self._logger.debug(
            f"_compute_A_lambda_for_filter: Computing extinction at "
            f"E(B-V)={self.ebv}"
        )
        # Calculate A_lambda at nominal E(B-V) and at perturbed values
        A_nom = compute_extinction_for_ebv(self.ebv)

        self._logger.debug(
            f"_compute_A_lambda_for_filter: Computing extinction at "
            f"E(B-V)={self.ebv + delta_E} for uncertainty estimation"
        )
        A_plus = compute_extinction_for_ebv(self.ebv + delta_E)

        self._logger.debug(
            f"_compute_A_lambda_for_filter: Computing extinction at "
            f"E(B-V)={self.ebv - delta_E} for uncertainty estimation"
        )
        A_minus = compute_extinction_for_ebv(self.ebv - delta_E)

        # Calculate uncertainty using numerical derivative
        # dA_lambda/dE(B-V) ≈ [A(E+δE) - A(E-δE)]/(2δE)
        derivative = (A_plus - A_minus) / (2 * delta_E)
        # Propagate E(B-V) uncertainty to A_lambda
        sigma_A = abs(derivative) * self._ebv_error

        self._logger.debug(
            f"_compute_A_lambda_for_filter: Calculated dA/dE(B-V) = "
            f"{derivative:.4f}, sigma_A = {sigma_A:.4f}"
        )

        self._logger.info(
            f"_compute_A_lambda_for_filter: Calculated A_lambda for filter "
            f"'{filter_object.name}': {A_nom:.4f} ± {sigma_A:.4f} mag"
        )

        self._logger.debug(
            "END - Returning (A_lambda, sigma_A_lambda)"
        )
        return A_nom, sigma_A

    def compute_absolute_magnitudes(self):
        """Convert all magnitudes in the catalog to absolute magnitudes.

        Updates the catalog table by adding 'abs_mag' and 'abs_mag_err' columns
        calculated using the distance modulus formula:

        M = m + 5*log10(d/10) - A_lambda
        where:
            M = absolute magnitude
            m = apparent magnitude
            d = distance in parsecs
            A_lambda = extinction at the filter wavelength

        The uncertainties are propagated considering errors in magnitude,
        distance, and extinction measurements using:
        σ_M = sqrt(σ_m^2 + (5*log10(e)*σ_d/d)^2 + σ_A^2)
        where:
            σ_M = uncertainty in absolute magnitude
            σ_m = uncertainty in apparent magnitude
            σ_d = uncertainty in distance
            d = distance
            σ_A = uncertainty in extinction
            e = Euler's number

        Raises
        ------
        ValueError
            If catalog data or distance is not set in the SED object.

        Examples
        --------
        >>> from sedlib import SED
        >>> from astropy import units as u
        >>>
        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun
        >>> sed.distance = 7.68 * u.pc
        >>>
        >>> sed.estimate_ebv()
        >>> sed.compute_A_lambda()
        >>> sed.compute_absolute_magnitudes()
        """
        self._logger.info(
            "BEGIN - Converting apparent magnitudes to absolute magnitudes"
        )

        # Check if required data is available
        if self.catalog is None:
            self._logger.error(
                "compute_absolute_magnitudes: Catalog data is missing"
            )
            raise ValueError(
                "Catalog data is required for calculating absolute magnitudes"
            )

        if self.distance is None:
            self._logger.error("compute_absolute_magnitudes: Distance is not set")
            raise ValueError("Distance must be set in the SED object")

        required_columns = ['A_lambda', 'A_lambda_err', 'mag', 'mag_err']
        missing_columns = []
        for col in required_columns:
            if (col not in self.catalog.table.colnames or
                    self.catalog.table[col] is None):
                missing_columns.append(col)

        if missing_columns:
            missing_str = ', '.join(missing_columns)
            self._logger.error(
                f"compute_absolute_magnitudes: Required column(s) missing: "
                f"{missing_str}"
            )
            raise ValueError(
                f"{missing_str} must be computed before computing absolute "
                "magnitudes"
            )

        self._logger.debug(
            f"compute_absolute_magnitudes: Using distance={self.distance}, "
            f"distance_error={self._distance_error}"
        )

        # Ensure the catalog has `abs_mag` and `abs_mag_err` columns
        if 'abs_mag' not in self.catalog.table.colnames:
            self._logger.debug(
                "compute_absolute_magnitudes: Creating abs_mag column in catalog"
            )
            self.catalog.table['abs_mag'] = [None] * len(self.catalog.table)
        if 'abs_mag_err' not in self.catalog.table.colnames:
            self._logger.debug(
                "compute_absolute_magnitudes: Creating abs_mag_err column in "
                "catalog"
            )
            self.catalog.table['abs_mag_err'] = [None] * len(self.catalog.table)

        abs_mags = list()
        abs_mags_err = list()

        self._logger.info(
            f"compute_absolute_magnitudes: Processing {len(self.catalog.table)} "
            "filters in catalog"
        )

        # Calculate absolute magnitude for each filter in the catalog
        for i, row in enumerate(self.catalog.table):
            mag = row['mag']
            mag_err = row['mag_err']
            a_lambda = row['A_lambda']
            a_lambda_err = row['A_lambda_err']

            # Skip if magnitude or extinction data is missing
            if mag is None or a_lambda is None:
                self._logger.warning(
                    f"compute_absolute_magnitudes: Skipping row {i} due to "
                    "missing magnitude or extinction data"
                )
                abs_mags.append(None)
                abs_mags_err.append(None)
                continue

            # Calculate absolute magnitude using distance modulus formula
            abs_mag = (
                mag + 5 - 5 * np.log10(self.distance.to(u.pc).value) - a_lambda
            )

            # Propagate errors
            abs_mag_err = np.sqrt(
                mag_err**2 +
                (5 * self._distance_error.value /
                 (self._distance.value * np.log(10)))**2 +
                a_lambda_err**2
            )

            self._logger.debug(
                f"compute_absolute_magnitudes: Row {i}: Converted mag={mag:.3f} "
                f"to abs_mag={abs_mag:.3f}"
            )
            abs_mags.append(abs_mag)
            abs_mags_err.append(abs_mag_err)

        # Update the catalog with calculated absolute magnitudes
        self._logger.debug(
            "compute_absolute_magnitudes: Updating catalog with calculated "
            "absolute magnitudes"
        )
        self.catalog.table['abs_mag'] = abs_mags
        self.catalog.table['abs_mag_err'] = abs_mags_err

        # Set display format for the new columns
        self._logger.debug(
            "compute_absolute_magnitudes: Setting format for abs_mag and "
            "abs_mag_err columns"
        )
        self.catalog.table['abs_mag'].info.format = '.3f'
        self.catalog.table['abs_mag_err'].info.format = '.3f'

        self._logger.info(
            "END - Successfully computed absolute magnitudes"
        )

    def _determine_optimal_batch_size(self, wavelength_points, num_samples):
        """
        Determine the optimal batch size for Monte Carlo simulations based on CPU cores
        and the computational complexity of the wavelength grid.
        
        Parameters
        ----------
        wavelength_points : int
            Number of wavelength points in the calculation grid
        num_samples : int
            Total number of Monte Carlo samples
            
        Returns
        -------
        int
            Optimal batch size for processing Monte Carlo samples
        """
        self._logger.debug(
            f"Determining optimal batch size for {num_samples} samples with "
            f"{wavelength_points} wavelength points"
        )
        
        # Get CPU count
        try:
            import multiprocessing
            num_cores = multiprocessing.cpu_count()
            self._logger.debug(f"Detected {num_cores} CPU cores")
        except:
            num_cores = 4  # Conservative fallback
            self._logger.debug(f"Could not detect CPU count, using {num_cores} as fallback")
        
        # Scale samples per core based on wavelength grid size
        # (more wavelength points = more computation per sample)
        if wavelength_points < 500:
            samples_per_core = 32  # Lightweight calculations
        elif wavelength_points < 2000:
            samples_per_core = 16  # Medium calculations
        else:
            samples_per_core = 8   # Heavy calculations
            
        self._logger.debug(
            f"Using {samples_per_core} samples per core based on wavelength grid size"
        )
        
        # Compute batch size
        batch_size = num_cores * samples_per_core
        
        # Ensure batch size is reasonable relative to total samples
        # At minimum, we want one batch per core, and at maximum, 
        # we want at least 10 batches for progress reporting
        batch_size = min(batch_size, max(num_cores, num_samples // 10))
        
        # Final bounds check
        batch_size = max(num_cores, min(batch_size, num_samples))
        
        self._logger.debug(f"Calculated optimal batch size: {batch_size}")
        return int(batch_size)

    def run(
        self,
        # High-level flags for each pipeline stage
        clean_data=True,
        combine_fluxes=True,
        filter_outliers=True,
        estimate_radius=True,
        estimate_extinction=True,
        compute_bolometric=True,
        # Configuration dictionaries for each stage
        data_cleaning_config=None,
        flux_combination_config=None,
        outlier_filtering_config=None,
        radius_estimation_config=None,
        extinction_estimation_config=None,
        bolometric_correction_config=None,
        # General settings
        silent=False,
        verbose=True,
        plot_results=True,
        continue_on_error=True,
        save=True,
        save_path=None,
        save_compressed=True,
        return_results=False
    ):
        """
        Run a complete analysis pipeline on the SED data.
        
        This method executes a sequence of data processing and analysis steps based on the
        provided configuration, handling errors gracefully and tracking the results of
        each step. The pipeline includes data cleaning, flux combination, outlier filtering,
        radius estimation, extinction estimation, and bolometric correction calculation.
        
        Parameters
        ----------
        clean_data : bool, optional
            Whether to perform data cleaning (default: True)
        combine_fluxes : bool, optional
            Whether to combine flux measurements from the same filter (default: True)
        filter_outliers : bool, optional
            Whether to filter outliers from the data (default: True)
        estimate_radius : bool, optional
            Whether to estimate the stellar radius (default: True)
        estimate_extinction : bool, optional
            Whether to estimate interstellar extinction E(B-V) (default: True)
        compute_bolometric : bool, optional
            Whether to compute bolometric correction (default: True)
        
        data_cleaning_config : dict, optional
            Configuration for data cleaning stage:
            - delete_missing_data_columns : str or list, columns to check (default: 'filter')
        
        flux_combination_config : dict, optional
            Configuration for flux combination stage:
            - method : str, method to use ('mean', 'median', etc.) (default: 'median')
        
        outlier_filtering_config : dict, optional
            Configuration for outlier filtering:
            - sigma_threshold : float, threshold for outlier detection (default: 3.0)
        
        radius_estimation_config : dict, optional
            Configuration for radius estimation:
            - method : str, method to use ('grid' or 'mc') (default: 'mc')
            - accept : bool, whether to update SED with result (default: True)
            - n_samples : int, number of MC samples if using 'mc' (default: 1000)
            - corner_plot : bool, whether to create corner plot for 'mc' (default: True)
            - grid_min : float, minimum radius for grid search (default: 0.1)
            - grid_max : float, maximum radius for grid search (default: 50.0)
            - grid_points : int, number of points in grid search (default: 10000)
            - refine_window : float, refinement window fraction (default: 0.3)
            - refine_steps : int, number of steps in refinement (default: 10000)
            - plot_chi2 : bool, whether to plot chi2 for grid search (default: False)
        
        extinction_estimation_config : dict, optional
            Configuration for extinction estimation:
            - method : str, method to use ('minimize', 'grid_search', 'mc') (default: 'mc')
            - accept : bool, whether to update SED with result (default: True)
            - n_samples : int, number of MC samples if using 'mc' (default: 1000)
            - corner_plot : bool, whether to create corner plot for 'mc' (default: True)
            - ebv_range : tuple, range of E(B-V) values (default: (0.0, 1.0))
            - ebv_initial : float, initial guess for E(B-V) (default: 0.1)
            - num_points : int, number of points in grid search (default: 10000)
            - optimization_method : str, optimization method (default: "L-BFGS-B")
        
        bolometric_correction_config : dict, optional
            Configuration for bolometric correction:
            - accept_radius : bool, whether to update radius (default: True)
        
        silent : bool, optional
            Whether to suppress verbose output (default: False)
        
        verbose : bool, optional
            Whether to print detailed information during processing (default: True)
        
        plot_results : bool, optional
            Whether to plot results (default: True)
        
        continue_on_error : bool, optional
            Whether to continue pipeline if non-critical errors occur (default: True)
        
        save : bool, optional
            Whether to save the SED project to disk after completion (default: True)
        
        save_path : str, optional
            Path where to save the SED project. If None, a default path based on the 
            object name will be used (default: None)
        
        save_compressed : bool, optional
            Whether to save the SED project in a compressed format (default: True)
            compression format is zip
        
        return_results : bool, optional
            Whether to return the results of the pipeline (default: False)
        
        Returns
        -------
        dict or None
            A dictionary containing the results and status of each pipeline stage:
            - 'success' : bool, becomes False as soon as any stage fails, stays False
              even if subsequent stages succeed
            - 'all_successful' : bool, True only if all non-skipped stages completed 
              successfully (calculated at the end)
            - 'stages' : dict, status and results for each stage
            - 'errors' : list, error messages if any occurred
            - 'timing' : dict, timing information for each stage
            - 'summary' : str, summary of the pipeline execution
            - 'save_path' : str, path where the SED project was saved (if applicable)
        
        Examples
        --------
        >>> from sedlib import SED
        >>> sed = SED(name='Vega')
        >>> 
        >>> # Run pipeline with default settings
        >>> results = sed.run()
        >>> 
        >>> # Run only specific stages
        >>> results = sed.run(
        ...     clean_data=True,
        ...     combine_fluxes=True,
        ...     filter_outliers=True,
        ...     estimate_radius=False,
        ...     estimate_extinction=False,
        ...     compute_bolometric=False
        ... )
        >>> 
        >>> # Custom configuration for radius estimation
        >>> results = sed.run(
        ...     radius_estimation_config={
        ...         'method': 'grid',
        ...         'grid_min': 1.0,
        ...         'grid_max': 10.0
        ...     }
        ... )
        """
        self._logger.info("BEGIN - Starting SED analysis pipeline")
        
        # Convert empty string save_path to None for consistency
        if save_path == "":
            save_path = None

        # Initialize result tracking
        self._result = {
            'success': True,
            'initial_parameters': {
                'name': self.name,
                'ra': self.ra,
                'dec': self.dec,
                'parallax': self.parallax,
                'parallax_error': self.parallax_error,
                'distance': self.distance,
                'distance_error': self.distance_error,
                'teff': self._initial_teff,
                'teff_error': self._initial_teff_error,
                'radius': self._initial_radius,
                'radius_error': self._initial_radius_error,
            },
            'stages': {},
            'errors': [],
            'timing': {},
            'summary': "",
            'save_path': None
        }
        
        # Default configurations
        default_data_cleaning_config = {
            'delete_missing_data_columns': 'filter'
        }
        
        default_flux_combination_config = {
            'method': 'median'
        }
        
        default_outlier_filtering_config = {
            'sigma_threshold': 3.0
        }
        
        default_radius_estimation_config = {
            'method': 'mc',
            'accept': True,
            'n_samples': 1000,
            'corner_plot': plot_results,
            'grid_min': 0.1,
            'grid_max': 50.0,
            'grid_points': 10000,
            'refine_window': 0.3,
            'refine_steps': 10000,
            'plot_chi2': plot_results,
            'show_progress': True
        }
        
        default_extinction_estimation_config = {
            'method': 'mc',
            'model': 'blackbody',
            'ext_model': G23(Rv=3.1),
            'accept': True,
            'n_samples': 1000,
            'corner_plot': plot_results,
            'ebv_range': (0.0, 10.0),
            'ebv_initial': 0.1,
            'num_points': 10000,
            'optimization_method': 'L-BFGS-B',
            'show_progress': True
        }
        
        default_bolometric_correction_config = {
            'accept_radius': True
        }
        
        # Merge user configs with defaults
        data_cleaning_config = {
            **default_data_cleaning_config, 
            **(data_cleaning_config or {})
        }
        flux_combination_config = {
            **default_flux_combination_config, 
            **(flux_combination_config or {})
        }
        outlier_filtering_config = {
            **default_outlier_filtering_config, 
            **(outlier_filtering_config or {})
        }
        radius_estimation_config = {
            **default_radius_estimation_config, 
            **(radius_estimation_config or {})
        }
        extinction_estimation_config = {
            **default_extinction_estimation_config, 
            **(extinction_estimation_config or {})
        }
        bolometric_correction_config = {
            **default_bolometric_correction_config, 
            **(bolometric_correction_config or {})
        }

        # Suppress verbose output if silent flag is True
        if silent:
            verbose = False
            radius_estimation_config['show_progress'] = False
            radius_estimation_config['corner_plot'] = False
            radius_estimation_config['plot_chi2'] = False

            extinction_estimation_config['show_progress'] = False
            extinction_estimation_config['corner_plot'] = False

        # Validate catalog exists
        if self.catalog is None:
            error_msg = "No catalog data available. Initialize SED with data first."
            self._logger.error(error_msg)
            self._result['success'] = False
            self._result['errors'].append(error_msg)
            self._result['summary'] = "Pipeline failed: No catalog data available"
            return self._result
        
        # Create a list of enabled stages to track stage numbers
        enabled_stages = []
        if clean_data:
            enabled_stages.append("data_cleaning")
        if combine_fluxes:
            enabled_stages.append("flux_combination")
        if filter_outliers:
            enabled_stages.append("outlier_filtering")
        if estimate_radius:
            enabled_stages.append("radius_estimation")
        if estimate_extinction:
            enabled_stages.append("extinction_estimation")
        if compute_bolometric:
            enabled_stages.append("bolometric_correction")
        if save:
            enabled_stages.append("save_project")
        
        total_enabled_stages = len(enabled_stages)
        
        pipeline_stage_emojis = {
            'Data Cleaning': '🧹',
            'Flux Combination': '📊',
            'Outlier Filtering': '🔍',
            'Radius Estimation': '⭕',
            'Extinction Estimation': '🌫️',
            'Bolometric Correction': '✨',
            'Save Project': '💾'
        }

        if verbose:
            print("\n" + "="*80)
            print(f"SED ANALYSIS PIPELINE FOR: "
                  f"{self.name if self.name else 'Unknown object'}")
            print("="*80)
            print("🚀 Pipeline stages to be executed:")
            for i, stage in enumerate(enabled_stages, 1):
                stage_name = stage.replace('_', ' ').title()
                emoji = pipeline_stage_emojis.get(stage_name, '')
                print(f"  {i}. {emoji} {stage_name}")
            print("-"*80)

            print("Initial parameters:")
            if self.teff is not None:
                print(f"🔥 Temperature: {self.teff}")
            if self.teff_error is not None:
                print(f"±️ Temperature error: {self.teff_error}")
            if self.radius is not None:
                print(f"⭕ Radius: {self.radius}")
            if self.radius_error is not None:
                print(f"±️ Radius error: {self.radius_error}")
            if self.distance is not None:
                print(f"📏 Distance: {self.distance}")
            if self.distance_error is not None:
                print(f"±️ Distance error: {self.distance_error}")
            print(f"📊 Number of photometric measurements: {len(self.catalog.table)}")
            print("-"*80 + "\n")
        
        # Helper function to run a pipeline stage
        def run_stage(name, enabled, stage_func, **kwargs):
            if not enabled:
                self._logger.info(f"Skipping {name} stage (disabled by user)")
                self._result['stages'][name] = {
                    'status': 'skipped',
                    'message': 'Stage disabled by user'
                }
                if verbose:
                    print(f"\n⏩ SKIPPING: {name.replace('_', ' ').title()} "
                          f"(disabled by user)")
                return False
            
            # Get stage number
            stage_num = enabled_stages.index(name) + 1
            
            stage_start = time()
            try:
                self._logger.info(f"Starting {name} stage")
                if verbose:
                    emoji = pipeline_stage_emojis[name.replace('_', ' ').title()]
                    print(f"\n🔄 STAGE {stage_num}/{total_enabled_stages}: "
                          f"{emoji} {name.replace('_', ' ').title()}")
                    print(f"   Starting {name.replace('_', ' ')}...")
                
                result = stage_func(**kwargs)
                
                stage_end = time()
                elapsed = stage_end - stage_start
                self._result['timing'][name] = elapsed
                
                # For radius_estimation and extinction_estimation, check the success field in result
                if name in ["radius_estimation", "extinction_estimation"] and isinstance(result, dict) and "success" in result:
                    if result["success"]:
                        self._result['stages'][name] = {
                            'status': 'success',
                            'result': result
                        }
                        self._logger.info(
                            f"Completed {name} stage successfully in {elapsed:.2f}s"
                        )
                        if verbose:
                            print(f"✅ COMPLETED: Stage {stage_num}/{total_enabled_stages} - "
                                  f"{name.replace('_', ' ').title()} in {elapsed:.2f}s")
                        return True
                    else:
                        error_msg = f"{name} completed but produced invalid results"
                        self._logger.warning(error_msg)
                        self._result['stages'][name] = {
                            'status': 'failed',
                            'error': error_msg,
                            'result': result
                        }
                        self._result['errors'].append(error_msg)
                        self._result['success'] = False
                        
                        if verbose:
                            print(f"⚠️ WARNING: Stage {stage_num}/{total_enabled_stages} - "
                                  f"{name.replace('_', ' ').title()} completed but produced invalid results in {elapsed:.2f}s")
                        
                        if not continue_on_error:
                            self._logger.warning("Pipeline aborted due to invalid results")
                            if verbose:
                                print("\n⛔ Pipeline aborted due to invalid results")
                            return False
                        return False
                else:
                    # For other stages, or if success field not available, assume success
                    self._result['stages'][name] = {
                        'status': 'success',
                        'result': result
                    }
                    self._logger.info(
                        f"Completed {name} stage successfully in {elapsed:.2f}s"
                    )
                    if verbose:
                        print(f"✅ COMPLETED: Stage {stage_num}/{total_enabled_stages} - "
                              f"{name.replace('_', ' ').title()} in {elapsed:.2f}s")
                    return True
            except Exception as e:
                stage_end = time()
                elapsed = stage_end - stage_start
                self._result['timing'][name] = elapsed
                error_msg = f"Error in {name} stage: {str(e)}"
                self._logger.error(error_msg)
                self._logger.error(traceback.format_exc())
                self._result['stages'][name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                self._result['errors'].append(error_msg)
                self._result['success'] = False
                
                if verbose:
                    print(f"❌ ERROR: Stage {stage_num}/{total_enabled_stages} - "
                          f"{name.replace('_', ' ').title()} failed after {elapsed:.2f}s")
                    print(f"   {str(e)}")
                
                if not continue_on_error:
                    self._logger.warning("Pipeline aborted due to error")
                    if verbose:
                        print("\n⛔ Pipeline aborted due to error")
                    return False
                return False
        
        # Stage 1: Data Cleaning
        def clean_data_stage():
            cols = data_cleaning_config['delete_missing_data_columns']
            number_of_rows_deleted = self.catalog.delete_missing_data_rows(cols)
            
            if verbose:
                print(f"   Removed {number_of_rows_deleted} rows with missing data "
                      f"in '{cols}' column(s)")
                print(f"   Remaining data points: {len(self.catalog.table)}")
            return {'removed_rows': number_of_rows_deleted}
        
        clean_success = run_stage("data_cleaning", clean_data, clean_data_stage)
        
        # Stage 2: Flux Combination
        def combine_fluxes_stage():
            method = flux_combination_config['method']
            original_len = len(self.catalog.table)
            self.catalog.combine_fluxes(method=method, overwrite=True)
            new_len = len(self.catalog.table)
            combined_count = original_len - new_len
            
            if verbose:
                print(f"   Combined flux measurements using '{method}' method")
                print(f"   Combined {combined_count} measurements")
                print(f"   Unique filters after combination: {new_len}")
            return {'combined_count': combined_count, 'method': method}
        
        combine_success = run_stage(
            "flux_combination", combine_fluxes, combine_fluxes_stage
        )
        
        # Stage 3: Outlier Filtering
        def filter_outliers_stage():
            sigma = outlier_filtering_config['sigma_threshold']
            self.catalog.filter_outliers(
                sigma_threshold=sigma,
                over_write=True,
                verbose=False  # We'll handle our own verbose output
            )
            outlier_count = (len(self.catalog.rejected_data) 
                             if self.catalog.rejected_data is not None else 0)
            if verbose:
                print(f"   Identified {outlier_count} outliers with sigma > {sigma}")
                print(f"   Remaining valid measurements: {len(self.catalog.table)}")
                if outlier_count > 0:
                    print(f"   Outliers are marked but not removed from the dataset")
            return {'outlier_count': outlier_count, 'sigma_threshold': sigma}
        
        outlier_success = run_stage(
            "outlier_filtering", filter_outliers, filter_outliers_stage
        )
        
        # Stage 4: Radius Estimation
        def check_radius_prerequisites():
            missing = []
            if self.teff is None:
                missing.append("effective temperature (teff)")
            if self.teff_error is None:
                missing.append("temperature error (teff_error)")
            if self.distance is None:
                missing.append("distance")
            if self.distance_error is None:
                missing.append("distance error (distance_error)")
            
            if missing:
                raise ValueError(
                    f"Cannot estimate radius: missing required parameters: "
                    f"{', '.join(missing)}"
                )
        
        def estimate_radius_stage():
            check_radius_prerequisites()
            
            radius_config = {
                'method': radius_estimation_config['method'],
                'accept': radius_estimation_config['accept'],
                'verbose': False,  # We'll handle our own verbose output
                'n_jobs': -1,
                'show_progress': radius_estimation_config['show_progress']
            }
            
            # Add method-specific parameters
            if radius_config['method'] == 'mc':
                radius_config.update({
                    'n_samples': radius_estimation_config['n_samples'],
                    'corner_plot': radius_estimation_config['corner_plot'],
                    'accept_method': "median"
                })
            elif radius_config['method'] == 'grid':
                radius_config.update({
                    'grid_min': radius_estimation_config['grid_min'],
                    'grid_max': radius_estimation_config['grid_max'],
                    'grid_points': radius_estimation_config['grid_points'],
                    'refine_window': radius_estimation_config['refine_window'],
                    'refine_steps': radius_estimation_config['refine_steps'],
                    'plot_chi2': radius_estimation_config['plot_chi2']
                })
            
            if verbose:
                print(f"   Using {radius_config['method']} method for radius estimation")
                if radius_config['method'] == 'mc':
                    print(f"   Running with {radius_config['n_samples']} "
                          f"Monte Carlo samples")
                elif radius_config['method'] == 'grid':
                    print(f"   Grid search range: {radius_config['grid_min']} to "
                          f"{radius_config['grid_max']} Rsun")
                    print(f"   Grid points: {radius_config['grid_points']}")
            
            result = self.estimate_radius(**radius_config)
            
            if radius_config['method'] == 'mc':
                radius_val = result['radius_median']
                radius_err = result['radius_std']
            else:
                radius_val = result['radius']
                radius_err = result['radius_error']
                
            if verbose:
                print(f"   --------- RADIUS ESTIMATION RESULTS ---------")
                print(f"   Radius: {radius_val}")
                print(f"   Uncertainty: {radius_err}")
                print(f"   Method: {radius_config['method']}")
                if radius_config['method'] == 'mc':
                    valid_samples = result.get('num_valid_samples', 
                                              result.get('n_samples', 'N/A'))
                    print(f"   Valid samples: {valid_samples}")
                print(f"   --------------------------------------------")
                
            return result
        
        radius_success = run_stage(
            "radius_estimation", estimate_radius, estimate_radius_stage
        )
        
        # Stage 5: Extinction Estimation
        def check_extinction_prerequisites():
            missing = []
            if self.teff is None:
                missing.append("effective temperature (teff)")
            if self.radius is None:
                missing.append("radius")
            if self.distance is None:
                missing.append("distance")
            
            if missing:
                raise ValueError(
                    f"Cannot estimate extinction: missing required parameters: "
                    f"{', '.join(missing)}"
                )
        
        def estimate_extinction_stage():
            check_extinction_prerequisites()
            
            ebv_config = {
                'method': extinction_estimation_config['method'],
                'model': extinction_estimation_config['model'],
                'ext_model': extinction_estimation_config['ext_model'],
                'accept': extinction_estimation_config['accept'],
                'verbose': False,  # We'll handle our own verbose output
                'n_jobs': -1,
                'show_progress': extinction_estimation_config['show_progress']
            }
            
            # Add method-specific parameters
            if ebv_config['method'] == 'mc':
                ebv_config.update({
                    'n_samples': extinction_estimation_config['n_samples'],
                    'plot_corner': extinction_estimation_config['corner_plot']
                })
            else:  # 'grid_search' or 'minimize'
                ebv_config.update({
                    'ebv_range': extinction_estimation_config['ebv_range'],
                    'ebv_initial': extinction_estimation_config['ebv_initial'],
                    'num_points': extinction_estimation_config['num_points'],
                    'optimization_method': extinction_estimation_config['optimization_method']
                })
            
            if verbose:
                print(f"   Using {ebv_config['method']} method for extinction estimation")
                print(f"   Extinction model: {ebv_config['ext_model'].__class__.__name__}")
                
                if ebv_config['method'] == 'mc':
                    print(f"   Running with {ebv_config['n_samples']} Monte Carlo samples")
                else:
                    print(f"   E(B-V) search range: {ebv_config['ebv_range']}")
            
            result = self.estimate_ebv(**ebv_config)
            
            if ebv_config['method'] == 'mc':
                ebv_val = result['ebv_mean']
                ebv_err = result['ebv_std']
            else:
                ebv_val = result['ebv']
                ebv_err = result['ebv_error']
                
            if verbose:
                print(f"   -------- EXTINCTION ESTIMATION RESULTS --------")
                print(f"   E(B-V): {ebv_val:.4f}")
                print(f"   Uncertainty: {ebv_err:.4f}")
                print(f"   Method: {ebv_config['method']}")
                if ebv_config['method'] == 'mc':
                    valid_samples = result.get('num_valid_samples', 
                                              result.get('n_samples', 'N/A'))
                    print(f"   Valid samples: {valid_samples}")
                elif 'rms_error' in result:
                    print(f"   RMS Error: {result['rms_error']:.4e}")
                print(f"   -----------------------------------------------")
                
            return result
        
        extinction_success = run_stage(
            "extinction_estimation",
            estimate_extinction,
            estimate_extinction_stage
        )
        
        # Stage 6: Bolometric Correction
        def check_bolometric_prerequisites():
            missing = []
            if self.teff is None:
                missing.append("effective temperature (teff)")
            if self.radius is None:
                missing.append("radius")
            if self.distance is None:
                missing.append("distance")
            if self.ebv is None:
                missing.append("extinction (ebv)")
            if self.ext_model is None:
                missing.append("extinction model (ext_model)")
            
            if missing:
                raise ValueError(
                    f"Cannot compute bolometric correction: missing required parameters: "
                    f"{', '.join(missing)}"
                )
        
        def compute_bolometric_stage():
            check_bolometric_prerequisites()
            
            if verbose:
                print(f"   Computing extinction (A_λ) for each filter")
            
            # First compute extinction for each filter
            self.compute_A_lambda()
            
            if verbose:
                print(f"   Computing absolute magnitudes")
            
            # Then compute absolute magnitudes
            self.compute_absolute_magnitudes()
            
            if verbose:
                print(f"   Running bolometric correction")
                print(f"   Accept radius correction: "
                      f"{bolometric_correction_config['accept_radius']}")
            
            # Run bolometric correction
            self._bc = BolometricCorrection(
                sed=self,
                accept_radius=bolometric_correction_config['accept_radius']
            )
            bc_result = self._bc.run(verbose=False)  # We'll handle our own verbose output
            
            # Create a new dictionary to hold the success status and original result
            # final_result = {'original_result': bc_result}
            # final_result = {'result': self._bc._result}
            final_result = self._bc._result
            
            # Add success status based on radius value and error
            if hasattr(self._bc, '_radius') and self._bc._radius is not None:
                # Check if radius and error are valid numbers
                basic_validity = (
                    self._bc._radius.value != 0.0 and 
                    not np.isnan(self._bc._radius.value) and
                    self._bc._radius_error is not None and
                    not np.isnan(self._bc._radius_error.value)
                )
                
                # Check if the relative error is too large
                if basic_validity:
                    relative_error = abs(self._bc._radius_error.value / self._bc._radius.value)
                    error_acceptable = relative_error <= 0.5  # 50% threshold
                    final_result['success'] = basic_validity and error_acceptable
                    
                    if not error_acceptable:
                        error_msg = f"Bolometric radius error too large: {relative_error:.2%} of radius value"
                        self._logger.warning(error_msg)
                        if verbose:
                            print(f"   ⚠️ {error_msg}")
                else:
                    final_result['success'] = False
            else:
                final_result['success'] = False
            
            if verbose:
                original_radius = self.radius
                print(f"   -------- BOLOMETRIC CORRECTION RESULTS --------")
                if hasattr(self._bc, '_radius'):
                    print(f"   Bolometric radius: {self._bc._radius}")
                    print(f"   Bolometric radius error: {self._bc._radius_error}")
                
                if hasattr(self._bc, 'radius_ratio'):
                    print(f"   Radius correction factor: {self._bc.radius_ratio:.4f}")
                    print(f"   Original radius: {original_radius}")
                    print(f"   Corrected radius: {self.radius}")
                
                if hasattr(self._bc, '_fbol'):
                    print(f"   Bolometric flux: {self._bc._fbol}")
                    print(f"   Bolometric flux error: {self._bc._fbol_error}")
                
                if hasattr(self._bc, '_mbol'):
                    print(f"   Apparent bolometric magnitude: {self._bc._mbol:.4f}")
                    print(f"   Absolute bolometric magnitude: {self._bc._Mbol:.4f}")
                print(f"   -----------------------------------------------")
            
            return final_result
        
        bolometric_success = run_stage(
            "bolometric_correction",
            compute_bolometric,
            compute_bolometric_stage
        )
        
        # Check if bolometric correction produced valid results
        if bolometric_success and 'stages' in self._result and 'bolometric_correction' in self._result['stages']:
            bolometric_result = self._result['stages']['bolometric_correction'].get('result', {})
            if isinstance(bolometric_result, dict) and not bolometric_result.get('success', True):
                # Success is False but no error occurred in the stage execution
                error_msg = "Bolometric correction completed but produced invalid radius values"
                self._logger.warning(error_msg)
                self._result['stages']['bolometric_correction']['status'] = 'failed'
                self._result['stages']['bolometric_correction']['error'] = error_msg
                self._result['errors'].append(error_msg)
                self._result['success'] = False
                
                if verbose:
                    print("⚠️ WARNING: Bolometric correction completed but produced invalid radius values")
        
        # Stage 7: Save Project
        def save_project_stage():
            # Determine the save path if not provided
            actual_save_path = save_path
            
            if actual_save_path is None:
                # Add timestamp to the beginning of the filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                # Convert any spaces or special characters to underscores
                name = self._user_provided_name.replace(' ', '_')
                name = name.replace('/', '_').replace('\\', '_')
                actual_save_path = f"{timestamp}-{name}.sed"
            
            if verbose:
                compressed_suffix = '.zip' if save_compressed else ''
                print(f"   Saving SED project to '{actual_save_path}{compressed_suffix}'")
                
            self._logger.info(
                f"Saving SED project to {actual_save_path}"
                f"{'.zip' if save_compressed else ''}"
            )
            
            # Use the SED.save method
            self.save(actual_save_path, compression=save_compressed)

            if save_compressed:
                actual_save_path = f"{actual_save_path}.zip"
            
            return {'saved_to': actual_save_path}
        
        # Run the save stage if requested
        if save:
            save_success = run_stage("save_project", True, save_project_stage)
            if save_success and 'result' in self._result['stages']['save_project']:
                save_result = self._result['stages']['save_project']['result']
                if 'saved_to' in save_result:
                    self._result['save_path'] = save_result['saved_to']
        
        # Generate summary
        completed_stages = sum(
            1 for stage in self._result['stages'].values() 
            if stage['status'] == 'success'
        )
        total_stages = len(enabled_stages)
        
        failed_stages = sum(
            1 for stage in self._result['stages'].values() 
            if stage['status'] == 'failed'
        )
        skipped_stages = sum(
            1 for stage in self._result['stages'].values() 
            if stage['status'] == 'skipped'
        )
        
        # Add a field indicating if all attempted stages were successful
        self._result['all_successful'] = (failed_stages == 0)
        
        total_time = sum(self._result['timing'].values())
        self._result['timing']['total_time'] = total_time
        
        self._result['summary'] = (
            f"Pipeline completed with {completed_stages}/{total_stages} stages successful, "
            f"{failed_stages} failed, {skipped_stages} skipped. "
            f"Total time: {total_time:.2f} seconds."
        )
        
        self._logger.info(
            f"END - SED analysis pipeline completed. "
            f"{self._result['summary']}"
        )
        
        if verbose:
            print("\n" + "="*80)
            print(f"PIPELINE SUMMARY")
            print("="*80)
            print(f"Stages completed: {completed_stages}/{total_stages}")
            if failed_stages > 0:
                print(f"Stages failed: {failed_stages}")
            if skipped_stages > 0:
                print(f"Stages skipped: {skipped_stages}")
            print(f"Total execution time: {total_time:.2f} seconds")
            
            # Print per-stage status
            print("\nStage Status:")
            for stage_name in enabled_stages:
                stage_info = self._result['stages'].get(stage_name, {})
                status = stage_info.get('status', 'unknown')
                emoji = "✅" if status == "success" else "⏩" if status == "skipped" else "❌"
                stage_display = stage_name.replace('_', ' ').title()
                print(f"  {emoji} {stage_display}: {status.upper()}")
            
            # Print key results if available
            print("\nFinal Results:")
            if self.radius is not None:
                print(f"  Radius: {self.radius} ± {self.radius_error}")
            if self.ebv is not None:
                print(f"  E(B-V): {self.ebv:.4f} ± {self.ebv_error:.4f}")
            if hasattr(self, '_fbol') and self._fbol is not None:
                print(f"  Bolometric flux: {self._fbol}")
            if hasattr(self, '_Lbol') and self._Lbol is not None:
                print(f"  Bolometric luminosity: {self._Lbol}")
            
            if self._result['save_path'] is not None:
                print(f"\nSED project saved to: {self._result['save_path']}")
            
            print("="*80 + "\n")

        if return_results:
            return self._result
    
    def export_result(self):
        """
        Export comprehensive analysis results as a structured dictionary.
        
        This method aggregates all stellar parameters, photometric measurements,
        extinction properties, and analysis results into a single dictionary
        suitable for data export, archiving, or further analysis.
        
        Returns
        -------
        dict
            A comprehensive dictionary containing:
            
            **Source Identification:**
            - source_id : None (placeholder for source identifier)
            - name : str, source name
            - ra : float, right ascension (degrees)
            - dec : float, declination (degrees)
            
            **Stellar Parameters:**
            - parallax : float, parallax (mas)
            - parallax_error : float, parallax uncertainty (mas)
            - distance : float, distance (pc)
            - distance_error : float, distance uncertainty (pc)
            - teff : float, effective temperature (K)
            - teff_error : float, effective temperature uncertainty (K)
            - teff_gaia : float, Gaia effective temperature (K)
            - teff_gaia_error : float, Gaia effective temperature uncertainty (K)
            - logg : float, surface gravity (log g)
            - logg_error : float, surface gravity uncertainty
            - init_radius : float, initial radius estimate (R_sun)
            - init_radius_error : float, initial radius uncertainty (R_sun)
            
            **Extinction Properties:**
            - ebv_mean : float, mean E(B-V) reddening
            - ebv_median : float, median E(B-V) reddening
            - ebv_std : float, standard deviation of E(B-V)
            
            **Photometry (for bands B, V, G, GRP, GBP, TESS):**
            - mag_[band] : float, apparent magnitude
            - mag_error_[band] : float, magnitude uncertainty
            - A_lambda_[band] : float, extinction in magnitudes
            - A_lambda_error_[band] : float, extinction uncertainty
            - abs_mags_[band] : float, absolute magnitude
            - abs_mags_error_[band] : float, absolute magnitude uncertainty
            
            **Bolometric Properties:**
            - bc_[band] : float, bolometric correction for each band
            - bc_[band]_error : float, bolometric correction uncertainty
            - bol_mags_[band] : float, bolometric magnitude for each band
            - bol_mags_error_[band] : float, bolometric magnitude uncertainty
            - abs_bol_mag : float, absolute bolometric magnitude
            - abs_bol_mag_err : float, absolute bolometric magnitude uncertainty
            - radius : float, final stellar radius (R_sun)
            - radius_error : float, final radius uncertainty (R_sun)
            
            **Metadata:**
            - success : bool, overall analysis success status
            - result_file_path : str or None, path to saved results file
            
        Notes
        -----
        - Preferred filters are selected based on a priority system
        - Values may be NaN if measurements are unavailable
        - All quantities are returned as scalar values (units stripped)
        - This method requires that the SED analysis pipeline has been run
        """
        out = {
            'source_id': None,
            'name': self._name,
            'ra': float(self._ra.value),
            'dec': float(self._dec.value),
            'parallax': float(self._parallax.value),
            'parallax_error': float(self._parallax_error.value),
            'distance': float(self._distance.value),
            'distance_error': float(self._distance_error.value),
            'teff': float(self._teff.value),
            'teff_error': float(self._teff_error.value),
            'teff_gaia': (float(self._teff_gaia.value)
                          if self._teff_gaia is not None else None),
            'teff_gaia_error': (float(self._teff_gaia_error.value)
                                if self._teff_gaia_error is not None else None),
            'logg': float(self._logg) if self._logg is not None else None,
            'logg_error': (float(self._logg_error)
                           if self._logg_error is not None else None),
            'init_radius': float(self._initial_radius.value),
            'init_radius_error': float(self._initial_radius.value),
            'ebv_mean': float(self._result['stages']['extinction_estimation']['result'][
                'ebv_mean'
            ]),
            'ebv_median': float(self._result['stages']['extinction_estimation'][
                'result'
            ]['ebv_median']),
            'ebv_std': float(self._result['stages']['extinction_estimation']['result'][
                'ebv_std'
            ]),
        }

        bands = ['B', 'V', 'G', 'GRP', 'GBP', 'TESS']

        # magnitudes
        result = select_preferred_filters(self, 'mag', 'mag_err')
        for b in bands:
            val, err = result.get(b, (np.nan, np.nan))
            out[f'mag_{b}'] = float(val)
            out[f'mag_error_{b}'] = float(err)

        # A_lambda
        result = select_preferred_filters(self, 'A_lambda', 'A_lambda_err')
        for b in bands:
            val, err = result.get(b, (np.nan, np.nan))
            out[f'A_lambda_{b}'] = float(val)
            out[f'A_lambda_error_{b}'] = float(err)

        # abs_mag
        result = select_preferred_filters(self, 'abs_mag', 'abs_mag_err')
        for b in bands:
            val, err = result.get(b, (np.nan, np.nan))
            out[f'abs_mags_{b}'] = float(val)
            out[f'abs_mags_error_{b}'] = float(err)

        # bolometric corrections
        for b, (val, err) in self._bc._bolometric_corrections.items():
            out[f'bc_{b}'] = float(val)
            out[f'bc_{b}_error'] = float(err)

        # bolometric mags
        for b, (val, err) in self._bc._bolometric_mags.items():
            out[f'bol_mags_{b}'] = float(val)
            out[f'bol_mags_error_{b}'] = float(err)

        out['abs_bol_mag'] = float(self._bc._abs_bol_mag)
        out['abs_bol_mag_err'] = float(self._bc._abs_bol_mag_err)
        out['radius'] = float(self._bc._radius.value)
        out['radius_error'] = float(self._bc._radius_error.value)
        out['success'] = self._result['success']
        out['result_file_path'] = self._result['save_path']

        return out
