"""
Correlation detection for SubhikshaSmartImpute.

This module detects correlations between columns to optimize
imputation and provide insights on data relationships.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from . import utils


class CorrelationDetector:
    """Detect correlations between columns in a dataset."""

    def __init__(self, min_correlation: float = 0.5, method: str = "pearson"):
        """
        Initialize correlation detector.

        Args:
            min_correlation: Minimum correlation threshold (default: 0.5)
            method: Correlation method - 'pearson', 'spearman', or 'kendall'
        """
        self.min_correlation = min_correlation
        self.method = method
        self.correlation_matrix = None
        self.strong_correlations = None

    def detect(self, df: pd.DataFrame) -> Dict[str, List[Tuple[str, float]]]:
        """
        Detect strong correlations in dataframe.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary mapping column names to list of (correlated_column, correlation_value)

        Raises:
            ValueError: If no numeric columns
        """
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            raise ValueError("No numeric columns found for correlation detection")

        # Calculate correlation matrix
        self.correlation_matrix = numeric_df.corr(method=self.method)

        # Find strong correlations
        self.strong_correlations = {}

        for col in self.correlation_matrix.columns:
            correlations = self.correlation_matrix[col]

            # Get correlations above threshold (excluding self-correlation)
            strong = correlations[
                (correlations.abs() >= self.min_correlation) & (correlations.abs() < 1.0)
            ].sort_values(ascending=False)

            if len(strong) > 0:
                self.strong_correlations[col] = [
                    (idx, float(val)) for idx, val in strong.items()
                ]

        return self.strong_correlations

    def get_correlated_features(
        self, column: str, top_n: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top N most correlated features for a column.

        Args:
            column: Column name
            top_n: Number of top correlations to return

        Returns:
            List of (column_name, correlation_value) tuples, sorted by correlation strength

        Raises:
            ValueError: If column not found or correlations not detected
        """
        if self.strong_correlations is None:
            raise ValueError("Call detect() first to find correlations")

        if column not in self.strong_correlations:
            return []

        return self.strong_correlations[column][:top_n]

    def get_correlation_pairs(self) -> List[Tuple[str, str, float]]:
        """
        Get all correlation pairs (avoiding duplicates).

        Returns:
            List of (column1, column2, correlation_value) tuples
        """
        if self.correlation_matrix is None:
            raise ValueError("Call detect() first to find correlations")

        pairs = []
        cols = self.correlation_matrix.columns

        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                corr_val = self.correlation_matrix.iloc[i, j]
                if abs(corr_val) >= self.min_correlation:
                    pairs.append((cols[i], cols[j], float(corr_val)))

        return sorted(pairs, key=lambda x: abs(x[2]), reverse=True)

    def get_feature_importance_for_imputation(
        self, column: str, df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get ranking of features by correlation strength for imputation.
        Useful for regression/KNN-based imputation.

        Args:
            column: Target column to impute
            df: Original DataFrame

        Returns:
            DataFrame with columns [feature, correlation, missing_ratio]
        """
        if self.strong_correlations is None:
            raise ValueError("Call detect() first to find correlations")

        if column not in self.correlation_matrix.columns:
            raise ValueError(f"Column '{column}' not found in numeric columns")

        correlations = self.correlation_matrix[column]
        missing_ratios = utils.get_missing_ratio(df)

        features = []
        for feat in correlations.index:
            if feat != column:
                features.append(
                    {
                        "feature": feat,
                        "correlation": abs(correlations[feat]),
                        "missing_ratio": missing_ratios.get(feat, 0.0),
                    }
                )

        result_df = pd.DataFrame(features)
        return result_df.sort_values("correlation", ascending=False).reset_index(
            drop=True
        )

    def is_highly_correlated(self, col1: str, col2: str) -> bool:
        """
        Check if two columns are highly correlated.

        Args:
            col1: First column
            col2: Second column

        Returns:
            True if correlation >= min_correlation threshold
        """
        if self.correlation_matrix is None:
            raise ValueError("Call detect() first")

        if (col1 not in self.correlation_matrix.columns or col2 not in self.correlation_matrix.columns):
            return False

        corr = abs(self.correlation_matrix.loc[col1, col2])
        return corr >= self.min_correlation

    def get_multicollinearity_warnings(self) -> Dict[str, List[str]]:
        """
        Identify multicollinearity issues (highly correlated features).

        Returns:
            Dictionary mapping column names to list of highly correlated columns
        """
        if self.correlation_matrix is None:
            raise ValueError("Call detect() first")

        warnings = {}
        cols = self.correlation_matrix.columns

        for col in cols:
            correlated = []
            for other_col in cols:
                if col != other_col:
                    corr = abs(self.correlation_matrix.loc[col, other_col])
                    if corr > 0.9:  # Very high correlation threshold
                        correlated.append(f"{other_col} ({corr:.3f})")

            if correlated:
                warnings[col] = correlated

        return warnings

    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (10, 8)) -> None:
        """
        Plot correlation heatmap (requires matplotlib).

        Args:
            figsize: Figure size as (width, height)
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            raise ImportError("matplotlib and seaborn required for plotting")

        if self.correlation_matrix is None:
            raise ValueError("Call detect() first")

        plt.figure(figsize=figsize)
        sns.heatmap(
            self.correlation_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            cbar_kws={"label": "Correlation"},
        )
        plt.title("Feature Correlation Matrix")
        plt.tight_layout()
        plt.show()


def get_features_for_regression(
    column: str,
    df: pd.DataFrame,
    detector: CorrelationDetector,
    max_features: int = 5,
    min_correlation: float = 0.3,
) -> List[str]:
    """
    Get best features for regression-based imputation.

    Args:
        column: Target column
        df: DataFrame
        detector: CorrelationDetector instance (must have run detect())
        max_features: Maximum features to return
        min_correlation: Minimum correlation threshold

    Returns:
        List of feature column names
    """
    if detector.correlation_matrix is None:
        raise ValueError("Detector must run detect() first")

    if column not in detector.correlation_matrix.columns:
        return []

    correlations = detector.correlation_matrix[column]

    # Get correlations above threshold, excluding self
    strong = (
        correlations[(correlations.abs() >= min_correlation) & (correlations != 1.0)]
        .abs()
        .sort_values(ascending=False)
    )

    # Exclude columns with too many missing values
    selected = []
    for feat in strong.head(max_features).index:
        missing_ratio = df[feat].isna().sum() / len(df)
        if missing_ratio < 0.5:  # Don't use features with >50% missing
            selected.append(feat)

    return selected
