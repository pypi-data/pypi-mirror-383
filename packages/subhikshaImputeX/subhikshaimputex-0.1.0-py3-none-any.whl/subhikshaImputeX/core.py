"""
Main SmartImputer class for SubhikshaSmartImpute.

This module contains the core imputer class that orchestrates
strategy selection and imputation across all columns.
"""

from typing import Dict
import pandas as pd
from . import utils
from . import strategies as strat_module
from . import detector
from . import evaluator as eval_module


logger = utils.setup_logger(__name__)


class SmartImputer:
    """
    Automatically detects and applies the best imputation strategy per column.

    This imputer evaluates multiple strategies using cross-validation and
    selects the best performing method for each column independently.
    """

    def __init__(
        self,
        strategy: str = "auto",
        evaluation: bool = True,
        n_splits: int = 5,
        detect_correlations: bool = True,
        verbose: bool = True,
        random_state: int = 42,
    ):
        """
        Initialize SmartImputer.

        Args:
            strategy: 'auto' to auto-select per column, or specific strategy name
            evaluation: If True, evaluate strategies using cross-validation
            n_splits: Number of CV splits for evaluation
            detect_correlations: If True, detect feature correlations
            verbose: Print progress and results
            random_state: Random seed for reproducibility
        """
        self.strategy = strategy
        self.evaluation = evaluation
        self.n_splits = n_splits
        self.detect_correlations = detect_correlations
        self.verbose = verbose
        self.random_state = random_state
        self._is_fitted = False

        self.fitted_strategies = {}
        self.evaluation_scores = {}
        self.missing_columns = []
        self.correlations = None
        self.feature_importance = {}
        self.report = {}

        # Define supported strategies for different data types
        self.numeric_strategies = ["mean", "median", "knn", "regression"]
        self.categorical_strategies = ["mode", "forward_fill"]

    def fit(self, X: pd.DataFrame) -> "SmartImputer":
        """
        Fit imputation strategies on the data.

        Args:
            X: Training DataFrame with missing values

        Returns:
            Self for method chaining

        Raises:
            TypeError: If X is not a DataFrame
            ValueError: If X is empty or all NaN
        """
        utils.validate_dataframe(X)

        if self.verbose:
            logger.info(
                f"Fitting SmartImputer on {X.shape[0]} rows, {X.shape[1]} columns"
            )

        self.missing_columns = utils.get_missing_columns(X)
        missing_ratio = utils.get_missing_ratio(X)

        if self.verbose:
            logger.info(f"Columns with missing values: {len(self.missing_columns)}")
            for col in self.missing_columns:
                logger.info(f"  {col}: {missing_ratio[col]:.2%} missing")

        # Detect correlations if requested
        if self.detect_correlations:
            self._detect_correlations(X)

        # Fit strategy for each column with missing values
        evaluator = eval_module.StrategyEvaluator(
            n_splits=self.n_splits, random_state=self.random_state
        )

        for col in self.missing_columns:
            column_type = (
                "numeric" if utils.is_numeric_column(X[col]) else "categorical"
            )

            # Get features for regression/KNN
            X_features = self._get_features_for_column(X, col)

            if self.verbose:
                logger.info(f"Processing column: {col} ({column_type})")

            if self.evaluation and self.strategy == "auto":
                # Evaluate all strategies
                best_strategy_name, best_score, all_scores = (
                    evaluator.get_best_strategy(
                        X[col], column_type, X_features, verbose=self.verbose
                    )
                )

                self.evaluation_scores[col] = {
                    "best": best_strategy_name,
                    "score": best_score,
                    "all_scores": all_scores,
                }
            else:
                # Choose sensible default based on column type
                if self.strategy != "auto":
                    best_strategy_name = self.strategy
                else:
                    best_strategy_name = "mean" if column_type == "numeric" else "mode"

            # Fit the selected strategy
            strategy_instance = self._instantiate_strategy(best_strategy_name)
            strategy_instance.fit(X[col], X_features)
            self.fitted_strategies[col] = strategy_instance

        if self.verbose:
            logger.info("Fitting complete!")
        self._is_fitted = True

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply imputation to data.

        Args:
            X: DataFrame to impute (should have same columns as training data)

        Returns:
            DataFrame with imputed values

        Raises:
            ValueError: If not fitted yet
            TypeError: If X is not a DataFrame
        """
        # --- FIX START ---
        if not getattr(self, "_is_fitted", False):
            raise ValueError(
                "SmartImputer must be fitted before calling transform(). Please call fit() first."
            )
        # --- FIX END ---

        if not self.fitted_strategies:
            # If fit() was called but there were no missing values, just return the input
            if self.verbose:
                logger.info(
                    "No missing values detected during fit; returning original DataFrame."
                )
            return X.copy()

        utils.validate_dataframe(X)

        X_imputed = X.copy()

        for col in self.missing_columns:
            if col not in X.columns:
                logger.warning(f"Column {col} not found in data to impute. Skipping.")
                continue

            strategy = self.fitted_strategies[col]
            X_features = self._get_features_for_column(X, col)

            try:
                # Use transform method with optional X parameter
                X_imputed[col] = strategy.transform(X[col], X_features)

                if self.verbose:
                    n_filled = X[col].isna().sum()
                    if n_filled > 0:
                        logger.info(f"Imputed {n_filled} values in column '{col}'")

            except Exception as e:
                logger.error(f"Error imputing column {col}: {str(e)}")
                raise

        return X_imputed

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit imputer and apply imputation in one step.

        Args:
            X: DataFrame with missing values

        Returns:
            DataFrame with imputed values
        """
        self.fit(X)
        return self.transform(X)

    def _detect_correlations(self, X: pd.DataFrame) -> None:
        """Detect correlations between columns."""
        try:
            corr_detector = detector.CorrelationDetector(min_correlation=0.3)
            self.correlations = corr_detector.detect(X)

            if self.verbose and self.correlations:
                logger.info(f"Found correlations in {len(self.correlations)} columns")

        except Exception as e:
            logger.warning(f"Correlation detection failed: {str(e)}")

    def _get_features_for_column(self, X: pd.DataFrame, col: str) -> pd.DataFrame:
        """Get feature matrix for regression/KNN imputation."""
        if col not in X.columns:
            return pd.DataFrame()

        # For numeric columns, use all other numeric columns
        if utils.is_numeric_column(X[col]):
            numeric_cols = utils.get_numeric_columns(X)
            numeric_cols = [c for c in numeric_cols if c != col]
            if numeric_cols:
                return X[numeric_cols]

        return pd.DataFrame()

    def _instantiate_strategy(
        self, strategy_name: str
    ) -> strat_module.ImputationStrategy:
        """Create strategy instance by name."""
        if strategy_name == "mean":
            return strat_module.MeanImputer()
        elif strategy_name == "median":
            return strat_module.MedianImputer()
        elif strategy_name == "mode":
            return strat_module.ModeImputer()
        elif strategy_name == "forward_fill":
            return strat_module.ForwardFillImputer()
        elif strategy_name == "knn":
            return strat_module.KNNImputation()
        elif strategy_name == "regression":
            return strat_module.RegressionImputer()
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    def get_report(self) -> Dict:
        """
        Generate detailed report of imputation results.

        Returns:
            Dictionary containing imputation report
        """
        report = {"n_columns_with_missing": len(self.missing_columns), "columns": {}}

        for col in self.missing_columns:
            col_report = {}

            if col in self.fitted_strategies:
                strategy = self.fitted_strategies[col]
                col_report["strategy"] = strategy.strategy_name

            if col in self.evaluation_scores:
                scores = self.evaluation_scores[col]
                col_report["best_score"] = scores["score"]
                col_report["all_scores"] = scores["all_scores"]

            report["columns"][col] = col_report

        return report

    def print_report(self) -> None:
        """Print formatted imputation report."""
        report = self.get_report()

        print("\n" + "=" * 60)
        print("SMARTIMPUTER IMPUTATION REPORT")
        print("=" * 60)
        print(f"Columns with missing values: {report['n_columns_with_missing']}")
        print()

        for col, col_info in report["columns"].items():
            print(f"Column: {col}")
            print(f"  Strategy: {col_info.get('strategy', 'N/A')}")

            if "best_score" in col_info:
                print(f"  Score: {col_info['best_score']:.4f}")

            if "all_scores" in col_info:
                print("  All scores:")
                for strat, score in sorted(
                    col_info["all_scores"].items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"    {strat}: {score:.4f}")
            print()

        print("=" * 60)
