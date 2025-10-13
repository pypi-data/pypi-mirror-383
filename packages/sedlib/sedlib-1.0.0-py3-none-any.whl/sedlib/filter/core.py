#!/usr/bin/env python

"""Core class for the filter module."""

__all__ = ["Filter"]

import os
import logging
import warnings
from io import BytesIO
from fnmatch import fnmatch
import requests
from pathlib import Path
from importlib import resources

from bs4 import BeautifulSoup
from typing import Optional, Union, List, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from astropy import units as u
from astropy.io import votable
from astropy.modeling.tabular import Tabular1D
from astropy.utils.exceptions import AstropyWarning
from astropy.utils.data import download_file

from .utils import SVO_FILTER_URL, InMemoryHandler


# Set up logging
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
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

# Set up default logger with both file and memory handlers
logger, in_memory_handler = setup_logger(__name__)

warnings.simplefilter('ignore', category=AstropyWarning)


class Filter:
    """
    A class for managing astronomical filter transmission curves.
    
    This class provides access to filter transmission curves from the SVO Filter
    Profile Service, which contains thousands of astronomical filters used by
    various surveys and instruments. Filters can be loaded from the SVO service
    or created from custom data.
    
    Parameters
    ----------
    name : str, optional
        Filter identifier in SVO format (e.g., 'Generic/Johnson.V').
        The filter name must match the naming convention used by the SVO service.
    method : str, default 'linear'
        Interpolation method for filter transmission curves.
        Available methods: 'linear', 'nearest'.
    bounds_error : bool, default False
        If True, raise ValueError when interpolated values are requested outside
        the domain of the input data. If False, use fill_value.
    fill_value : float or None, default 0.0
        Value to use for points outside the interpolation domain.
        If None, values outside the domain are extrapolated.
    cache : bool, default True
        If True, cache filter data for faster subsequent access.
    timeout : int, default 10
        Timeout in seconds for HTTP requests to SVO service.
    log_to_file : bool, default False
        Whether to enable file logging.
    log_to_memory : bool, default True
        Whether to enable in-memory logging.
    log_level : int, default logging.DEBUG
        Logging level to use.
    log_file : str or Path, optional
        Path to log file. Default is 'sed.log'.
        
    Attributes
    ----------
    name : str
        Filter identifier.
    wavelength : astropy.units.Quantity
        Wavelength array for the filter transmission curve.
    transmission : numpy.ndarray
        Transmission values corresponding to wavelengths.
    data : astropy.modeling.tabular.Tabular1D
        Interpolated transmission function.
    _spec : dict
        Filter specifications from SVO service.
        
    Methods
    -------
    from_svo(name)
        Load filter transmission curve from SVO service.
    from_data(name, wavelength, transmission)
        Create filter from custom wavelength and transmission data.
    search(name, case=False)
        Search for filter names in SVO catalog using wildcards.
    apply(wavelength, flux, error=None, plot=False)
        Apply filter to spectrum and return filtered flux.
    plot(ax=None, figsize=(10, 6), title=None, xlabel=None, ylabel=None, filename=None)
        Plot filter transmission curve.
    get_logs(log_type='all')
        Get stored log records (in-memory logging only).
    dump_logs(filename)
        Dump log records to file (in-memory logging only).
    clear_logs()
        Clear stored log records (in-memory logging only).
        
    Raises
    ------
    ValueError
        If filter name format is invalid or filter not found.
    requests.RequestException
        If network request to SVO service fails.
    TypeError
        If input parameters have incorrect types.
        
    Examples
    --------
    >>> from sedlib import Filter
    >>> from astropy import units as u
    >>>
    >>> # Load Johnson V filter
    >>> f = Filter('Generic/Johnson.V')
    >>> transmission = f(5500 * u.AA)
    >>> print(f"Transmission at 5500 Å: {transmission:.3f}")
    >>>
    >>> # Search for TESS filters
    >>> f_search = Filter()
    >>> tess_filters = f_search.search('*TESS*')
    >>> print(f"Found TESS filters: {tess_filters}")
    >>>
    >>> # Create custom filter
    >>> import numpy as np
    >>> wl = np.linspace(4000, 8000, 100) * u.AA
    >>> trans = np.exp(-((wl - 5500*u.AA) / (500*u.AA))**2)
    >>> custom_filter = Filter()
    >>> custom_filter.from_data('Custom/V', wl, trans)
    >>> custom_filter.plot()
    """

    def __init__(
        self,
        name: Optional[str] = None,
        method: str = 'linear',
        bounds_error: bool = False,
        fill_value: Union[float, None] = 0.,
        cache: bool = True,
        timeout: int = 10,
        log_to_file: bool = False,
        log_to_memory: bool = True,
        log_level: int = DEFAULT_LOG_LEVEL,
        log_file: Optional[Union[str, Path]] = 'sed.log'
    ) -> None:
        # Configure instance-specific logging if different from default
        if (log_level != DEFAULT_LOG_LEVEL or 
            not log_to_file or 
            not log_to_memory or 
            log_file != 'sed.log'):
            self.logger, self.memory_handler = setup_logger(
                f"{__name__}.{id(self)}",
                log_file=log_file,
                use_file_handler=log_to_file,
                use_memory_handler=log_to_memory,
                log_level=log_level
            )
        else:
            self.logger = logger
            self.memory_handler = in_memory_handler

        self.logger.info(
            f"BEGIN __init__ - Creating new Filter instance with name='{name}', "
            f"method='{method}'"
        )

        param_types = {
            'name': (type(None), str),
            'method': str,
            'cache': bool,
            'bounds_error': bool,
            'fill_value': (float, type(None)),
        }

        for param, expected_types in param_types.items():
            if not isinstance(locals()[param], expected_types):
                type_names = ' or '.join([
                    t.__name__ for t in (
                        expected_types if isinstance(expected_types, tuple)
                        else (expected_types,)
                    )
                ])
                self.logger.error(
                    f"Type validation failed for parameter '{param}' - "
                    f"expected {type_names}"
                )
                raise TypeError(f'`{param}` must be {type_names} type.')

        if method not in ['linear', 'nearest']:
            self.logger.error(
                f"Invalid method '{method}' specified - "
                "must be 'linear' or 'nearest'"
            )
            raise ValueError('`method` must be one of "linear" or "nearest"!')

        self.name = name
        self._method = method
        self._cache = cache
        self._timeout = timeout
        self._bounds_error = bounds_error
        self._fill_value = fill_value

        self.wavelength = None
        self.transmission = None
        self.data = None
        self._spec = None

        self._xml = None
        self._meta_xml = None

        self._default_flux_unit = u.erg / (u.s * u.cm**2 * u.Hz)

        self._catalog = None

        if name is not None:
            self.logger.debug(
                f"Initializing filter data from SVO for name='{name}'"
            )
            self.from_svo()

        self.logger.info("END __init__ - Filter instance created successfully")

    def __call__(self, wavelength: u.Quantity) -> Optional[float]:
        self.logger.debug(
            f"BEGIN __call__ - Evaluating filter at wavelength={wavelength}"
        )

        if wavelength.unit != u.AA:
            self.logger.debug("Converting wavelength unit to Angstrom")
            wavelength = wavelength.to(u.AA, equivalencies=u.spectral())

        if self.data is not None:
            result = self.data(wavelength)
            self.logger.debug(
                f"END __call__ - Returning transmission value: {result}"
            )
            return result

        self.logger.warning(
            "END __call__ - No filter data available, returning None"
        )
        return None

    def __repr__(self) -> str:
        if self._spec is not None:
            return self._spec['Description']

        return self.name

    def __str__(self) -> str:
        if self._spec is not None:
            return self._spec['Description']

        return self.name

    def __getitem__(self, item: str) -> Any:
        if self._spec is None:
            return None

        return self._spec[item]

    def __eq__(self, object: Optional['Filter']) -> bool:
        if object is None:
            return False

        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) == float(object.WavelengthEff.value)

    def __ne__(self, object: 'Filter') -> bool:
        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) != float(object.WavelengthEff.value)

    def __gt__(self, object: 'Filter') -> bool:
        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) > float(object.WavelengthEff.value)

    def __lt__(self, object: 'Filter') -> bool:
        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) < float(object.WavelengthEff.value)

    def __ge__(self, object: 'Filter') -> bool:
        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) >= float(object.WavelengthEff.value)

    def __le__(self, object: 'Filter') -> bool:
        if not isinstance(object, Filter):
            raise TypeError('`object` must be `Filter` type.')

        return float(self.WavelengthEff.value) <= float(object.WavelengthEff.value)

    def _prepare(self) -> None:
        # Use importlib.resources to access package data files
        try:
            # For Python 3.9+
            meta_file = resources.files('sedlib.filter.data').joinpath('svo_meta_data.xml')
            with meta_file.open('r') as f:
                self._meta_xml = BeautifulSoup(f, features='lxml')
            
            catalog_file = resources.files('sedlib.filter.data').joinpath('svo_all_filter_database.pickle')
            with catalog_file.open('rb') as f:
                self._catalog = pd.read_pickle(f)
        except AttributeError:
            # Fallback for Python 3.7-3.8 using older API
            with resources.open_text('sedlib.filter.data', 'svo_meta_data.xml') as f:
                self._meta_xml = BeautifulSoup(f, features='lxml')
            
            with resources.open_binary('sedlib.filter.data', 'svo_all_filter_database.pickle') as f:
                self._catalog = pd.read_pickle(f)

    def _parse_xml(self) -> None:
        if self._xml is None:
            return

        self._spec = dict()
        params = self._xml.find_all('PARAM')

        for i, param in enumerate(params):
            attrs = param.attrs

            value = attrs['value']

            if attrs['datatype'] == 'double':
                value = float(attrs['value']) * u.Unit(attrs['unit'])

            if 'Unit' in attrs['name']:
                continue

            self._spec[attrs['name']] = value
            self.__dict__[attrs['name']] = value

    def from_svo(self, name: Optional[str] = None) -> None:
        """
        Gets filter from SVO service

        Parameters
        ----------
        name : str
            filter name

        Examples
        --------
        >>> from sedlib import Filter
        >>>
        >>> f = Filter()
        >>> f.from_svo('Generic/Johnson.V')
        >>> f
        Johnson V
        """
        self.logger.info(
            f"BEGIN from_svo - Fetching filter data from SVO. "
            f"name='{name or self.name}'"
        )

        if not isinstance(name, (type(None), str)):
            self.logger.error(f"Invalid name type: {type(name)}")
            raise TypeError('`name` must be `str` or `None` type.')

        if name is not None:
            self.name = name.strip()

        try:
            self.logger.debug(
                f"Downloading filter data from URL: {SVO_FILTER_URL}{self.name}"
            )
            path = download_file(
                f'{SVO_FILTER_URL}{self.name}', cache=self._cache,
                timeout=self._timeout, allow_insecure=True
            )
            self.logger.debug("Filter data download successful")
        except Exception as e:
            self.logger.error(f"Failed to download filter data: {str(e)}")
            raise requests.ConnectionError(
                f"Failed to download filter data: {str(e)}"
            )

        with open(path, 'r') as f:
            text = f.read()

        self._xml = BeautifulSoup(text, features='xml')

        info = self._xml.find('INFO')
        if info is None or info.attrs.get('value') != 'OK':
            self.logger.error(f"Filter '{self.name}' not found in SVO database")
            raise ValueError(f'Filter "{self.name}" is not found!')

        self.logger.debug("Parsing filter metadata from XML")
        self._parse_xml()

        try:
            self.logger.debug("Parsing filter transmission data")
            vt = votable.parse_single_table(BytesIO(text.encode())).to_table()
            self.wavelength = vt['Wavelength']
            self.transmission = vt['Transmission']
        except Exception as e:
            self.logger.error(
                f"Failed to parse filter transmission data: {str(e)}"
            )
            raise ValueError(f"Failed to parse filter data: {str(e)}")

        self.logger.debug("Creating interpolation function for filter curve")
        self.data = Tabular1D(
            points=self.wavelength, lookup_table=self.transmission,
            method=self._method, bounds_error=self._bounds_error,
            fill_value=self._fill_value
        )

        self.logger.info(
            f"END from_svo - Successfully loaded filter '{self.name}' from SVO"
        )

    def from_data(
        self,
        name: str,
        wavelength: u.Quantity,
        transmission: np.ndarray
    ) -> None:
        """
        Creates filter from custom data set

        Parameters
        ----------
        name : str
            filter name

        wavelength : astropy.units.quantity.Quantity
            wavelength array.
            The unit must be Angstrom [A].

        transmission : np.array
            transmission array.
            It must be unitless. Values should be normalized to 1.

        Examples
        --------
        >>> import numpy as np
        >>> from astropy import units as u
        >>> from sedlib import Filter
        >>>
        >>> f = Filter()
        >>>
        >>> # Creating a Neutral Density filter (ND 1.0)
        >>> w = np.arange(3000, 7000, 10) * u.AA
        >>> t = np.full(len(w), fill_value=0.1)
        >>>
        >>> f.from_data(name='ND 1.0', wavelength=w, transmission=t)
        >>> f
        ND 1.0
        """
        self.logger.info(
            f"BEGIN from_data - Creating custom filter '{name}' with "
            f"{len(wavelength)} points"
        )

        if not isinstance(name, str):
            self.logger.error(f"Invalid name type: {type(name)}")
            raise TypeError('`name` must be `str` type.')

        if not isinstance(wavelength, u.Quantity):
            self.logger.error(f"Invalid wavelength type: {type(wavelength)}")
            raise TypeError('`wavelength` must be Quantity object')

        if not isinstance(transmission, np.ndarray):
            self.logger.error(f"Invalid transmission type: {type(transmission)}")
            raise TypeError('`transmission` must be numpy array')

        if wavelength.unit != u.AA:
            self.logger.error(f"Invalid wavelength unit: {wavelength.unit}")
            raise TypeError('`wavelength` must be Angstrom')

        self.name = name
        self.wavelength = wavelength
        self.transmission = transmission

        self.logger.debug("Creating interpolation function for custom filter curve")
        self.data = Tabular1D(
            points=self.wavelength,
            lookup_table=self.transmission,
            method=self._method,
            bounds_error=self._bounds_error,
            fill_value=self._fill_value
        )

        self.logger.info(
            f"END from_data - Custom filter '{name}' created successfully"
        )

    def apply(
        self,
        wavelength: u.Quantity,
        flux: u.Quantity,
        error: Optional[Union[u.Quantity, np.ndarray]] = None,
        plot: bool = False
    ) -> np.ndarray:
        """
        Applies the filter to the given spectrum

        Parameters
        ----------
        wavelength : astropy.units.quantity.Quantity
            wavelength array.
            The unit must be Angstrom [A].

        flux : np.array or astropy.units.quantity.Quantity
            flux array

        error : None, np.array or astropy.units.quantity.Quantity
            error of flux

        plot : bool
            plots the spectrum passing through the filter
            Default value is False

        Return
        ------
            np.array

        Examples
        --------
        >>> import numpy as np
        >>> from astropy import units as u
        >>> from sedlib import Filter
        >>>
        >>> # generate fake date
        >>> w = np.arange(3000, 7000, 10) * u.AA
        >>> f = np.random.random(len(w))
        >>>
        >>> f = Filter('Generic/Johnson.V')
        >>> applied_filter = f.apply(w, f)
        """
        self.logger.info(
            f"BEGIN apply - Applying filter '{self.name}' to spectrum with "
            f"{len(wavelength)} points"
        )

        if not isinstance(wavelength, u.Quantity):
            self.logger.error(f"Invalid wavelength type: {type(wavelength)}")
            raise TypeError('`wavelength` must be Quantity object')

        if not isinstance(flux, u.Quantity):
            self.logger.error(f"Invalid flux type: {type(flux)}")
            raise TypeError('`flux` must be Quantity object')

        if not isinstance(error, (u.Quantity, np.ndarray, type(None))):
            self.logger.error(f"Invalid error type: {type(error)}")
            raise TypeError('`error` must be Quantity or None')

        if not isinstance(plot, bool):
            self.logger.error(f"Invalid plot type: {type(plot)}")
            raise TypeError('`plot` must be bool object')

        if wavelength.unit != u.AA:
            self.logger.error(f"Invalid wavelength unit: {wavelength.unit}")
            raise TypeError('`wavelength` must be Angstrom')

        self.logger.debug("Computing filter-weighted flux")
        result = self.data(wavelength) * flux

        self.logger.info(f"END apply - Filter successfully applied to spectrum")
        return result

    def search(
        self,
        name: Optional[str] = None,
        case: bool = False
    ) -> List[str]:
        """
        Searches filter name from SVO catalog.
        Wild characters can be used in the filter name.

        Parameters
        ----------
        name : None or str
            filter name.
            If name is None, returns all filter names

        case : bool
            Searches for filter names in a case-sensitive
            Default value is False

        Returns
        -------
        list of str

        Examples
        --------
        >>> from sedlib import Filter
        >>>
        >>> f = Filter()
        >>> f.search('*generic*johnson*')
        ['Generic/Johnson.U',
         'Generic/Johnson.B',
         'Generic/Johnson.V',
         'Generic/Johnson.R',
         'Generic/Johnson.I',
         'Generic/Johnson.J',
         'Generic/Johnson.M']
        """
        self.logger.info(
            f"BEGIN search - Searching for filters with pattern='{name}', "
            f"case_sensitive={case}"
        )

        if not isinstance(name, (type(None), str)):
            self.logger.error(f"Invalid name type: {type(name)}")
            raise TypeError('`name` must be `str` or `None` type.')

        if self._catalog is None:
            self.logger.debug("Loading filter catalog")
            self._prepare()

        df = self._catalog

        if name is None:
            result = df['filterID'].to_list()
            self.logger.info(f"END search - Returning all {len(result)} filters")
            return result

        self.logger.debug(f"Applying filter pattern matching")
        if case:
            mask = df['filterID'].apply(fnmatch, args=(name.strip(),))
        else:
            mask = df['filterID'].str.lower().apply(
                fnmatch,
                args=(name.strip().lower(),)
            )

        result = df[mask]['filterID'].to_list()
        self.logger.info(f"END search - Found {len(result)} matching filters")
        return result

    def mag_to_flux(
        self,
        mag: float,
        unit: u.Quantity = u.Jy
    ) -> u.Quantity:
        """Convert magnitude to flux density using the filter's zero point.

        Parameters
        ----------
        mag : float
            Magnitude value to be converted. The magnitude should be in the
            filter's native magnitude system (e.g. AB mag, Vega mag, etc).

        unit : astropy.units.Quantity
            Desired output unit for the flux density.
            Possible values are u.Jy and u.erg / (u.cm**2 * u.AA * u.s)

        Returns
        -------
        flux : astropy.units.Quantity
            Flux density corresponding to the input magnitude. The returned flux
            will have units of erg/(s*cm^2*Hz) or Jansky (Jy) depending on the
            filter's zero point unit.

        Raises
        ------
        ValueError
            If the filter's Zero Point Type is not 'Pogson'.
        TypeError
            If mag is not a float value.
        AttributeError
            If filter data has not been loaded from SVO.

        Notes
        -----
        This method uses the filter's zero point to convert magnitude to flux
        density. It assumes a Pogson magnitude system where:

        flux = ZeroPoint * 10^(-0.4 * magnitude)

        The zero point is obtained from the filter's SVO metadata.

        Examples
        --------
        >>> from sedlib import Filter
        >>> from astropy import units as u
        >>>
        >>> # Initialize Johnson V filter
        >>> f = Filter('Generic/Johnson.V')
        >>>
        >>> # Convert V=15 mag to flux density
        >>> flux = f.mag_to_flux(15.0)
        >>> print(f"{flux:.2e}")
        """
        self.logger.info(
            f"BEGIN mag_to_flux - Converting magnitude {mag} to flux in units "
            f"of {unit}"
        )

        if not self._spec:
            self.logger.warning("No filter specification available")
            return None

        if self.ZeroPointType != 'Pogson':
            self.logger.error(
                f"Unsupported zero point type: {self.ZeroPointType}"
            )
            raise ValueError('The Zero Point Type must be Pogson')

        if not isinstance(mag, (float, int)):
            self.logger.error(f"Invalid magnitude type: {type(mag)}")
            raise TypeError('Magnitude must be a float or integer')

        if not isinstance(unit, u.UnitBase):
            self.logger.error(f"Invalid unit type: {type(unit)}")
            raise TypeError('`unit` must be an astropy Unit object')

        if unit not in [u.Jy, u.erg / (u.cm**2 * u.AA * u.s)]:
            self.logger.error(f"Unsupported flux unit: {unit}")
            raise ValueError(
                'Unit must be either u.Jy or u.erg / (u.cm**2 * u.AA * u.s)'
            )

        self.logger.debug("Computing flux from magnitude")
        flux = self.ZeroPoint * 10 ** (-0.4 * mag)

        if unit != u.Jy:
            self.logger.debug(f"Converting flux from Jy to {unit}")
            flux = (
                2.9979246 *
                (self.WavelengthRef.value**-2) *
                1e-5 *
                flux.value
            )
            flux = flux * u.erg / (u.cm**2 * u.AA * u.s)

        self.logger.info(
            f"END mag_to_flux - Converted magnitude {mag} to flux {flux}"
        )
        return flux

    def flux_to_mag(self, flux: u.Quantity) -> float:
        """
        Convert flux density to magnitude using the filter's zero point.

        Parameters
        ----------
        flux : astropy.units.Quantity
            Flux density to be converted.
            The unit must be erg / (cm2 Hz s) or Jy.
            The flux should be measured through this filter's bandpass.

        Returns
        -------
        mag : float
            Magnitude corresponding to the input flux density in the
            filter's magnitude system.

        Raises
        ------
        TypeError
            If flux is not an astropy Quantity object.
        ValueError
            If the filter's Zero Point Type is not 'Pogson'.
            If the filter data has not been loaded.

        Notes
        -----
        This method uses the filter's zero point to convert flux density to
        magnitude. It assumes a Pogson magnitude system.

        Examples
        --------
        >>> from sedlib import Filter
        >>> from astropy import units as u
        >>>
        >>> f = Filter('Generic/Johnson.V')
        >>> flux = 3.636e-20 * u.erg / (u.cm**2 * u.AA * u.s)
        >>> mag = f.flux_to_mag(flux)
        >>> print(f"{mag:.1f}")
        """
        self.logger.info(
            f"BEGIN flux_to_mag - Converting flux {flux} to magnitude"
        )

        if not self._spec:
            self.logger.warning("No filter specification available")
            return None

        if not isinstance(flux, u.Quantity):
            self.logger.error(f"Invalid flux type: {type(flux)}")
            raise TypeError("Flux must be an astropy Quantity")

        if self.ZeroPointType != 'Pogson':
            self.logger.error(
                f"Unsupported zero point type: {self.ZeroPointType}"
            )
            raise ValueError(
                f'The Zero Point Type must be Pogson\n'
                f'Not implemented for {self.ZeroPointType}'
            )

        self.logger.debug("Computing magnitude from flux")
        if self.ZeroPoint.unit == flux.unit:
            mag = -2.5 * np.log10(flux.value / self.ZeroPoint.value)
        else:
            self.logger.debug(
                "Converting flux units before magnitude calculation"
            )
            f = ((1 / 2.9979246) * 1e5 * 
                 (self.WavelengthRef**2) * flux).value
            mag = -2.5 * np.log10(f / self.ZeroPoint.value)

        self.logger.info(
            f"END flux_to_mag - Converted flux to magnitude {mag}"
        )
        return mag

    def plot(
        self,
        ax: Optional[plt.Axes] = None,
        figsize: tuple = (12, 5),
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        filename: Optional[str] = None
    ) -> None:
        """
        Plots transmission curve

        Parameters
        ----------
        ax : matplotlib.axes._axes.Axes or None
            matplotlib axes

        figsize : tuple
            figure size

        title : str or None
            title of plot
            If title is None, title is filter name

        xlabel : str or None
            label for the x-axis
            If label is None, x-axis label is `Wavelength [A]`

        ylabel : str or None
            label for the y-axis
            If label is None, y-axis label is `Transmission`

        filename : str or None
            filename of the transmission curve
            If filename is None, the curve don't be saved

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> from sedlib import Filter
        >>>
        >>> f = Filter('SLOAN/SDSS.gprime_filter')
        >>>
        >>> f.plot()
        >>> plt.show()
        """
        self.logger.info(
            f"BEGIN plot - Creating transmission curve plot for filter "
            f"'{self.name}'"
        )

        fig = None

        if ax is None:
            self.logger.debug("Creating new figure and axes")
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot()

        if title is None:
            title = self.__str__()

        if xlabel is None:
            xlabel = 'Wavelength [$\\AA$]'

        if ylabel is None:
            ylabel = 'Transmission'

        self.logger.debug("Setting plot labels and title")
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        self.logger.debug("Plotting transmission curve")
        ax.plot(
            self.wavelength, self.transmission,
            'k-', lw=1, label=self.name
        )

        if hasattr(self, 'WavelengthEff') and hasattr(self, 'WidthEff'):
            self.logger.debug("Adding effective wavelength and width indicators")
            ax.axvline(
                self.WavelengthEff.value, color='green',
                linestyle='dashed', linewidth=1.5,
                label=f'Center: {self.WavelengthEff.value: .2f} $\\AA$'
            )

            ax.axvspan(
                xmin=self.WavelengthEff.value - self.WidthEff.value / 2,
                xmax=self.WavelengthEff.value + self.WidthEff.value / 2,
                color='black', linestyle='--', alpha=0.25,
                label=f'Eff. Width: {self.WidthEff.value: .2f} $\\AA$'
            )

            ax.annotate(
                '', xy=(
                    self.WavelengthEff.value - self.WidthEff.value / 2,
                    self.data(self.WavelengthEff.value) / 2
                ),
                xytext=(
                    self.WavelengthEff.value + self.WidthEff.value / 2,
                    self.data(self.WavelengthEff.value) / 2
                ),
                xycoords='data', textcoords='data',
                arrowprops={
                    'arrowstyle': '<->', 'facecolor': 'cyan'
                }
            )

        if hasattr(self, 'WavelengthMin'):
            self.logger.debug("Adding minimum wavelength indicator")
            ax.axvline(
                x=self.WavelengthMin.value, color='blue',
                linestyle='dashed', linewidth=1.5,
                label=f'Min: {self.WavelengthMin.value: .2f} $\\AA$ [1%]'
            )

        if hasattr(self, 'WavelengthMax'):
            self.logger.debug("Adding maximum wavelength indicator")
            ax.axvline(
                x=self.WavelengthMax.value, color='red',
                linestyle='dashed', linewidth=1.5,
                label=f'Max: {self.WavelengthMax.value: .2f} $\\AA$ [1%]'
            )

        ax.legend()

        if filename is not None:
            self.logger.debug(f"Saving plot to file: {filename}")
            fig.savefig(filename)

        self.logger.info(
            "END plot - Filter transmission curve plot created successfully"
        )

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
        if self.memory_handler:
            return self.memory_handler.get_logs(log_type)
        return None

    def dump_logs(self, filename: str) -> None:
        """Dump all stored log records for this filter instance to a file.
        if in-memory logging is enabled, dump the log records to a file,
        otherwise do nothing
        """
        if self.memory_handler:
            self.memory_handler.dump_logs(filename)

    def clear_logs(self) -> None:
        """Clear all stored log records for this filter instance.
        if in-memory logging is enabled, clear the log records,
        otherwise do nothing
        """
        if self.memory_handler:
            self.memory_handler.clear()
