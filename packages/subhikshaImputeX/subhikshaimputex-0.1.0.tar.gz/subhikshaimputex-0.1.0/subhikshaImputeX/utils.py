"""
Utility functions for SubhikshaSmartImpute.

This module provides helper functions for validation, data preprocessing,
and logging that are used across the library.
"""

import logging
from typing import Tuple, List, Union
import numpy as np
import pandas as pd


# Configure logging
logger = logging.getLogger(__name__)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure logger for the library.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    log = logging.getLogger(name)
    log.setLevel(level)

    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate that input is a proper pandas DataFrame.

    Args:
        df: DataFrame to validate

    Raises:
        TypeError: If not a DataFrame
        ValueError: If DataFrame is empty or all NaN
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pd.DataFrame, got {type(df).__name__}")

    if df.empty:
        raise ValueError("DataFrame is empty")

    if df.isna().all().all():
        raise ValueError("DataFrame contains all NaN values")


def get_missing_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of columns with missing values.

    Args:
        df: Input DataFrame

    Returns:
        List of column names with at least one NaN value
    """
    return df.columns[df.isna().any()].tolist()


def get_missing_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Calculate missing value ratio for each column.

    Args:
        df: Input DataFrame

    Returns:
        Series with column names as index and missing ratios as values
    """
    return df.isna().sum() / len(df)


def is_numeric_column(series: pd.Series) -> bool:
    """
    Check if a Series contains numeric data.

    Args:
        series: Pandas Series to check

    Returns:
        True if numeric, False otherwise
    """
    return pd.api.types.is_numeric_dtype(series)


def is_categorical_column(series: pd.Series) -> bool:
    """
    Check if a Series contains categorical data.

    Args:
        series: Pandas Series to check

    Returns:
        True if categorical, False otherwise
    """
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(
        series
    )


def validate_column_type(series: pd.Series, expected_type: str) -> bool:
    """
    Validate that a column is of expected type (numeric or categorical).

    Args:
        series: Pandas Series to validate
        expected_type: 'numeric' or 'categorical'

    Returns:
        True if type matches, False otherwise

    Raises:
        ValueError: If invalid expected_type
    """
    if expected_type == "numeric":
        return is_numeric_column(series)
    elif expected_type == "categorical":
        return is_categorical_column(series)
    else:
        raise ValueError(
            f"expected_type must be 'numeric' or 'categorical', got {expected_type}"
        )


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of numeric columns.

    Args:
        df: Input DataFrame

    Returns:
        List of numeric column names
    """
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of categorical columns.

    Args:
        df: Input DataFrame

    Returns:
        List of categorical column names
    """
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def safe_fillna(series: pd.Series, value: Union[int, float, str]) -> pd.Series:
    """
    Safely fill NaN values, handling edge cases.

    Args:
        series: Series to fill
        value: Value to fill with

    Returns:
        Series with NaN values filled

    Raises:
        ValueError: If value is NaN
    """
    if pd.isna(value):
        raise ValueError("Cannot fill with NaN value")

    return series.fillna(value)


def check_sufficient_data(series: pd.Series, min_non_null: int = 2) -> bool:
    """
    Check if series has enough non-null values for imputation.

    Args:
        series: Series to check
        min_non_null: Minimum required non-null values (default: 2)

    Returns:
        True if sufficient data, False otherwise
    """
    return bool(series.notna().sum() >= min_non_null)


def get_indices_train_test_split(
    n_samples: int, test_size: float = 0.2, random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get train/test split indices for cross-validation.

    Args:
        n_samples: Total number of samples
        test_size: Proportion of test set (default: 0.2)
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (train_indices, test_indices)
    """
    np.random.seed(random_state)
    indices = np.arange(n_samples)
    np.random.shuffle(indices)

    split_idx = int(n_samples * (1 - test_size))
    return indices[:split_idx], indices[split_idx:]


def handle_infinite_values(series: pd.Series) -> pd.Series:
    """
    Replace infinite values with NaN.

    Args:
        series: Series to process

    Returns:
        Series with infinite values replaced by NaN
    """
    return series.replace([np.inf, -np.inf], np.nan)


def clip_outliers(
    series: pd.Series, lower: float = 0.01, upper: float = 0.99
) -> pd.Series:
    """
    Clip outliers using quantile-based method.

    Args:
        series: Numeric series to process
        lower: Lower quantile threshold (default: 0.01)
        upper: Upper quantile threshold (default: 0.99)

    Returns:
        Series with outliers clipped
    """
    if not is_numeric_column(series):
        return series

    q_lower = series.quantile(lower)
    q_upper = series.quantile(upper)
    return series.clip(lower=q_lower, upper=q_upper)


def format_report_dict(data: dict, indent: int = 0) -> str:
    """
    Format dictionary for readable console output.

    Args:
        data: Dictionary to format
        indent: Indentation level (default: 0)

    Returns:
        Formatted string representation
    """
    output = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            output.append(f"{prefix}{key}:")
            output.append(format_report_dict(value, indent + 1))
        elif isinstance(value, float):
            output.append(f"{prefix}{key}: {value:.4f}")
        else:
            output.append(f"{prefix}{key}: {value}")

    return "\n".join(output)
