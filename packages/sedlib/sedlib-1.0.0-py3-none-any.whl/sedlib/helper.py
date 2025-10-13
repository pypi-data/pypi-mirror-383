#!/usr/bin/env python

"""
Helper functions for sedlib
"""

__all__ = [
    'get_pattern', '_init_simbad', 'query_gaia_parameters',
    'find_nearest', 'dumps_quantities', 'get_tmag', 'select_preferred_filters'
]

import json
from typing import Any

import numpy as np

from astropy import units as u
from astropy.units import Quantity
from astroquery.simbad import Simbad
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier


VIZIER_PHOTOMETRY_API_URL = 'https://vizier.cds.unistra.fr/viz-bin/sed'

FILTER_SYSTEM_MAPPINGS = {
    'HIP': {
        'Hp': 'Hipparcos/Hipparcos.Hp',
        'BT': 'TYCHO/TYCHO.B',
        'VT': 'TYCHO/TYCHO.B'
    },
    'SDSS': lambda fn: f'SLOAN/SDSS.{fn[0]}prime_filter' if fn[-1] == "\'" else f'SLOAN/SDSS.{fn}',
    'TYCHO': lambda fn: f'TYCHO/{fn}',
    'Gaia': lambda fn: f'GAIA/GAIA3.{fn}',
    'GAIA/GAIA2': lambda fn: f'GAIA/GAIA2.{fn}',
    'GAIA/GAIA3': lambda fn: f'GAIA/GAIA3.{fn}',
    'IRAS': lambda fn: f'IRAS/IRAS.{fn}mu',
    'DIRBE': lambda fn: f'COBE/DIRBE.{fn.replace(".", "p")}m',
    'Cousins': lambda fn: f'Generic/Cousins.{fn}' if fn in ['R', 'I'] else f'Generic/Johnson_UBVRIJHKL.{fn}',
    # 'Johnson': lambda fn: f'Generic/Johnson_UBVRIJHKL.{fn if fn not in ("L\'", "L", "L\'\'") else "LI" if fn in ("L\'", "L") else "LII"}'
    # 'Johnson': lambda fn: f'Generic/Johnson_UBVRIJHKL.{fn}' if fn not in ("L'", "L", "L''") else f'Generic/Johnson_UBVRIJHKL.{"LI" if fn in ("L'", "L") else "LII"}'
    'Johnson': lambda fn: f'Generic/Johnson_UBVRIJHKL.{fn}' if fn not in ("L'", "L", "L''") else (
        f'Generic/Johnson_UBVRIJHKL.LI' if fn in ("L'", "L") else f'Generic/Johnson_UBVRIJHKL.LII'
    )
}


def get_pattern(system, filter_name):
    if system in FILTER_SYSTEM_MAPPINGS:
        mapping = FILTER_SYSTEM_MAPPINGS[system]
        if callable(mapping):
            return mapping(filter_name)
        elif filter_name in mapping:
            return mapping[filter_name]
    return f'*{system.strip().lower()}*{filter_name.strip().lower()}*'


def find_nearest(array, target):
    """
    Find the nearest value in a NumPy array to a given target.

    Parameters
    ----------
    array : numpy.ndarray
        Input array to search within.
    target : int or float
        The target value to find the nearest to.

    Returns
    -------
    nearest_value : float
        The value in the array closest to the target.
    nearest_index : tuple
        The index of the nearest value (supports multi-dimensional arrays).

    Raises
    ------
    TypeError
        If `array` is not a numpy.ndarray or if `target` is not int or float.

    Examples
    --------
    >>> array = np.array([10, 15, 20, 25, 30])
    >>> find_nearest(array, 18)
    (20, 2)

    >>> array_2d = np.array([[10, 15], [20, 25]])
    >>> find_nearest(array_2d, 18)
    (20, (1, 0))
    """
    # Check if input is a NumPy array
    if not isinstance(array, np.ndarray):
        raise TypeError("Input array must be a NumPy ndarray.")
    
    # Check if target is of type int or float
    if not isinstance(target, (int, float)):
        raise TypeError("Target value must be of type int or float.")
    
    # Flatten the array to handle both 1D and multi-dimensional cases
    flat_index = np.abs(array - target).ravel().argmin()
    
    # Get the nearest value
    nearest_value = array.ravel()[flat_index]
    
    # Convert flat index to multi-dimensional index if necessary
    nearest_index = np.unravel_index(flat_index, array.shape)

    return nearest_value, nearest_index


def _init_simbad():
    # Simbad.reset_votable_fields()
    # Simbad.remove_votable_fields('coordinates')
    # Simbad.add_votable_fields(
    #     'ra', 'dec', 'parallax', 'otype', 'otypes', 'sptype', 'distance'
    # )
    Simbad.add_votable_fields(
        'parallax',
    )


def query_gaia_parameters(name, search_simbad=True):
    """Query Gaia DR3 to get stellar parameters for an object.

    This function first searches for the object's Gaia DR3 source ID using SIMBAD,
    then queries the Gaia archive for parallax, distance, temperature and radius information.

    Parameters
    ----------
    name : str
        Name of the astronomical object to query
    
    search_simbad : bool, optional
        If True, search for the object's Gaia DR3 source ID using SIMBAD.
        If False, use the provided name as the Gaia DR3 source ID.

    Returns
    -------
    dict or None
        Dictionary containing source_id, parallax, parallax_error, distance_pc,
        distance_error_pc, teff (effective temperature) and radius. Returns None 
        if no SIMBAD match is found.
    """
    gaia_id = name

    # Query SIMBAD for object IDs
    if search_simbad:
        simbad_results = Simbad.query_objectids(name)
        if len(simbad_results) == 0:
            return None

        # Find Gaia DR3 ID
        gaia_id = None
        for id_entry in simbad_results['id']:
            if 'Gaia DR3' in id_entry:
                # gaia_id = id_entry.strip().split()[-1]
                gaia_id = id_entry
                break

        if not gaia_id:
            return None
    
    gaia_id = gaia_id.strip().split()[-1]

    # Construct and execute Gaia query
    query = f"""
        SELECT
            dr3.source_id,
            dr3.ra,
            dr3.dec,
            dr3.parallax,
            dr3.parallax_error,
            1000.0 / dr3.parallax AS distance_pc,
            (1000.0 / dr3.parallax) * (dr3.parallax_error / dr3.parallax) AS distance_error_pc,
            dr3.teff_gspphot AS teff,
            dr3.teff_gspphot_lower AS teff_lower,
            dr3.teff_gspphot_upper AS teff_upper,
            ap.radius_gspphot AS radius,
            ap.radius_gspphot_lower AS radius_lower,
            ap.radius_gspphot_upper AS radius_upper
        FROM gaiadr3.gaia_source AS dr3
        INNER JOIN gaiadr3.astrophysical_parameters AS ap
        ON dr3.source_id = ap.source_id
        WHERE dr3.source_id = {gaia_id}
    """

    job = Gaia.launch_job(query)
    t = job.get_results()

    # Convert table row to dictionary
    result = {
        'source_id': t['source_id'][0],
        'ra': t['ra'][0],
        'dec': t['dec'][0],
        'parallax': t['parallax'][0],
        'parallax_error': t['parallax_error'][0],
        'distance_pc': t['distance_pc'][0],
        'distance_error_pc': t['distance_error_pc'][0],
        'teff': t['teff'][0],
        'teff_lower': t['teff_lower'][0],
        'teff_upper': t['teff_upper'][0],
        'radius': t['radius'][0],
        'radius_lower': t['radius_lower'][0],
        'radius_upper': t['radius_upper'][0]
    }

    return result


def dumps_quantities(obj: Any, **json_kwargs) -> str:
    """
    Serialize `obj` to JSON, converting any astropy.units.Quantity into its raw value.

    Parameters
    ----------
    obj
        Any Python object (e.g. dict, list, nested structures) possibly
        containing Quantity instances.
    json_kwargs
        Extra keyword arguments to pass through to json.dumps()
        (e.g. indent=2, sort_keys=True).

    Returns
    -------
    str
        The JSON string with all Quantity instances replaced by their .value.
    """
    class _QuantityEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, Quantity):
                return o.value
            if isinstance(o, np.ndarray):
                return o.tolist()
            # Handle LbfgsInvHessProduct type from scipy.optimize
            if o.__class__.__name__ == 'LbfgsInvHessProduct':
                return "<LbfgsInvHessProduct object>"
            # Try to convert other numpy types
            if isinstance(o, (np.integer, np.floating, np.bool_)):
                return o.item()
            return super().default(o)

    return json.dumps(obj, cls=_QuantityEncoder, **json_kwargs)


def get_tmag(source_id, release="dr3"):
    """
    Retrieve Tmag and its uncertainty (e_Tmag) from the TESS Input Catalog (TIC 8.2, IV/39/tic82),
    given either a Gaia DR2 or DR3 source_id.

    Parameters
    ----------
    source_id : int or str
        The Gaia source identifier (DR2 or DR3), depending on `release`.
    release : str, optional
        Indicates which Gaia release `source_id` refers to: "dr2" or "dr3".
        Default is "dr3".

    Returns
    -------
    tuple (Tmag, e_Tmag) as floats, or None if no match is found.
    """
    # Vizier.ROW_LIMIT = 1
    
    catalog_id = "IV/39/tic82"
    source_id = str(source_id).strip()

    def _query_tic_by_dr2(dr2_id):
        """Query TIC for Tmag given a DR2 source_id string."""
        # 1) Try a direct GAIA‐constraint on TIC
        viz = Vizier(columns=["Tmag", "e_Tmag", "GAIA"], catalog=catalog_id)
        result = viz.query_constraints(GAIA=dr2_id)

        if result:
            t = result[0]
            return float(t['Tmag'][0]), float(t['e_Tmag'][0])

        # 2) Fallback: cone‐search around "Gaia DR2 <dr2_id>"
        viz_fallback = Vizier(columns=["Tmag", "e_Tmag"], catalog=catalog_id)
        name = f"Gaia DR2 {dr2_id}"
        fallback = viz_fallback.query_object(name, radius=2 * u.arcsec)
        if fallback and catalog_id in fallback and len(fallback[catalog_id]) > 0:
            row = fallback[catalog_id][0]
            return float(row["Tmag"]), float(row["e_Tmag"])

        return None

    if release.lower() == "dr2":
        return _query_tic_by_dr2(source_id)

    adql = f"""
        SELECT TOP 1 x.dr2_source_id
        FROM gaiadr3.gaia_source AS dr3
        JOIN gaiadr3.dr2_neighbourhood AS x
          ON dr3.source_id = x.dr3_source_id
        WHERE dr3.source_id = {source_id}
    """
    job = Gaia.launch_job(adql)
    rows = job.get_results()
    
    if len(rows) == 0:
        return None

    dr2_id = str(rows["dr2_source_id"][0])
    return _query_tic_by_dr2(dr2_id)


def select_preferred_filters(sed, column, column_error) -> dict:
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
        'TESS/TESS:Red'
    ]

    result = {}
    chosen_bands = {}

    for filt in allowed_filters:
        mask = sed.catalog.table['vizier_filter'] == filt
        if not mask.any():
            continue

        row = sed.catalog.table[mask][0]
        mag = row[column]
        mag_err = row[column_error]

        band = filt.split(":")[-1]
        if band not in chosen_bands:
            if band == 'Red':
                band = 'TESS'
            result[band.upper()] = (mag, mag_err)
            chosen_bands[band] = filt

    return result
