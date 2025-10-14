# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 10:43:53 2025

@author: aydina
"""

import pandas as pd

#%%# High level validation function

def validate_inputs(data, ptable, geog, tab_vars, record_key, threshold):
    """
    Validates inputs for a perturbation process.

    - Type validation on input data & ptable
    - Validate other input arguments
        - Check that at least one variable specified for geog or tab_vars
        - Check variable is specified for record_key
        - Check threshold is an integer   
    - Validate microdata and ptable contain required columns
        - Check data contain the specified geog, tab_vars & record_key
        - Check ptable contains required columns
    - Validate the range of record keys and cell keys
    - Validate data has sufficient % records with record keys to apply perturbation

    Parameters:
    - data (pd.DataFrame): The main dataset
    - ptable (pd.DataFrame): Perturbation table with 'pcv', 'ckey', and 'pvalue' columns
    - geog (list): List of geographic variables
    - tab_vars (list): List of tabulation variables
    - record_key (str): Column name for the record key
    - threshold (int): Threshold value for perturbation

    Raises:
    - TypeError, Exception or Warning message if any validation fails.
    """

    _check_input_data_types(data, ptable)
    _check_input_arguments(geog, tab_vars, record_key, threshold)
    _check_input_data_contain_columns(data, ptable, geog, tab_vars, record_key)


    # Check if the range of record keys and cell keys match
    max_ckey = ptable["ckey"].max()
    min_ckey = ptable["ckey"].min()
    max_rkey = data[record_key].max()
    min_rkey = data[record_key].min()

    _check_key_range(min_ckey, max_ckey, min_rkey, max_rkey)
    
    
    # Check data has sufficient % records with record keys to apply perturbation
    rkey_nan_count = data[record_key].isna().sum()
    rkey_percent = 100 * (1 - rkey_nan_count / len(data))
    
    _check_missing_record_key(rkey_nan_count, rkey_percent)
        
    
    print("Input validation completed.")


#%%# Low level validation functions

def _check_input_data_types(data, ptable):
    """
    Type validation on input data & ptable
    
    Parameters:
    - data (pd.DataFrame): The main dataset
    - ptable (pd.DataFrame): Perturbation table
    
    Raises:
    - TypeError if validation fails.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Specified value for data must be a Pandas DataFrame.")
    if not isinstance(ptable, pd.DataFrame):
        raise TypeError("Specified value for ptable must be a Pandas DataFrame.")


def _check_input_arguments(geog, tab_vars, record_key, threshold):
    """
    Checks if required input arguments are specified
    
    Parameters:
    - geog (list): List of geographic variables
    - tab_vars (list): List of tabulation variables
    - record_key (str): Column name for the record key
    - threshold (int): Threshold value for perturbation

    Raises:
    - Exception if any validation fails.
    """
    # Check that at least one variable specified for geog or tab_vars
    if len(geog) == 0 and len(tab_vars) == 0:
        raise Exception("No variables for tabulation. Please specify value for geog or tab_vars.")
    
    # Check variable is specified for record_key
    if len(record_key) == 0:
        raise Exception("Please specify a value for record_key.")

    # Check threshold is an integer  
    if not isinstance(threshold, int):
        raise Exception("Specified value for threshold must be an integer.")


def _check_missing_record_key(rkey_nan_count, rkey_percent):
    """
    Generates exception or warning message depending on the rate of missing record keys
    
    Parameters:
    - rkey_nan_count (int): Number of missing record keys
    - rkey_percent (float): Percentage of missing record keys
    
    Returns:
    Exception or Warning message
    """
    if rkey_percent < 50:
        raise Exception("Less than 50% of records have a record key. "
                        "Cell key perturbation will be much less effective with fewer "
                        "record keys, so this code requires at least 50% of records to "
                        "have a record key.")
    elif rkey_percent < 100:
        warning_string = "Warning: "
        if rkey_percent < 99.94:
            warning_string += f"Only {round(rkey_percent, 1)}% of records have a record key. "
        warning_string += f"{rkey_nan_count} record(s) have missing record keys."
        print(warning_string)


def _check_input_data_contain_columns(data, ptable, geog, tab_vars, record_key):
    """
    Validates if microdata and ptable contain required columns
    
    Parameters:
    - data (pd.DataFrame): The main dataset
    - ptable (pd.DataFrame): Perturbation table
    - geog (list): List of geographic variables
    - tab_vars (list): List of tabulation variables
    - record_key (str): Column name for the record key

    Raises:
    - Exception if any validation fails.
    """
    # Check geog, tab_vars & record_key specified are columns in data
    if geog and not all(item in data.columns for item in geog):
        raise Exception("Specified value(s) for geog must be column(s) in data.")
    if tab_vars and not all(item in data.columns for item in tab_vars):
        raise Exception("Specified value(s) for tab_vars must be column(s) in data.")
    if record_key and record_key not in data.columns:
        raise Exception("Specified value for record_key must be a column in data.")

    # Check ptable contains required columns
    required_ptable_cols = {"pcv", "ckey", "pvalue"}
    if not required_ptable_cols.issubset(ptable.columns):
        raise Exception("Supplied ptable must contain columns named 'pcv', 'ckey' and 'pvalue'.")


def _check_key_range(min_ckey, max_ckey, min_rkey, max_rkey):
    """
    Generates warning message if there is negative cell key or record key,
    or their ranges do not match
    
    Parameters:
    - min_ckey (int): Minimum value of cell key in ptable
    - max_ckey (int): Maximum value of cell key in ptable
    - min_rkey (int): Minimum value of record_key in data
    - max_rkey (int): Maximum value of record_key in data
    
    Returns:
    Warning message
    """
    if max_ckey != max_rkey:
        print(f'Warning: The ranges of record keys and cell keys appear to be different. '
              f'The maximum record key is {max_rkey}, whereas the maximum cell key is {max_ckey}. '
              f'Please check you are using the appropriate ptable for this data.')
    if min_ckey < 0:
        print("Warning: Negative cell key found in ptable!")
    if min_rkey < 0:
        print("Warning: Negative record key found in data!")