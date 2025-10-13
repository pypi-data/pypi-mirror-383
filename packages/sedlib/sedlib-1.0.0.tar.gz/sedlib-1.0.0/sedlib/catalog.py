#!/usr/bin/env python

"""
Catalog class for organizing photometric data
"""

__all__ = ['Catalog']

import re
import logging
import sqlite3

import numpy as np
import pandas as pd

from astropy import units as u
from astropy.table import Table
from astropy.modeling.physical_models import BlackBody


# # Set up logging
# logger = logging.get(__name__)
# logger.setLevel(logging.DEBUG)

# # Create a file handler
# fh = logging.FileHandler('sed.log')
# fh.setLevel(logging.DEBUG)

# # Create a formatter
# formatter = logging.Formatter(
#     '%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%dT%H:%M:%S'
# )
# fh.setFormatter(formatter)

# # Add the handler to the logger
# logger.addHandler(fh)


class Catalog:
    """
    A class to manage and organize photometric catalog data.
    
    This class provides a wrapper around Astropy Table objects for managing
    photometric data, including methods for data cleaning, filtering, and
    statistical analysis.
    
    Parameters
    ----------
    name : str, optional
        Name identifier for the catalog.
    table : astropy.table.Table, optional
        Existing Astropy Table to use as the catalog data.
    logger : logging.Logger, optional
        Logger instance for logging operations.
    **kwargs : dict, optional
        Additional keyword arguments to set as attributes.
        
    Attributes
    ----------
    name : str
        Catalog name identifier.
    table : astropy.table.Table
        The underlying Astropy Table containing photometric data.
    teff : astropy.units.Quantity, optional
        Effective temperature of the target object.
    teff_error : astropy.units.Quantity, optional
        Error in effective temperature.
    radius : astropy.units.Quantity, optional
        Stellar radius of the target object.
    radius_error : astropy.units.Quantity, optional
        Error in stellar radius.
    distance : astropy.units.Quantity, optional
        Distance to the target object.
    distance_error : astropy.units.Quantity, optional
        Error in distance.
    rejected_data : astropy.table.Table, optional
        Data points that were rejected during filtering operations.
    is_rejected : bool
        Flag indicating if data has been rejected.
        
    Methods
    -------
    from_table(table)
        Initialize catalog from existing Astropy Table.
    add_rows(new_rows)
        Add new rows to the catalog.
    select_rows(criteria, as_dataframe=False)
        Select rows based on criteria.
    update_rows(criteria, new_data)
        Update rows matching criteria.
    delete_rows(criteria=None, row_numbers=None)
        Delete rows based on criteria or row numbers.
    find_missing_data_rows(columns, as_dataframe=True)
        Find rows with missing data.
    delete_missing_data_rows(columns)
        Delete rows with missing data.
    combine_fluxes(method='mean', overwrite=False)
        Combine duplicate filter measurements.
    filter_outliers(sigma_threshold=3.0)
        Apply sigma clipping to filter outliers.
    flux_to_magnitude()
        Convert flux values to magnitudes.
    get_column_stats(column_name)
        Calculate statistics for a column.
    sql_query(query)
        Execute SQL query on the catalog.
        
    Examples
    --------
    >>> from sedlib import Catalog
    >>> from astropy.table import Table
    >>> import numpy as np
    >>>
    >>> # Create catalog from data
    >>> data = {
    >>>     'RA': [180.0, 180.1],
    >>>     'DEC': [30.0, 30.1],
    >>>     'filter': ['V', 'B'],
    >>>     'flux': [1e-12, 8e-13],
    >>>     'eflux': [1e-13, 8e-14]
    >>> }
    >>> table = Table(data)
    >>> catalog = Catalog('test_catalog', table)
    >>>
    >>> # Filter outliers
    >>> catalog.filter_outliers(sigma_threshold=2.0)
    >>>
    >>> # Get statistics
    >>> stats = catalog.get_column_stats('flux')
    >>> print(f"Mean flux: {stats['mean']:.2e}")
    """

    def __init__(self, name=None, table=None, logger=None, **kwargs):
        self.name = name
        self.table = table if table is not None else Table()

        self._logger = logger
        self._logger.info(f"Initialized Catalog with name: {name}")
        
        self.teff = None
        self.teff_error = None
        self.radius = None
        self.radius_error = None
        self.distance = None
        self.distance_error = None

        for key, val in kwargs.items():
            setattr(self, key, val)
        
        if len(self.table) > 0:
            self.table['RA'].info.format = '.3f'
            self.table['DEC'].info.format = '.3f'
            self.table['wavelength'].info.format = '.3f'

            columns = [
                'RA', 'DEC', 'vizier_filter', 'filter',
                'frequency', 'wavelength', 'flux', 'eflux'
            ]
            self.table = table[columns]
        
        self.rejected_data = None
        self.is_rejected = False
        self._rejected_sigma_threshold = 3.0

    def __str__(self):
        return str(self.table)

    def __repr__(self):
        return str(self.table)

    def __setitem__(self, key, value):
        if self.table is None:
            raise ValueError("Table is not initialized.")

        try:
            self.table[key] = value
        except ValueError:
            raise ValueError(f"Column '{key}' does not exist in the table.")

    def __getitem__(self, item):
        if self.table is None:
            raise ValueError("Table is not initialized.")

        try:
            return self.table[item]
        except ValueError:
            raise ValueError(f"Column '{item}' does not exist in the table.")

    # def __getattr__(self, name):
    #     try:
    #         return getattr(self.table, name)
    #     except AttributeError:
    #         raise AttributeError(
    #             f"'{type(self).__name__}' object has no attribute '{name}'"
    #         )

    def __len__(self):
        if self.table is None:
            raise ValueError("Table is not initialized.")
        return len(self.table)

    def __call__(self, max_rows=20):
        return self.table.show_in_notebook(display_length=max_rows)

    def from_table(self, table):
        """
        Initialize Catalog with an existing astropy Table.

        Parameters
        ----------
        table : astropy.table.Table
            The astropy Table to use as the catalog.

        Raises
        ------
        TypeError
            If table is not an astropy.table.Table object.
        """
        if not isinstance(table, Table):
            raise TypeError("Argument must be an astropy.table.Table object")

        self.table = table
        self._self._logger.info(
            f"Loaded table with {len(table)} rows and {len(table.columns)} columns"
        )

    def sql_query(self, query):
        """
        Execute a SQL query on the catalog to retrieve data
        based on specific conditions.

        Parameters
        ----------
        query : str
            A SQL query string to execute.

        Returns
        -------
        result : pandas.DataFrame
            A DataFrame containing the query result.

        Raises
        ------
        ValueError
            If the catalog table is not initialized or if the query fails.

        Examples
        --------
        >>> catalog.sql_query("SELECT * FROM catalog WHERE flux > 1.5")
        >>> catalog.sql_query(
                "SELECT eflux FROM catalog WHERE vizier_filter LIKE '%Johnson%'"
            )
        """
        if self.table is None:
            raise ValueError("Catalog table is not initialized.")

        self._logger.debug(f"Executing SQL query: {query}")

        # Convert the astropy table to a pandas DataFrame
        self._logger.debug("Converting astropy table to pandas DataFrame")
        df = self.table.to_pandas()

        # Convert unsupported column types to strings for SQLite compatibility
        self._logger.debug("Converting unsupported column types to strings")
        for col in df.columns:
            if (not pd.api.types.is_numeric_dtype(df[col]) and
                    not pd.api.types.is_string_dtype(df[col])):
                df[col] = df[col].astype(str)

        # Load the DataFrame into an in-memory SQLite database
        self._logger.debug("Loading DataFrame into SQLite database")
        connection = sqlite3.connect(":memory:")
        try:
            df.to_sql(
                "catalog",
                connection,
                index=False,
                if_exists="replace"
            )
            # Execute the query and fetch the results into a DataFrame
            self._logger.debug("Executing SQL query and fetching results")
            result_df = pd.read_sql_query(query, connection)
            self._logger.info(f"SQL query returned {len(result_df)} rows")
            return result_df
        except Exception as e:
            self._logger.error(f"SQL query failed: {str(e)}")
            raise ValueError(f"Failed to execute query: {e}")
        finally:
            connection.close()  # Ensure the SQLite connection is closed

    def add_rows(self, new_rows):
        """
        Add new rows to the catalog.

        Parameters
        ----------
        new_rows : list of dict
            List of dictionaries, where each dictionary represents a new row
            with keys as column names and values as row data.

        Raises
        ------
        ValueError
            If the catalog table has not been initialized or columns do not match.
        """
        if self.table is None:
            raise ValueError("Catalog table is not initialized.")

        self._logger.info(f"Adding {len(new_rows)} new rows to catalog")

        try:
            self._logger.debug("Validating column names in new rows")
            for row_data in new_rows:
                if not all(column in self.table.colnames
                          for column in row_data.keys()):
                    raise ValueError(
                        "One or more columns in the new row data do not exist "
                        "in the table."
                    )
                self.table.add_row(row_data)
            self._logger.debug("Successfully added new rows")
        except Exception as e:
            self._logger.error(f"Failed to add rows: {str(e)}")
            raise

    def select_rows(self, criteria, as_dataframe=False):
        """
        Select rows from the catalog that meet the specified criteria.

        Parameters
        ----------
        criteria : dict
            A dictionary specifying conditions to select rows for extraction.
            Keys are column names, and values are conditions (e.g., {"flux": "<15"}).

        as_dataframe : bool, optional
            If True, returns the result as a Pandas DataFrame; if False, as an
            astropy.table.Table. Default is False.

        Returns
        -------
        result : astropy.table.Table or pandas.DataFrame
            The rows that match the criteria, either as a Table or DataFrame.

        Raises
        ------
        ValueError
            If the catalog table is not initialized.
        """

        if self.table is None:
            raise ValueError("Catalog table is not initialized.")

        self._logger.debug(f"Selecting rows with criteria: {criteria}")

        # Get row indices that match the criteria
        self._logger.debug("Filtering rows based on criteria")
        row_indices = self._filter_by_criteria(criteria)

        # Extract the rows from the table
        self._logger.debug("Extracting matching rows")
        extracted_table = self.table[row_indices]

        # Convert to DataFrame if requested
        if as_dataframe:
            self._logger.debug("Converting result to pandas DataFrame")
            return extracted_table.to_pandas()

        self._logger.info(f"Selected {len(extracted_table)} rows matching criteria")
        return extracted_table

    def update_rows(self, criteria, new_data):
        """
        Update rows in the catalog that match the criteria with new data.

        Parameters
        ----------
        criteria : dict
            A dictionary specifying conditions to select rows for updating.
            Keys are column names, and values are conditions
            (e.g., {"flux": "<15"} or {"eflux": None}).

        new_data : dict
            Dictionary where keys are column names and values are the new data
            to be set in the selected rows.

        Raises
        ------
        ValueError
            If the criteria contain invalid operators or
            if `new_data` contains invalid columns.
        """

        self._logger.debug(f"Updating rows matching {criteria} with new data: {new_data}")

        self._logger.debug("Finding rows matching criteria")
        rows_to_update = self._filter_by_criteria(criteria)
        self._logger.info(f"Found {len(rows_to_update)} rows to update")

        self._logger.debug("Updating matched rows with new data")
        for row_index in rows_to_update:
            for column, value in new_data.items():
                if column in self.table.colnames:
                    self.table[row_index][column] = value
                else:
                    raise ValueError(
                        f"Column '{column}' does not exist in the table."
                    )

    def delete_rows(self, criteria=None, row_numbers=None):
        """
        Delete rows in the catalog based on criteria or specific row numbers.

        Parameters
        ----------
        criteria : dict, optional
            A dictionary specifying conditions to select rows for deletion.
            Keys are column names, and values are conditions
            (e.g., {"flux": "<15"} or {"eflux": None}).

        row_numbers : int or list of int, optional
            Specific row index or list of row indices to delete.

        Returns
        -------
        int
            Number of rows deleted

        Raises
        ------
        ValueError
            If neither `criteria` nor `row_numbers` is provided, or if criteria
            contain invalid operators, or if arguments have invalid types.
        """
        if criteria is not None and not isinstance(criteria, dict):
            raise ValueError("`criteria` must be a dictionary")

        if row_numbers is not None:
            if isinstance(row_numbers, int):
                row_numbers = [row_numbers]
            elif not isinstance(row_numbers, list):
                raise ValueError(
                    "`row_numbers` must be an integer or list of integers"
                )

            if not all(isinstance(x, int) for x in row_numbers):
                raise ValueError("All elements in `row_numbers` must be integers")

        if criteria is None and row_numbers is None:
            raise ValueError("Either `criteria` or `row_numbers` must be provided")

        rows_to_delete = []
        if criteria:
            self._logger.debug(f"Finding rows matching criteria: {criteria}")
            rows_to_delete.extend(self._filter_by_criteria(criteria))

        if row_numbers:
            self._logger.debug(f"Adding specified row numbers: {row_numbers}")
            rows_to_delete.extend(row_numbers)

        rows_to_delete = list(set(rows_to_delete))
        self._logger.debug(f"Removing {len(rows_to_delete)} rows")
        self.table.remove_rows(rows_to_delete)
        deleted_count = len(rows_to_delete)
        self._logger.info(f"Deleted {deleted_count} rows")

        return deleted_count

    def find_missing_data_rows(self, columns, as_dataframe=True):
        """
        Finds rows with missing (None or NaN) data in any of the specified columns.

        Parameters
        ----------
        columns : str or list of str
            Column name or list of column names to check
            for missing data (either None or NaN).

        as_dataframe : bool, optional
            If True, returns the result as a table-like structure;
            if False, as a catalog table.
            Default is True.

        Returns
        -------
        table-like structure or catalog table
            A table containing rows with missing data (None or NaN)
            in any of the specified columns.

        Raises
        ------
        ValueError
            If the catalog table is not initialized or
            if `columns` is not a valid type.

        Notes
        -----
        This method allows you to identify rows that contain
        missing data (None or NaN) in specified columns for data quality
        checks or cleaning purposes.
        """
        if self.table is None:
            raise ValueError("Catalog table is not initialized.")

        # Convert columns to a list if it's provided as a single string
        if isinstance(columns, str):
            columns = [columns]
        elif not isinstance(columns, list) or not all(
                isinstance(col, str) for col in columns):
            raise ValueError(
                "`columns` must be a string or a list of strings "
                "representing column names."
            )

        self._logger.debug(f"Converting catalog table to pandas DataFrame")
        # Convert the catalog table to a DataFrame for easier manipulation
        df = self.table.to_pandas()

        self._logger.debug(f"Checking for missing data in columns: {columns}")
        # Build the condition to check for either None or NaN in specified columns
        conditions = []
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numeric columns check for NaN
                conditions.append(df[col].isnull() | np.isnan(df[col]))
            else:
                # Non-numeric columns check only for None
                conditions.append(df[col].isnull())

        # Combine all conditions to create a final selection mask
        combined_condition = conditions[0]
        for cond in conditions[1:]:
            combined_condition |= cond

        # Extract rows where any of the conditions are True (indicating None/NaN)
        result_df = df[combined_condition]
        self._logger.info(f"Found {len(result_df)} rows with missing data")

        # Convert to a catalog table or keep as table-like structure
        if as_dataframe:
            return result_df

        return Table.from_pandas(result_df)

    def delete_missing_data_rows(self, columns):
        """
        Delete rows from the catalog that have missing (None or NaN) data
        in any of the specified columns.

        Warning
        -------
        This method permanently deletes rows from the catalog and cannot be undone.
        Use with caution, as there is no way to recover deleted rows.
        Proceed at your own risk.

        Parameters
        ----------
        columns : str or list of str
            Column name or list of column names to check for missing data.
            If a single string is provided, it will be converted to a list.

        Returns
        -------
        int
            The number of rows deleted from the catalog.

        Raises
        ------
        ValueError
            If the catalog table is not initialized or if `columns` is not valid.

        Examples
        --------
        >>> catalog = Catalog(table=some_table)
        >>> deleted_count = catalog.delete_missing_data_rows(['flux', 'wavelength'])
        >>> print(f"Deleted {deleted_count} rows with missing data.")
        """
        # Type checking and conversion for columns parameter
        if isinstance(columns, str):
            columns = [columns]
        elif not isinstance(columns, list) or not all(
                isinstance(col, str) for col in columns):
            raise ValueError(
                "`columns` must be a string or list of strings "
                "representing column names."
            )

        self._logger.debug(f"Finding rows with missing data in columns: {columns}")
        # Find rows with missing data in specified columns
        missing_data_df = self.find_missing_data_rows(columns, as_dataframe=True)

        # Get the indices of rows with missing data
        missing_indices = missing_data_df.index.tolist()

        self._logger.debug(f"Removing {len(missing_indices)} rows with missing data")
        # Delete the rows with missing data
        self.table.remove_rows(missing_indices)

        # Log and return the count of deleted rows
        deleted_count = len(missing_indices)
        self._logger.info(
            f"Deleted {deleted_count} rows with missing data in columns: {columns}"
        )
        return deleted_count

    def combine_fluxes(
        self, method="mean", default_eflux_ratio=0.01, overwrite=False
    ):
        """Combine flux values from the same filter in the catalog table.

        Parameters
        ----------
        method : str, optional
            The method to combine flux values. Options are:
            - "mean": Calculate the weighted mean.
            - "median": Calculate the median.
            Default is "mean".

        default_eflux_ratio : float
            The default ratio of flux to eflux to use when eflux is missing or
            non-positive. Default is 0.01.

        overwrite : bool, optional
            If True, the table in the class is overwritten with the combined data.
            If False, the original table remains unchanged and the combined data 
            is returned as a new table. Default is False.

        Returns
        -------
        int
            If `overwrite=True`, returns the number of unique filters that were 
            combined.
        astropy.table.Table
            If `overwrite=False`, returns a new table containing the combined data.

        Raises
        ------
        ValueError
            If the method is not "mean" or "median".

        Notes
        -----
        - The method combines flux values for rows with the same `vizier_filter` 
          column value. The returned table will contain only the `wavelength`, 
          `frequency`, `flux`, `eflux`, `vizier_filter`, and `filter` columns.
        - If `overwrite=True`, the original table in the class will be replaced 
          with the combined table. If `overwrite=False`, the original table 
          remains unchanged.
        - In the absence of valid `eflux` values (e.g., missing or non-positive 
          values), uniform weights are applied during flux combination. This 
          approach assumes equal uncertainty for all flux values, which may lead 
          to less accurate results. It is recommended to handle missing or invalid
          `eflux` values prior to calling this method for better accuracy.
        - The `default_eflux_ratio` parameter allows you to specify a default 
          ratio of flux to eflux to use when eflux is missing or non-positive. 
          This can be useful if you want to assume a default uncertainty for the 
          flux values.

        Examples
        --------
        >>> from sedlib import SED

        >>> sed = SED("Vega")
        >>> sed.combine_fluxes(method="mean", overwrite=True)
        """
        if not isinstance(method, str):
            raise ValueError("`method` must be a string.")

        if not isinstance(default_eflux_ratio, float):
            raise ValueError("`default_eflux_ratio` must be a float.")

        if not isinstance(overwrite, bool):
            raise ValueError("`overwrite` must be a boolean.")

        if self.table is None:
            raise ValueError("Catalog table is not initialized.")

        if method not in {"mean", "median"}:
            raise ValueError(
                f"Invalid method: {method}. Choose 'mean' or 'median'."
            )

        self._logger.debug("Finding unique filters")

        # Group rows by filter
        unique_filters = set(self.table["vizier_filter"])
        new_rows = []

        self._logger.debug(f"Processing {len(unique_filters)} unique filters")
        for filt in unique_filters:
            # Extract rows for this filter
            rows = self.table[self.table["vizier_filter"] == filt]

            # Flux and eflux values
            fluxes = np.array(rows["flux"])
            efluxes = np.array(rows["eflux"])

            # Replace NaN or zero eflux with default values
            invalid_mask = (np.isnan(efluxes)) | (efluxes == 0)
            if np.any(invalid_mask):
                self._logger.warning(
                    f"Found invalid eflux values (NaN or zero) for filter "
                    f"'{filt}'. Replacing with default."
                )
                efluxes[invalid_mask] = fluxes[invalid_mask] * default_eflux_ratio

            # Calculate weights (inverse of variance)
            weights = 1 / efluxes**2

            self._logger.debug(f"Combining fluxes for filter {filt} using {method}")
            # Combine fluxes
            if method == "mean":
                combined_flux = np.average(fluxes, weights=weights)
            else:  # method == "median"
                combined_flux = np.median(fluxes)

            # Combine efluxes using RMS (root-mean-square)
            combined_eflux = np.sqrt(np.sum(efluxes**2)) / len(efluxes)

            # Add a new row
            new_row = {
                "wavelength": rows["wavelength"][0],
                "frequency": rows["frequency"][0],
                "flux": combined_flux,
                "eflux": combined_eflux,
                "vizier_filter": filt,
                "filter": rows["filter"][0],
            }

            new_rows.append(new_row)

        self._logger.debug("Creating new table with combined rows")
        # Replace table with combined rows
        combined_table = Table(rows=new_rows)

        # Sort the table by "wavelength" column
        combined_table.sort("wavelength")

        # Set units for the new table columns
        for col in ["wavelength", "frequency", "flux", "eflux"]:
            if col in self.table.colnames:
                combined_table[col].unit = self.table[col].unit

        combined_table['wavelength'].info.format = '.3f'
        combined_table['frequency'].info.format = '.3e'
        combined_table['flux'].info.format = '.3e'
        combined_table['eflux'].info.format = '.3e'

        if overwrite:
            self.table = combined_table
            self.flux_to_magnitude()
            
            return len(unique_filters)

        return combined_table

    def _filter_by_criteria(self, criteria):
        """
        Filter rows based on given criteria.

        Parameters
        ----------
        criteria : dict
            Dictionary where keys are column names and values are filter
            conditions (e.g., {"flux": "<15"} or {"name": "== 'star'"}).

        Returns
        -------
        list of int
            List of row indices that match the criteria.

        Raises
        ------
        ValueError
            If a condition in `criteria` contains an invalid operator or if there is
            a type mismatch between the table data and the condition.
        """
        valid_operators = {
            "<", ">", "<=", ">=", "==", "!=", "is None", "is not None"
        }
        matched_rows = []

        for row_index, row in enumerate(self.table):
            if self._row_matches_criteria(row, criteria, valid_operators):
                matched_rows.append(row_index)

        return matched_rows

    def _row_matches_criteria(self, row, criteria, valid_operators):
        """
        Helper function to determine if a row matches all criteria.
        """

        for column, condition in criteria.items():
            if not self._matches_condition(row[column], condition, valid_operators):
                return False  # If any condition fails, the row does not match

        return True  # All conditions matched

    def _matches_condition(self, value, condition, valid_operators):
        """
        Helper function to check if a value meets a specified condition.
        """

        # Check for None conditions
        if condition in {None, "is None"}:
            return value is None
        elif condition == "is not None":
            return value is not None

        # Extract the operator and the comparison value
        operator_found = re.search(r'([<>!]=?|==)', condition)
        if not operator_found or operator_found.group(0) not in valid_operators:
            raise ValueError(
                f"Invalid operator in condition: '{condition}'. "
                f"Allowed operators are: {', '.join(valid_operators)}"
            )

        operator = operator_found.group(0)
        value_str = condition.replace(operator, "", 1).strip()

        # Attempt to convert the condition value to match the type of row's value
        try:
            condition_value = self._convert_condition_value(value, value_str)
            return eval(f"value {operator} condition_value")
        except ValueError:
            raise ValueError(
                f"Failed to convert '{value_str}' to the same type as column value "
                f"'{value}'."
            )
        except TypeError as e:
            raise TypeError(str(e))

    def _convert_condition_value(self, value, value_str):
        """
        Convert the condition value to the same type as the row's value.
        """

        if isinstance(value, (float, np.floating)):
            return float(value_str)

        if isinstance(value, (int, np.integer)):
            return int(value_str)

        if isinstance(value, (str, np.str_)):
            return value_str.strip("'\"")

        raise TypeError(f"Unsupported column data type: {type(value)}")

    def get_column_stats(self, column_name):
        """
        Calculate basic statistics for a specified numerical column.

        Parameters
        ----------
        column_name : str
            The name of the column to calculate statistics for.

        Returns
        -------
        dict
            A dictionary with mean, median, and standard deviation of the column.

        Raises
        ------
        ValueError
            If the specified column does not exist or is non-numeric.
        """
        if column_name not in self.table.colnames:
            raise ValueError(f"Column '{column_name}' does not exist in the table.")

        col_data = self.table[column_name]
        if not isinstance(col_data[0], (int, float, np.integer, np.floating)):
            raise ValueError(f"Column '{column_name}' is non-numeric.")

        return {
            'mean': np.mean(col_data),
            'median': np.median(col_data),
            'std_dev': np.std(col_data),
        }

    def flux_to_magnitude(self):
        """
        Convert all fluxes to magnitudes using the filter's zero point.

        This method converts flux values in the catalog table to magnitudes using
        each filter's zero point. It creates two new columns in the table:
        'mag' for magnitudes and 'mag_err' for magnitude errors.

        The conversion is done using the filter's flux_to_mag() method, which
        assumes a Pogson magnitude system.

        Notes
        -----
        - For rows where the filter is None, magnitude values will be set to None
        - The flux values must be in units compatible with the filter's zero point
        - The magnitude system (AB, Vega, etc.) depends on the filter's zero point

        Examples
        --------
        >>> from sedlib import SED
        >>> from astropy import units as u
        >>>
        >>> sed = SED(name='Vega')
        >>> sed.teff = 10070 * u.K
        >>> sed.radius = 2.766 * u.Rsun
        >>> sed.distance = 7.68 * u.pcs
        >>>
        >>> sed.catalog.flux_to_magnitude()
        """
        self._logger.info("Converting all fluxes to magnitudes")

        if self.table is None:
            self._logger.error("Catalog table is not initialized")
            raise ValueError('Catalog table is not initialized')

        mags = []
        mag_errs = []

        flux_unit = self.table['flux'].unit
        eflux_unit = self.table['eflux'].unit

        self._logger.debug(f"Processing {len(self.table)} rows")

        # Initialize magnitude columns if they don't exist
        if 'mag' not in self.table.colnames:
            self.table['mag'] = [None] * len(self.table)
        if 'mag_err' not in self.table.colnames:
            self.table['mag_err'] = [None] * len(self.table)

        success_count = 0

        for row in self.table:
            f = row['filter']
            flux = row['flux'] * flux_unit
            eflux = row['eflux'] * eflux_unit

            if f is None:
                self._logger.warning(
                    f"Skipping row with filter {row['vizier_filter']}: "
                    "No filter object found"
                )
                mags.append(None)
                mag_errs.append(None)
                continue

            success_count += 1

            # Convert flux to magnitude using filter's zero point
            mags.append(f.flux_to_mag(flux))

            # Calculate magnitude error using error propagation formula
            mag_err = (2.5 / (flux * np.log(10))) * eflux
            mag_errs.append(mag_err)

        self.table['mag'] = mags
        self.table['mag_err'] = mag_errs

        try:
            self.table['mag'].info.format = '.3f'
            self.table['mag_err'].info.format = '.3f'
        except:
            # if there are nan values in columns, convert them to float
            self.table['mag'] = np.array(self.table['mag'], dtype=float)
            self.table['mag_err'] = np.array(self.table['mag_err'], dtype=float)

            # then format the columns
            self.table['mag'].info.format = '.3f'
            self.table['mag_err'].info.format = '.3f'

        self._logger.info(
            f"Successfully converted {success_count} fluxes to magnitudes"
        )

    def filter_outliers(
        self,
        sigma_threshold=3.0,
        over_write=False,
        verbose=False
    ):
        """Filter out outlier data points from the SED catalog using iterative 
        sigma clipping in logarithmic space.

        This method computes the residuals between the observed fluxes in the 
        catalog and the predicted fluxes from the blackbody model computed with 
        the current effective temperature (teff), radius, and distance of the 
        object. The residual is defined as:

            r = log10(F_obs) - log10(F_model)

        where:
            - F_obs is the observed flux.
            - F_model is the flux predicted by the blackbody model:
                  F_model = (π * BlackBody(temperature=teff, scale=scale)
                           (wavelength)) / dR,
              with dR = (distance / radius)^2.

        An iterative sigma clipping is performed on the residuals, flagging any 
        data point for which

            |r - median(r)| > sigma_threshold * σ

        Data points that do not meet this criterion are considered outliers. The 
        process is repeated until no new points are flagged. This allows us to 
        robustly identify points deviating from the continuum—even if some 
        extreme values initially skew the statistics.

        Parameters
        ----------
        sigma_threshold : float, optional
            The sigma threshold for clipping (default is 3.0). Data points with 
            residuals deviating more than sigma_threshold times the standard 
            deviation from the median are flagged as outliers.
        over_write : bool, optional
            If True, the outlier points are permanently removed from the SED 
            object's catalog. If False, the method returns an Astropy Table of 
            outlier points without modifying the catalog.
        verbose : bool, optional
            If True, logs detailed information about each iteration of the 
            filtering process (default is True).

        Returns
        -------
        outliers : astropy.table.Table or None
            If over_write is False, returns an Astropy Table containing the 
            outlier data points. If over_write is True, updates the catalog in 
            place and returns None.

        Raises
        ------
        ValueError
            If required parameters (teff, radius, distance) are not set or if the 
            catalog is missing the required 'wavelength' and 'flux' columns.

        Examples
        --------
        >>> from sedlib import SED
        >>> from astropy import units as u
        >>> sed = SED(name='Vega')
        >>> sed.teff = 9600 * u.K
        >>> sed.radius = 2.818 * u.Rsun
        >>> sed.distance = 7.68 * u.pc
        >>> # Flag outliers using a 3-sigma threshold without modifying catalog:
        >>> outlier_table = sed.filter_outliers(
        ...     sigma_threshold=3.0, over_write=False, plot=True
        ... )
        """
        # Verify that required parameters are set.
        if self.teff is None or self.radius is None or self.distance is None:
            self._logger.error(
                "Effective temperature, radius, and distance must be set before "
                "filtering outliers."
            )
            raise ValueError(
                "Effective temperature, radius, and distance must be set before "
                "filtering outliers."
            )

        # verify that the catalog is initialized
        if self.table is None:
            self._logger.error("Catalog data is required for filtering outliers.")
            raise ValueError("Catalog data is required for filtering outliers.")
        
        self._rejected_sigma_threshold = sigma_threshold

        # geometric dilution factor
        dR = (self.distance.to(u.cm) / self.radius.to(u.cm)) ** 2

        # scale factor
        scale = 1.0 * u.erg / (u.cm**2 * u.AA * u.s * u.sr)

        # blackbody model
        bb_model = BlackBody(temperature=self.teff, scale=scale)

        if "wavelength" not in self.table.colnames or "flux" not in self.table.colnames:
            self._logger.error("Catalog must contain 'wavelength' and 'flux' columns.")
            raise ValueError(
                "Catalog must contain 'wavelength' and 'flux' columns."
            )

        wavelengths = self.table["wavelength"]
        observed_flux = self.table["flux"]

        # Compute the predicted flux for each wavelength.
        predicted_flux = bb_model(wavelengths) * np.pi / dR

        # Calculate residuals in logarithmic space.
        residuals = (
            np.log10(observed_flux.value) - np.log10(predicted_flux.value)
        )

        # Perform iterative sigma clipping.
        # True indicates an "inlier" (continuum point).
        mask = np.ones(len(residuals), dtype=bool)
        iteration = 0
        while True:
            iteration += 1
            current_residuals = residuals[mask]
            if len(current_residuals) == 0:
                self._logger.warning("No data points remain after clipping.")
                break
            median_val = np.median(current_residuals)
            sigma_val = np.std(current_residuals, ddof=1)

            # Create a new mask: keep points within sigma_threshold * sigma of 
            # the median.
            new_mask = (
                np.abs(residuals - median_val) <= sigma_threshold * sigma_val
            )

            # Check for convergence.
            if np.array_equal(mask, new_mask):
                break
            mask = new_mask

        # Identify outliers (those not in the final mask).
        outlier_indices = np.where(~mask)[0]
        num_outliers = len(outlier_indices)
        self._logger.info(
            f"Total outliers detected: {num_outliers} out of {len(residuals)} "
            "data points."
        )

        # save the rejected data
        self.rejected_data = self.table[~mask].copy()

        if verbose:
            print(
                f"Total outliers detected: {num_outliers} out of "
                f"{len(residuals)} data points after {iteration} iterations."
            )

        if over_write:
            # Permanently update the catalog to keep only the inliers.
            self.table = self.table[mask]
            self._logger.info("Outlier points have been removed from the catalog.")
            return None

        self._logger.info("Returning a table of outlier points for inspection.")
        return self.rejected_data
