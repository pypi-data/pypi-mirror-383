#!/usr/bin/env python

__all__ = ['BolometricCorrection']

import math
from typing import Optional, Tuple
from importlib import resources

import yaml

import numpy as np

import astropy.units as u


class BolometricCorrection(object):
    """
    Class for computing bolometric corrections (BC) for stars based on their
    effective temperature and for inferring stellar properties such as the weighted
    bolometric magnitude and the stellar radius (expressed in solar units).

    This class performs a full analysis pipeline that includes the following steps:
      1. **Loading Coefficients:** Reads temperature-to-bolometric correction
         polynomial coefficients from a YAML file. These coefficients (with their
         fixed uncertainties) allow the calculation of bolometric corrections using
         a 4th-degree polynomial.
      2. **Filter Selection:** From the available photometric filters in the star's
         SED, the class selects the preferred filters (e.g., Johnson B, V; GAIA G,
         GBP, GRP, etc.) based on a pre-defined priority order.
      3. **Bolometric Correction Computation:** For each selected filter, it
         computes the bolometric correction for the target star's effective
         temperature.
      4. **Absolute Bolometric Magnitude Determination:** The computed corrections
         are applied to the observed absolute magnitudes, and a weighted average is
         obtained using inverse-variance weighting. This yields the star's absolute
         bolometric magnitude and its associated uncertainty.
      5. **Stellar Radius Estimation:** Using the relation between luminosity,
         radius, and effective temperature (i.e., L = 4πR²σT⁴) along with the
         bolometric magnitude definition (M_Bol = -2.5 log L + constant), the
         stellar radius is determined relative to the Sun. The target star's radius
         (in R_sun) is computed via:
            R_star / R_sun = 10^((M_bol,☉ - M_bol,star)/5) * (T_☉ / T_star)²,
         and the uncertainty is propagated accordingly.

    The full analysis pipeline can be executed in one go using the `run` method.

    Example
    -------
    >>> from sedlib import SED, BolometricCorrection
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
    >>>
    >>> bc = BolometricCorrection(sed=sed)
    >>> bc.run()
    >>> print(f"Stellar radius: {bc.radius:.2f} ± {bc.radius_error:.2f} R_sun")
    """

    def __init__(
        self,
        sed: Optional[object] = None,
        coeff_file: Optional[str] = None,
        accept_radius: bool = False
    ):
        """
        Initialize the BolometricCorrection instance.

        Parameters
        ----------
        sed : sedlib.SED, optional
            SED object containing catalog and stellar parameters. Must have
            computed absolute magnitudes and effective temperature.
        coeff_file : str, optional
            Path to the YAML file containing the coefficient data. If None, the
            default 'temp_to_bc_coefficients.yaml' file is used.
        accept_radius : bool, optional
            If True, the computed radius will be stored in sed.radius and 
            sed.radius_error. Default is False.
            
        Raises
        ------
        ValueError
            If sed object is provided but lacks required attributes.
        FileNotFoundError
            If coefficient file cannot be found.
        yaml.YAMLError
            If coefficient file cannot be parsed.
            
        Notes
        -----
        The bolometric correction analysis requires:
        - Effective temperature (sed.teff)
        - Absolute magnitudes for preferred filters
        - Distance information for magnitude calculations
        
        The preferred filters are selected automatically based on availability
        and priority: Johnson B,V; GAIA G, GBP, GRP; etc.
        """
        self._sed = sed
        self._coefficients = {}
        self._bolometric_corrections = {}
        self._bolometric_mags = {}
        self._abs_mags = {}

        self._abs_bol_mag = None
        self._abs_bol_mag_err = None

        self._sun_bol_mag = 4.74
        self._sun_teff = 5772 * u.K

        self._radius = None
        self._radius_error = None

        self._accept_radius = accept_radius

        if sed is not None:
            self._sed = sed
            self._abs_mags = self._select_preferred_filters()

        self._load_coefficients(coeff_file)

    @property
    def abs_bol_mag(self) -> float:
        return self._abs_bol_mag

    @property
    def abs_bol_mag_err(self) -> float:
        return self._abs_bol_mag_err

    @property
    def radius(self) -> u.Quantity:
        return self._radius

    @property
    def radius_error(self) -> u.Quantity:
        return self._radius_error

    def _load_coefficients(self, coeff_file: Optional[str] = None) -> dict:
        """
        Internal method to load polynomial coefficients from a YAML file and store
        each as a tuple (value, error). Additionally, if a filter block contains
        an "RMS" key, that value is removed and stored as the fixed error for
        that filter.

        Parameters
        ----------
        coeff_file : str, optional
            Path to the YAML file containing coefficient data.
        """
        self._coefficients = {}

        try:
            if coeff_file is None:
                file_obj = resources.open_text(
                    'sedlib.data',
                    'temp_to_bc_coefficients.yaml'
                )
            else:
                file_obj = open(coeff_file, 'r')
            with file_obj as file:
                self._coefficients = yaml.safe_load(file)
        except Exception as e:
            source = ("package resources" if coeff_file is None
                     else f"file '{coeff_file}'")
            raise IOError(f"Error loading coefficients from {source}: {e}")

    def _select_preferred_filters(self) -> dict:
        """
        The allowed filters and their priority are defined as follows:

        - Johnson:B
        - Johnson:V
        - GAIA/GAIA3:G
        - GAIA/GAIA3:Gbp
        - GAIA/GAIA3:Grp
        - GAIA/GAIA2:G
        - GAIA/GAIA2:Gbp
        - GAIA/GAIA2:Grp
        - Gaia:G
        - TESS/TESS:Red

        Returns
        -------
        dict
            Dictionary where keys are the selected filter names and values are
            tuples (abs_mag, abs_mag_err).
        """
        # allowed filters in order
        allowed_filters = [
            'Johnson:B',
            'Johnson:V',
            'GAIA/GAIA3:G',
            'GAIA/GAIA3:Grp',
            'GAIA/GAIA3:Gbp',
            'GAIA/GAIA2:G',
            'GAIA/GAIA2:Grp',
            'GAIA/GAIA2:Gbp',
            'Gaia:G',
            'TESS/TESS:Red',
        ]

        result = {}
        chosen_bands = {}

        for filt in allowed_filters:
            mask = self._sed.catalog.table['vizier_filter'] == filt
            if not mask.any():
                continue

            row = self._sed.catalog.table[mask][0]
            mag = row['abs_mag']
            mag_err = row['abs_mag_err']

            band = filt.split(":")[-1]
            if band not in chosen_bands:
                if band == 'Red':
                    band = 'TESS'
                result[band.upper()] = (mag, mag_err)
                chosen_bands[band] = filt

        return result

    @staticmethod
    def _compute_bc_and_error(
        T: float,
        T_err: float,
        coeffs: dict
    ) -> Tuple[float, float]:
        """
        Internal method to compute the bolometric correction (BC) for a given
        effective temperature (in Kelvin) using the 4th-degree polynomial. (The
        propagated uncertainty computed here will later be replaced by the fixed
        value from the YAML file.)

        Parameters
        ----------
        T : float
            Effective temperature in Kelvin (nominal value).
        T_err : float
            Effective temperature error in Kelvin.
        coeffs : dict
            Dictionary of coefficients for a specific filter with keys 'a', 'b',
            'c', 'd', 'e'. Each coefficient is a tuple: (value, error).

        Returns
        -------
        tuple of float
            (BC, sigma_BC) where sigma_BC is computed but will later be replaced
            by a fixed value.
        """
        # Compute L = log10(T)
        L = math.log10(T)
        # Propagate error from T to L: σ_L = T_err / (T ln(10))
        sigma_L = T_err / (T * math.log(10))

        # Unpack coefficients
        a, sigma_a = coeffs["a"]
        b, sigma_b = coeffs["b"]
        c, sigma_c = coeffs["c"]
        d, sigma_d = coeffs["d"]
        e, sigma_e = coeffs["e"]

        # Compute nominal BC:
        BC = a + L * b + (L**2) * c + (L**3) * d + (L**4) * e

        # Compute propagated uncertainty (to be replaced)
        dfdL = b + 2 * L * c + 3 * (L**2) * d + 4 * (L**3) * e
        sigma_BC = np.sqrt(
            sigma_a**2 +
            (L * sigma_b)**2 +
            ((L**2) * sigma_c)**2 +
            ((L**3) * sigma_d)**2 +
            ((L**4) * sigma_e)**2 +
            (dfdL * sigma_L)**2
        )
        return BC, sigma_BC

    def compute_bolometric_corrections(
        self,
        filter_name: Optional[str] = None,
        return_results: bool = False
    ) -> dict:
        """
        Compute bolometric corrections (BC) for either a single filter or all
        available filters.

        Parameters
        ----------
        filter_name : str, optional
            Filter name (e.g., 'B', 'V', 'G', 'GBP', 'GRP', 'TESS').
            If None, computes BCs for all available filters.
        return_results : bool, optional
            If True, returns the computed BCs as a dictionary.
            If False, updates the instance variables and returns None.

        Returns
        -------
        dict
            Dictionary mapping filter names to tuples of (BC, fixed_error).
            For a single filter, returns a dictionary with one entry.

        Raises
        ------
        ValueError
            If specified filter_name is not valid.
        """
        results = {}

        if filter_name is not None:
            # Single filter case
            if filter_name not in self._coefficients:
                raise ValueError(
                    "Invalid filter name. Choose from: " +
                    ", ".join(self._coefficients.keys())
                )
            filters_to_process = [filter_name]
        else:
            # All filters case
            filters_to_process = self._coefficients.keys()

        T = self._sed.teff.to(u.K).value
        T_err = self._sed.teff_error.to(u.K).value

        for filt in filters_to_process:
            coeffs = self._coefficients[filt]

            bc_result = self._compute_bc_and_error(T, T_err, coeffs)
            fixed_err = coeffs['RMS']

            results[filt] = (bc_result[0], fixed_err)

        self._bolometric_corrections = results

        return self._bolometric_corrections if return_results else None

    def apply_correction(self):
        """
        Apply the bolometric correction to a set of absolute magnitudes.
        """
        for filt in self._abs_mags.keys():
            mag, mag_err = self._abs_mags[filt]
            bc, bc_err = self._bolometric_corrections[filt]

            self._bolometric_mags[filt] = (
                mag + bc,
                np.sqrt(mag_err**2 + bc_err**2)
            )

    def compute_weighted_abs_bol_mag(
        self,
        return_results: bool = False
    ) -> Tuple[float, float]:
        """
        Compute a weighted average of the bolometric magnitudes from different
        filters.

        The weighted average is computed using inverse-variance weighting:

            weighted_mag = sum(m_i / sigma_i^2) / sum(1 / sigma_i^2)
            weighted_error = sqrt(1 / sum(1 / sigma_i^2))

        Parameters
        ----------
        return_results : bool, optional
            If True, returns the computed weighted average as a tuple.
            If False, updates the instance variables and returns None.

        Returns
        -------
        tuple of float
            (weighted_bolometric_magnitude, weighted_error)

        Raises
        ------
        ValueError
            If no bolometric magnitudes have been computed.
        """
        if not self._bolometric_mags:
            raise ValueError(
                "No bolometric magnitudes available. "
                "Run apply_correction() first."
            )

        mags = []
        errors = []
        for filt in self._bolometric_mags:
            mag, err = self._bolometric_mags[filt]
            mags.append(float(mag))
            errors.append(err)

        mags = np.array(mags)
        errors = np.array(errors)
        weights = 1 / errors**2

        self._abs_bol_mag = np.sum(mags * weights) / np.sum(weights)
        self._abs_bol_mag_err = np.sqrt(1 / np.sum(weights))

        if return_results:
            return (self._abs_bol_mag, self._abs_bol_mag_err)
        return None

    def compute_normalized_radius(
        self,
        return_results: bool = False
    ) -> Tuple[u.Quantity, u.Quantity]:
        """
        The radius ratio is calculated as:
            R_star / R_sun = 10^((M_bol,sun - M_bol,star)/5) * (T_sun / T_star)^2

        Uncertainty propagation (via logarithmic differentiation):
            (delta R_star / R_star)^2 = ( (ln10/5 * delta M_bol,star)^2 +
                                        (2 * delta T_star / T_star)^2 )

        Parameters
        ----------
        return_results : bool, optional
            If True, return the radius ratio and its error as a tuple.
            If False, update the instance variables and return None.

        Returns
        -------
        tuple of astropy.units.Quantity
            A tuple (radius_ratio, radius_ratio_err) where:
            - radius_ratio is the target star's radius in units of the Sun's
              radius.
            - radius_ratio_err is the corresponding uncertainty.

        Raises
        ------
        ValueError
            If the target star's bolometric magnitude (or its error) has not been
            computed, or if the Sun's parameters are not defined.
        """
        # Ensure that the target star's bolometric magnitude and error are
        # available.
        if self._abs_bol_mag is None or self._abs_bol_mag_err is None:
            raise ValueError(
                "Target star's bolometric magnitude and/or its error have not "
                "been computed. Please run compute_weighted_abs_bol_mag() first."
            )

        # Retrieve target star parameters.
        target_mbol = self._abs_bol_mag
        target_mbol_err = self._abs_bol_mag_err
        target_teff = self._sed.teff.to(u.K).value
        target_teff_err = self._sed.teff_error.to(u.K).value

        # Retrieve Sun parameters.
        sun_bol_mag = self._sun_bol_mag
        sun_teff = self._sun_teff.value

        # Compute the radius ratio using the relation:
        # R_star / R_sun = 10^((M_bol,sun - M_bol,star)/5) * (T_sun / T_star)^2
        radius_ratio = (10 ** ((sun_bol_mag - target_mbol) / 5.0) *
                       (sun_teff / target_teff) ** 2)

        # Propagate uncertainties.
        # The logarithmic derivative of R_ratio is:
        #   d(ln(R_ratio)) = -(ln10/5)*dM_bol,star - 2*(dT_star/T_star)
        # Thus, the relative uncertainty is:
        #   (delta R_ratio / R_ratio)^2 = ( (ln10/5 * delta M_bol,star)^2 +
        #                                   (2 * delta T_star/T_star)^2 )
        rel_error = np.sqrt(
            (np.log(10) / 5 * target_mbol_err) ** 2 +
            (2 * target_teff_err / target_teff) ** 2
        )
        radius_ratio_err = radius_ratio * rel_error

        self._radius = radius_ratio * u.R_sun
        self._radius_error = radius_ratio_err * u.R_sun

        if return_results:
            return self._radius, self._radius_error
        return None

    def run(self, verbose: bool = False) -> None:
        """
        Execute the complete bolometric correction analysis pipeline.

        The pipeline performs the following steps:
          1. Compute bolometric corrections for available filters.
          2. Apply the bolometric corrections to the target star's absolute
             magnitudes.
          3. Compute a weighted average of the corrected bolometric magnitudes.
          4. Compute the target star's radius in units of the Sun's radius by
             comparing the target's bolometric magnitude and effective temperature
             with solar values.

        Parameters
        ----------
        verbose : bool, optional
            If True, print verbose output.

        Returns
        -------
        tuple of astropy.units.Quantity
            A tuple (radius, radius_error)

        Example
        -------
        >>> from sedlib import SED, BolometricCorrection
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
        >>>
        >>> bc = BolometricCorrection(sed=sed)
        >>> bc.run()
        >>> print(
        ...     f"Stellar radius: {bc.radius:.2f} ± {bc.radius_error:.2f} R_sun"
        ... )
        """
        # Execute pipeline sequentially
        self.compute_bolometric_corrections()
        self.apply_correction()
        self.compute_weighted_abs_bol_mag()
        self.compute_normalized_radius()

        if verbose:
            print(
                f"Stellar radius: {self._radius:.2f} ± "
                f"{self._radius_error:.2f} R_sun"
            )

        if self._accept_radius:
            self._sed._radius = self._radius
            self._sed._radius_error = self._radius_error

        self._result = {
            'abs_mags': self._abs_mags,
            'bolometric_corrections': self._bolometric_corrections,
            'bol_mags': self._bolometric_mags,
            'abs_bol_mag': self._abs_bol_mag,
            'abs_bol_mag_err': self._abs_bol_mag_err,
            'radius': self._radius,
            'radius_error': self._radius_error
        }

        return self._radius, self._radius_error
