"""
SubhikshaSmartImpute - Automatic Missing Value Imputation Library

A production-ready Python library that automatically detects and applies
the best missing value imputation method for each column in a dataset.

Key Features:
    - Auto per-column strategy selection
    - Multiple imputation methods (mean, median, KNN, regression, etc.)
    - Cross-validation based evaluation
    - Correlation detection
    - Transparent reporting

Example:
    >>> from subhikshasmartimpute import SmartImputer
    >>> imputer = SmartImputer(evaluation=True, verbose=True)
    >>> df_clean = imputer.fit_transform(df)
    >>> imputer.print_report()

Author: Subhiksha_Anandhan
License: MIT
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Subhiksha_Anandhan"
__license__ = "MIT"

from .core import SmartImputer
from .strategies import (
    ImputationStrategy,
    MeanImputer,
    MedianImputer,
    ModeImputer,
    ForwardFillImputer,
    KNNImputation,
    RegressionImputer,
    ConstantImputer,
    get_strategy_for_column,
)
from .detector import CorrelationDetector, get_features_for_regression
from .evaluator import StrategyEvaluator
from . import utils

__all__ = [
    "SmartImputer",
    "ImputationStrategy",
    "MeanImputer",
    "MedianImputer",
    "ModeImputer",
    "ForwardFillImputer",
    "KNNImputation",
    "RegressionImputer",
    "ConstantImputer",
    "CorrelationDetector",
    "StrategyEvaluator",
    "get_strategy_for_column",
    "get_features_for_regression",
    "utils",
]
