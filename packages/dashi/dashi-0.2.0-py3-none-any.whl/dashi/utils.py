# Copyright 2024 Biomedical Data Science Lab, Universitat Politècnica de València (Spain)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utils functions
"""

from datetime import datetime
from typing import Optional, List

import pandas as pd

from dashi._constants import MONTH_SHORT_ABBREVIATIONS, VALID_DATE_TYPE


def _format_date_for_year(date: datetime) -> str:
    year_part = date.strftime('%Y')

    return year_part


def _format_date_for_month(date: datetime) -> str:
    year_part = date.strftime('%y')
    month_part = MONTH_SHORT_ABBREVIATIONS[date.month - 1]

    return year_part + month_part


def _format_date_for_week(date: datetime) -> str:
    year_part = date.strftime('%y')
    month_part = MONTH_SHORT_ABBREVIATIONS[date.month - 1]
    day_part = str(date.isoweekday())

    return year_part + month_part + day_part

def _validate_date_format(date_format, verbose=False):
    """Valida el formato de fecha y muestra mensajes informativos si verbose=True."""
    has_year = _is_letter_in_date_format(date_format, ['Y', 'y'])
    has_month = _is_letter_in_date_format(date_format, ['m', 'M', 'b', 'B', 'h'])
    has_day = _is_letter_in_date_format(date_format, ['d', 'D'])

    if has_year and has_month and has_day:
        if verbose:
            print('The data format contains year, month, and day')
    elif has_year and has_month:
        if verbose:
            print('The data format contains year and month but not day')
            print('Take into account that if you perform an analysis by week, the day will be automatically assigned as the first day of the month.')
    elif has_year:
        if verbose:
            print('The data format contains only the year')
            print('Take into account that if you perform an analysis by week or by month, they will be automatically assigned as the first day of the month and first month of the year.')
    else:
        print('Please, check the format of the date. At least it should contain the year.')
        raise ValueError('Invalid date format')


def format_data(input_dataframe: pd.DataFrame,
                *,
                date_column_name: Optional[str] = None,
                source_column_name: Optional[str] = None,
                date_format: Optional[str] = '%y/%m/%d',
                verbose: bool = False,
                numerical_column_names: Optional[List[str]] = None,
                categorical_column_names: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Function to transform dates into 'Date' Python format

    Parameters
    ----------
    input_dataframe : pd.DataFrame
        Pandas dataframe object with at least one columns of dates.

    date_column_name: Optional[str]
        The name of the column containing the dates. If you are not performing a temporal analysis, set this parameter
        to `None`.

    source_column_name: Optional[str]
        The name of the column containing the source information. If you are not performing a multi-source analysis,
        set this parameter to `None`.

    date_format: Optional[str]
        Structure of date format. By default '%y/%m/%d'.

    verbose: bool
        Whether to display additional information during the process. Defaults to `False`.

    numerical_column_names: Optional[List[str]]
        A list containing all the numerical column names in the dataset. If this parameter is `None`, the variables
        types must be managed by the user.

    categorical_column_names: Optional[List[str]]
        A list containing all the categorical column names in the dataset. If this parameter is `None`, the variables
        types must be managed by the user.

    Returns
    -------
    pd.DataFrame
        A `pandas.DataFrame` with each column cast to its correct dtype and any rows containing missing values in the
        date or source fields dropped.
    """
    if date_column_name is not None and date_column_name not in input_dataframe.columns:
        raise ValueError(f'There is no column in your DataFrame named as: {date_column_name}')

    if source_column_name is not None and source_column_name not in input_dataframe.columns:
        raise ValueError(f'There is no column in your DataFrame named as: {source_column_name}')

    output_dataframe = input_dataframe.copy()

    if numerical_column_names is not None:
        if verbose:
            print('Formating numerical columns as float')
        for col in numerical_column_names:
            output_dataframe[col] = output_dataframe[col].astype(float)

    if categorical_column_names is not None:
        if verbose:
            print('Formating categorical columns as category')
        for col in categorical_column_names:
            output_dataframe[col] = output_dataframe[col].astype(str).astype('category')


    if date_column_name is not None:
        if output_dataframe[date_column_name].dtype == VALID_DATE_TYPE:
            return output_dataframe

        if verbose:
            print(f'Formatting the {date_column_name} column')

        _validate_date_format(date_format, verbose)

        output_dataframe[date_column_name] = pd.to_datetime(output_dataframe[date_column_name], format=date_format)

        initial_len = len(output_dataframe)
        output_dataframe = output_dataframe.dropna(subset=[date_column_name]).reset_index(drop=True)
        removed_rows = initial_len - len(output_dataframe)
        if removed_rows > 0:
            print(f'There are {removed_rows} rows that do not contain date information. They have been removed.')
        return output_dataframe

    elif source_column_name is not None:
        initial_len = len(output_dataframe)
        output_dataframe = output_dataframe.dropna(subset=[source_column_name]).reset_index(drop=True)
        removed_rows = initial_len - len(output_dataframe)
        if removed_rows > 0:
            print(f'There are {removed_rows} rows that do not contain source information. They have been removed.')
        return output_dataframe

    else:
        raise ValueError('Please specify the date column or source column.')


def _is_letter_in_date_format(date_format, date_pattern):
    # Check if any of the pattern elements is on the date_format string
    return any(any(element in character_to_check for element in date_pattern) for character_to_check in date_format)
