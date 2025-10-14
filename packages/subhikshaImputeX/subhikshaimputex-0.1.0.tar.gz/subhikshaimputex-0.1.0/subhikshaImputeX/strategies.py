"""
Imputation strategies for SubhikshaSmartImpute.

This module contains various imputation methods that can be applied to
individual columns. Each strategy is optimized for specific data types.
"""

from typing import Union, Optional, List
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from . import utils


class ImputationStrategy:
    """Base class for imputation strategies."""

    def __init__(self, strategy_name: str):
        """
        Initialize strategy.

        Args:
            strategy_name: Name of the strategy
        """
        self.strategy_name = strategy_name
        self.fitted = False

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "ImputationStrategy":
        """
        Fit the strategy to data.

        Args:
            series: Target series with missing values
            X: Optional feature matrix for regression-based methods

        Returns:
            Self for chaining
        """
        raise NotImplementedError

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """
        Apply imputation to series.

        Args:
            series: Series with missing values
            X: Optional feature matrix (ignored for simple strategies)

        Returns:
            Series with imputed values
        """
        raise NotImplementedError

    def fit_transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """
        Fit and transform in one step.

        Args:
            series: Series with missing values
            X: Optional feature matrix

        Returns:
            Imputed series
        """
        self.fit(series, X)
        return self.transform(series, X)


class MeanImputer(ImputationStrategy):
    """Impute missing values with column mean."""

    def __init__(self):
        super().__init__("mean")
        self.fill_value = None

    def fit(self, series: pd.Series, X: Optional[pd.DataFrame] = None) -> "MeanImputer":
        """Calculate mean from non-null values."""
        if not utils.check_sufficient_data(series):
            raise ValueError(f"Insufficient data to fit {self.strategy_name} imputer")

        self.fill_value = series.mean()
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Fill NaN with mean."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")
        return utils.safe_fillna(series, self.fill_value)


class MedianImputer(ImputationStrategy):
    """Impute missing values with column median."""

    def __init__(self):
        super().__init__("median")
        self.fill_value = None

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "MedianImputer":
        """Calculate median from non-null values."""
        if not utils.check_sufficient_data(series):
            raise ValueError(f"Insufficient data to fit {self.strategy_name} imputer")

        self.fill_value = series.median()
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Fill NaN with median."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")
        return utils.safe_fillna(series, self.fill_value)


class ModeImputer(ImputationStrategy):
    """Impute missing values with column mode (most frequent)."""

    def __init__(self):
        super().__init__("mode")
        self.fill_value = None

    def fit(self, series: pd.Series, X: Optional[pd.DataFrame] = None) -> "ModeImputer":
        """Calculate mode from non-null values."""
        if not utils.check_sufficient_data(series):
            raise ValueError(f"Insufficient data to fit {self.strategy_name} imputer")

        mode_result = series.mode()
        if len(mode_result) == 0:
            raise ValueError("Cannot calculate mode for this series")

        self.fill_value = mode_result[0]
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Fill NaN with mode."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")
        return utils.safe_fillna(series, self.fill_value)


class ForwardFillImputer(ImputationStrategy):
    """Impute missing values using forward fill (last observation carried forward)."""

    def __init__(self):
        super().__init__("forward_fill")

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "ForwardFillImputer":
        """No fitting required for forward fill."""
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Apply forward fill."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")
        result = series.ffill()
        result = result.bfill()
        return result


class KNNImputation(ImputationStrategy):
    """Impute missing values using K-Nearest Neighbors."""

    def __init__(self, n_neighbors: int = 5):
        super().__init__("knn")
        self.n_neighbors = n_neighbors
        self.imputer = KNNImputer(n_neighbors=n_neighbors)

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "KNNImputation":
        """Fit KNN imputer using feature matrix."""
        if X is None or len(X) == 0:
            raise ValueError("KNN imputation requires feature matrix X")

        X_with_target = X.copy()
        X_with_target["target"] = series

        self.imputer.fit(X_with_target)
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Apply KNN imputation."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")

        if X is None or len(X) == 0:
            raise ValueError("KNN transform requires feature matrix X")

        X_with_target = X.copy()
        X_with_target["target"] = series

        result = self.imputer.transform(X_with_target)
        return pd.Series(result[:, -1], index=series.index)


class RegressionImputer(ImputationStrategy):
    """Impute missing values using Linear Regression on other features."""

    def __init__(self):
        super().__init__("regression")
        self.model = LinearRegression()
        self.predictors = None

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "RegressionImputer":
        """Fit regression model using non-null values."""
        if X is None or len(X) == 0:
            raise ValueError("Regression imputation requires feature matrix X")

        # Get rows where target is not null
        mask = series.notna()
        if mask.sum() < 2:
            raise ValueError("Insufficient non-null values for regression imputation")

        X_train = X.loc[mask].values
        y_train = series.loc[mask].values

        self.model.fit(X_train, y_train)
        self.predictors = X
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Apply regression imputation."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")

        result = series.copy()
        mask = result.isna()

        if mask.any() and X is not None:
            X_missing = X.loc[mask].values
            predicted = self.model.predict(X_missing)
            result.loc[mask] = predicted

        return result


class ConstantImputer(ImputationStrategy):
    """Impute missing values with a constant value."""

    def __init__(self, value: Union[int, float, str]):
        super().__init__("constant")
        self.fill_value = value

        if pd.isna(value):
            raise ValueError("Constant value cannot be NaN")

    def fit(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> "ConstantImputer":
        """No fitting required for constant imputation."""
        self.fitted = True
        return self

    def transform(
        self, series: pd.Series, X: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Fill NaN with constant."""
        if not self.fitted:
            raise ValueError("Imputer not fitted. Call fit() first.")
        return utils.safe_fillna(series, self.fill_value)


def get_strategy_for_column(
    column_type: str, strategy: str = "auto"
) -> List[ImputationStrategy]:
    """
    Get list of strategies suitable for a column type.

    Args:
        column_type: 'numeric' or 'categorical'
        strategy: 'auto' returns all applicable, or specific strategy name

    Returns:
        List of strategy instances

    Raises:
        ValueError: If invalid column_type or strategy
    """
    numeric_strategies = [
        MeanImputer(),
        MedianImputer(),
        ForwardFillImputer(),
        KNNImputation(),
        RegressionImputer(),
    ]

    categorical_strategies = [
        ModeImputer(),
        ForwardFillImputer(),
        KNNImputation(),
    ]

    if column_type == "numeric":
        strategies = numeric_strategies
    elif column_type == "categorical":
        strategies = categorical_strategies
    else:
        raise ValueError(f"Invalid column_type: {column_type}")

    if strategy == "auto":
        return strategies
    else:
        for s in strategies:
            if s.strategy_name == strategy:
                return [s]
        raise ValueError(
            f"Strategy '{strategy}' not available for {column_type} columns"
        )
