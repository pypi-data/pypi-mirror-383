"""
Imputation strategy evaluator for SubhikshaSmartImpute.

This module evaluates imputation strategies using cross-validation
on known values to select the best performing method.
"""

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from . import utils
from . import strategies as strat_module


class StrategyEvaluator:
    """Evaluate imputation strategies using cross-validation."""

    def __init__(
        self,
        n_splits: int = 5,
        test_size: float = 0.2,
        random_state: int = 42,
        metric: str = "rmse",
    ):
        """
        Initialize evaluator.

        Args:
            n_splits: Number of cross-validation splits
            test_size: Proportion of values to hide for evaluation
            random_state: Random seed for reproducibility
            metric: Evaluation metric ('rmse' for numeric, 'accuracy' for categorical)
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.random_state = random_state
        self.metric = metric
        self.scores = {}

    def evaluate_strategy(
        self,
        series: pd.Series,
        strategy: strat_module.ImputationStrategy,
        X: Optional[pd.DataFrame] = None,
        verbose: bool = False,
    ) -> float:
        """
        Evaluate a single strategy using cross-validation.

        Args:
            series: Series to evaluate (must be numeric or categorical)
            strategy: Imputation strategy to test
            X: Optional feature matrix for regression/KNN
            verbose: Print evaluation details

        Returns:
            Average score across splits (higher is better)

        Raises:
            ValueError: If insufficient data or invalid strategy
        """
        if not utils.check_sufficient_data(series, min_non_null=5):
            raise ValueError("Insufficient non-null values for evaluation")

        column_type = "numeric" if utils.is_numeric_column(series) else "categorical"
        scores = []

        for split in range(self.n_splits):
            try:
                score = self._evaluate_single_split(
                    series, strategy, X, column_type, split
                )
                scores.append(score)
            except Exception as e:
                if verbose:
                    print(
                        f"Warning: Split {split} failed for {strategy.strategy_name}: {str(e)}"
                    )
                continue

        if len(scores) == 0:
            return 0.0

        avg_score = np.mean(scores)

        if verbose:
            print(
                f"{strategy.strategy_name}: {avg_score:.4f} (avg across {len(scores)} splits)"
            )

        return avg_score

    def _evaluate_single_split(
        self,
        series: pd.Series,
        strategy: strat_module.ImputationStrategy,
        X: Optional[pd.DataFrame] = None,
        column_type: str = "numeric",
        split: int = 0,
    ) -> float:
        """
        Evaluate strategy on a single split.

        Args:
            series: Target series
            strategy: Strategy to evaluate
            X: Optional feature matrix
            column_type: 'numeric' or 'categorical'
            split: Split number (for random seed)

        Returns:
            Score for this split
        """
        # Get non-null indices
        non_null_mask = series.notna()
        non_null_indices = np.where(non_null_mask)[0]

        if len(non_null_indices) < 5:
            raise ValueError("Insufficient non-null values")

        # Randomly select test indices to mask
        np.random.seed(self.random_state + split)
        n_test = max(1, int(len(non_null_indices) * self.test_size))
        test_idx_positions = np.random.choice(
            len(non_null_indices), n_test, replace=False
        )
        test_indices = non_null_indices[test_idx_positions]

        # Create series with masked values
        series_masked = series.copy()
        true_values = series.loc[test_indices].values
        series_masked.loc[test_indices] = np.nan

        # Prepare feature matrix if needed
        X_masked = None
        if X is not None:
            X_masked = X.copy()

        try:
            # Fit and transform
            strategy_copy = self._copy_strategy(strategy)
            strategy_copy.fit(series_masked, X_masked)
            imputed = strategy_copy.transform(series_masked)

            # Calculate score
            predicted_values = imputed.loc[test_indices].values

            if column_type == "numeric":
                score = self._calculate_rmse(true_values, predicted_values)
            else:
                score = self._calculate_accuracy(true_values, predicted_values)

            return score

        except Exception as e:
            raise ValueError(f"Strategy evaluation failed: {str(e)}")

    def _copy_strategy(
        self, strategy: strat_module.ImputationStrategy
    ) -> strat_module.ImputationStrategy:
        """Create a copy of strategy for safe evaluation."""
        strategy_name = strategy.strategy_name

        if strategy_name == "mean":
            return strat_module.MeanImputer()
        elif strategy_name == "median":
            return strat_module.MedianImputer()
        elif strategy_name == "mode":
            return strat_module.ModeImputer()
        elif strategy_name == "forward_fill":
            return strat_module.ForwardFillImputer()
        elif strategy_name == "knn":
            return strat_module.KNNImputation(n_neighbors=5)
        elif strategy_name == "regression":
            return strat_module.RegressionImputer()
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    def _calculate_rmse(self, true_vals: np.ndarray, pred_vals: np.ndarray) -> float:
        """
        Calculate RMSE (inverted so higher is better).

        Args:
            true_vals: True values
            pred_vals: Predicted values

        Returns:
            Negative RMSE (so higher score = better imputation)
        """
        rmse = np.sqrt(np.mean((true_vals - pred_vals) ** 2))
        return -rmse  # Negative so higher score is better

    def _calculate_accuracy(
        self, true_vals: np.ndarray, pred_vals: np.ndarray
    ) -> float:
        """
        Calculate accuracy for categorical values.

        Args:
            true_vals: True values
            pred_vals: Predicted values

        Returns:
            Accuracy score (0 to 1, higher is better)
        """
        return np.mean(true_vals == pred_vals)

    def evaluate_all_strategies(
        self,
        series: pd.Series,
        column_type: str,
        X: Optional[pd.DataFrame] = None,
        verbose: bool = True,
    ) -> Dict[str, float]:
        """
        Evaluate all applicable strategies for a column.

        Args:
            series: Series to evaluate
            column_type: 'numeric' or 'categorical'
            X: Optional feature matrix
            verbose: Print results

        Returns:
            Dictionary mapping strategy names to scores
        """
        strategies = strat_module.get_strategy_for_column(column_type)
        results = {}

        for strategy in strategies:
            try:
                score = self.evaluate_strategy(series, strategy, X, verbose)
                results[strategy.strategy_name] = score
            except Exception as e:
                if verbose:
                    print(f"Failed to evaluate {strategy.strategy_name}: {str(e)}")
                results[strategy.strategy_name] = -np.inf

        return results

    def get_best_strategy(
        self,
        series: pd.Series,
        column_type: str,
        X: Optional[pd.DataFrame] = None,
        verbose: bool = True,
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Find best imputation strategy for a series.

        Args:
            series: Series to evaluate
            column_type: 'numeric' or 'categorical'
            X: Optional feature matrix
            verbose: Print results

        Returns:
            Tuple of (best_strategy_name, best_score, all_scores_dict)
        """
        all_scores = self.evaluate_all_strategies(series, column_type, X, verbose)

        best_strategy = max(all_scores.keys(), key=lambda k: all_scores[k])
        best_score = all_scores[best_strategy]

        if verbose:
            print(f"\nBest strategy: {best_strategy} (score: {best_score:.4f})")

        return best_strategy, best_score, all_scores
