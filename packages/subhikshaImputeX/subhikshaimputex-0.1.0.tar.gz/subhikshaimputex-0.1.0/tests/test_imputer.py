"""
Unit tests for SubhikshaSmartImpute core functionality.

Run with: pytest tests/test_imputer.py -v
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subhikshaSmartImpute import (
    SmartImputer,
    MeanImputer,
    MedianImputer,
    ModeImputer,
    KNNImputation,
    RegressionImputer,
    ForwardFillImputer,
    CorrelationDetector,
    StrategyEvaluator
)
from subhikshaSmartImpute import utils


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def numeric_df_with_missing():
    """Create numeric DataFrame with missing values."""
    np.random.seed(42)
    return pd.DataFrame({
        'A': [1.0, 2.0, np.nan, 4.0, 5.0],
        'B': [10.0, np.nan, 30.0, 40.0, 50.0],
        'C': [100.0, 200.0, 300.0, 400.0, 500.0],
    })


@pytest.fixture
def categorical_df_with_missing():
    """Create categorical DataFrame with missing values."""
    return pd.DataFrame({
        'Color': ['Red', 'Blue', np.nan, 'Red', 'Green'],
        'Size': ['S', np.nan, 'L', 'M', 'S'],
    })


@pytest.fixture
def mixed_df_with_missing():
    """Create mixed type DataFrame."""
    np.random.seed(42)
    return pd.DataFrame({
        'Age': [25.0, np.nan, 35.0, 45.0, np.nan],
        'Salary': [50000.0, 60000.0, np.nan, 80000.0, 90000.0],
        'Department': ['Sales', 'IT', np.nan, 'HR', 'Sales'],
    })


# ============================================================================
# Test Utils
# ============================================================================

class TestUtils:
    """Test utility functions."""
    
    def test_validate_dataframe_valid(self, numeric_df_with_missing):
        """Test DataFrame validation with valid input."""
        utils.validate_dataframe(numeric_df_with_missing)  # Should not raise
    
    def test_validate_dataframe_not_dataframe(self):
        """Test DataFrame validation with non-DataFrame."""
        with pytest.raises(TypeError):
            utils.validate_dataframe([1, 2, 3])
    
    def test_validate_dataframe_empty(self):
        """Test DataFrame validation with empty DataFrame."""
        with pytest.raises(ValueError):
            utils.validate_dataframe(pd.DataFrame())
    
    def test_get_missing_columns(self, numeric_df_with_missing):
        """Test getting columns with missing values."""
        missing = utils.get_missing_columns(numeric_df_with_missing)
        assert set(missing) == {'A', 'B'}
    
    def test_get_missing_ratio(self, numeric_df_with_missing):
        """Test calculating missing ratios."""
        ratios = utils.get_missing_ratio(numeric_df_with_missing)
        assert ratios['A'] == 0.2
        assert ratios['B'] == 0.2
        assert ratios['C'] == 0.0
    
    def test_is_numeric_column(self):
        """Test numeric column detection."""
        series = pd.Series([1, 2, 3, np.nan])
        assert utils.is_numeric_column(series) is True
    
    def test_is_categorical_column(self):
        """Test categorical column detection."""
        series = pd.Series(['A', 'B', 'C', np.nan])
        assert utils.is_categorical_column(series) is True
    
    def test_check_sufficient_data(self):
        """Test sufficient data checking."""
        series = pd.Series([1, 2, np.nan, np.nan])
        assert utils.check_sufficient_data(series, min_non_null=2) is True
        assert utils.check_sufficient_data(series, min_non_null=10) is False


# ============================================================================
# Test Imputation Strategies
# ============================================================================

class TestImputationStrategies:
    """Test individual imputation strategies."""
    
    def test_mean_imputer_basic(self):
        """Test MeanImputer basic functionality."""
        series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        imputer = MeanImputer()
        imputer.fit(series)
        result = imputer.transform(series)
        
        assert result.isna().sum() == 0
        assert result[2] == 3.0  # Mean of [1, 2, 4, 5]
    
    def test_median_imputer_basic(self):
        """Test MedianImputer basic functionality."""
        series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        imputer = MedianImputer()
        imputer.fit(series)
        result = imputer.transform(series)
        
        assert result.isna().sum() == 0
        assert result[2] == 3.0  # Median of [1, 2, 4, 5]
    
    def test_mode_imputer_basic(self):
        """Test ModeImputer basic functionality."""
        series = pd.Series(['A', 'B', 'A', np.nan, 'A'])
        imputer = ModeImputer()
        imputer.fit(series)
        result = imputer.transform(series)
        
        assert result.isna().sum() == 0
        assert result[3] == 'A'
    
    def test_forward_fill_imputer(self):
        """Test ForwardFillImputer."""
        series = pd.Series([1.0, 2.0, np.nan, 4.0, np.nan])
        imputer = ForwardFillImputer()
        imputer.fit(series)
        result = imputer.transform(series)
        
        assert result.isna().sum() == 0
        assert result[2] == 2.0  # Forward filled from previous
    
    def test_fit_transform(self):
        """Test fit_transform method."""
        series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        imputer = MeanImputer()
        result = imputer.fit_transform(series)
        
        assert result.isna().sum() == 0
        assert imputer.fitted is True
    
    def test_imputer_not_fitted_error(self):
        """Test error when transform before fit."""
        series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        imputer = MeanImputer()
        
        with pytest.raises(ValueError):
            imputer.transform(series)
    
    def test_insufficient_data_error(self):
        """Test error with insufficient data."""
        series = pd.Series([np.nan, np.nan])
        imputer = MeanImputer()
        
        with pytest.raises(ValueError):
            imputer.fit(series)


# ============================================================================
# Test SmartImputer
# ============================================================================

class TestSmartImputer:
    """Test main SmartImputer class."""
    
    def test_smartimputer_initialization(self):
        """Test SmartImputer initialization."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        assert imputer.strategy == 'auto'
        assert imputer.evaluation is False
        assert imputer.fitted_strategies == {}
    
    def test_smartimputer_fit(self, numeric_df_with_missing):
        """Test fitting SmartImputer."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        imputer.fit(numeric_df_with_missing)
        
        assert len(imputer.fitted_strategies) > 0
        assert 'A' in imputer.fitted_strategies
        assert 'B' in imputer.fitted_strategies
    
    def test_smartimputer_transform(self, numeric_df_with_missing):
        """Test transforming with SmartImputer."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        imputer.fit(numeric_df_with_missing)
        result = imputer.transform(numeric_df_with_missing)
        
        assert result.isna().sum().sum() == 0
        assert result.shape == numeric_df_with_missing.shape
    
    def test_smartimputer_fit_transform(self, numeric_df_with_missing):
        """Test fit_transform method."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        result = imputer.fit_transform(numeric_df_with_missing)
        
        assert result.isna().sum().sum() == 0
        assert result.shape == numeric_df_with_missing.shape
    
    def test_smartimputer_transform_before_fit(self, numeric_df_with_missing):
        """Test error when transform before fit."""
        imputer = SmartImputer(verbose=False)
        
        with pytest.raises(ValueError):
            imputer.transform(numeric_df_with_missing)
    
    def test_smartimputer_get_report(self, numeric_df_with_missing):
        """Test getting imputation report."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        imputer.fit(numeric_df_with_missing)
        report = imputer.get_report()
        
        assert 'n_columns_with_missing' in report
        assert 'columns' in report
        assert report['n_columns_with_missing'] == 2
    
    def test_smartimputer_with_specific_strategy(self, numeric_df_with_missing):
        """Test SmartImputer with specific strategy."""
        imputer = SmartImputer(strategy='mean', evaluation=False, verbose=False)
        result = imputer.fit_transform(numeric_df_with_missing)
        
        assert result.isna().sum().sum() == 0
    
    def test_smartimputer_mixed_types(self, mixed_df_with_missing):
        """Test SmartImputer with mixed data types."""
        imputer = SmartImputer(evaluation=False, verbose=False)
        result = imputer.fit_transform(mixed_df_with_missing)
        
        assert result.isna().sum().sum() == 0
        assert result['Department'].dtype == 'object'


# ============================================================================
# Test Correlation Detector
# ============================================================================

class TestCorrelationDetector:
    """Test correlation detection."""
    
    def test_correlation_detector_initialization(self):
        """Test CorrelationDetector initialization."""
        detector = CorrelationDetector(min_correlation=0.5)
        assert detector.min_correlation == 0.5
        assert detector.correlation_matrix is None
    
    def test_correlation_detector_detect(self, numeric_df_with_missing):
        """Test correlation detection."""
        detector = CorrelationDetector(min_correlation=0.3)
        correlations = detector.detect(numeric_df_with_missing)
        
        assert detector.correlation_matrix is not None
        assert isinstance(correlations, dict)
    
    def test_correlation_detector_get_correlation_pairs(self, numeric_df_with_missing):
        """Test getting correlation pairs."""
        detector = CorrelationDetector(min_correlation=0.3)
        detector.detect(numeric_df_with_missing)
        pairs = detector.get_correlation_pairs()
        
        assert isinstance(pairs, list)
    
    def test_correlation_detector_no_numeric_columns(self, categorical_df_with_missing):
        """Test error with no numeric columns."""
        detector = CorrelationDetector()
        
        with pytest.raises(ValueError):
            detector.detect(categorical_df_with_missing)


# ============================================================================
# Test Strategy Evaluator
# ============================================================================

class TestStrategyEvaluator:
    """Test strategy evaluation."""
    
    def test_evaluator_initialization(self):
        """Test StrategyEvaluator initialization."""
        evaluator = StrategyEvaluator(n_splits=5)
        assert evaluator.n_splits == 5
        assert evaluator.scores == {}
    
    def test_evaluator_evaluate_strategy(self):
        """Test evaluating a single strategy."""
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, np.nan, np.nan])
        evaluator = StrategyEvaluator(n_splits=2)
        imputer = MeanImputer()
        
        score = evaluator.evaluate_strategy(series, imputer, verbose=False)
        assert isinstance(score, float)
    
    def test_evaluator_get_best_strategy(self):
        """Test getting best strategy."""
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, np.nan, np.nan])
        evaluator = StrategyEvaluator(n_splits=2)
        
        best_strategy, score, all_scores = evaluator.get_best_strategy(
            series, 'numeric', verbose=False
        )
        
        assert isinstance(best_strategy, str)
        assert isinstance(score, float)
        assert isinstance(all_scores, dict)


# ============================================================================
# Test Integration
# ============================================================================

class TestIntegration:
    """Test end-to-end integration."""
    
    def test_full_workflow(self, mixed_df_with_missing):
        """Test complete imputation workflow."""
        # Create train/test split
        train = mixed_df_with_missing.iloc[:3]
        test = mixed_df_with_missing.iloc[3:]
        
        # Fit on train
        imputer = SmartImputer(evaluation=False, verbose=False)
        imputer.fit(train)
        
        # Transform both
        train_clean = imputer.transform(train)
        test_clean = imputer.transform(test)
        
        # Verify
        assert train_clean.isna().sum().sum() == 0
        assert test_clean.isna().sum().sum() == 0
    
    def test_reproducibility(self, numeric_df_with_missing):
        """Test reproducibility with random_state."""
        imputer1 = SmartImputer(random_state=42, evaluation=False, verbose=False)
        result1 = imputer1.fit_transform(numeric_df_with_missing.copy())
        
        imputer2 = SmartImputer(random_state=42, evaluation=False, verbose=False)
        result2 = imputer2.fit_transform(numeric_df_with_missing.copy())
        
        pd.testing.assert_frame_equal(result1, result2)
    
    def test_with_no_missing_values(self):
        """Test with DataFrame without missing values."""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        imputer = SmartImputer(verbose=False)
        imputer.fit(df)
        result = imputer.transform(df)
        
        pd.testing.assert_frame_equal(df, result)
# ============================================================================
# FIXES FOR FAILING TESTS
# ============================================================================

def test_check_sufficient_data_fix():
    """Fix: Use == instead of 'is' for numpy boolean comparison."""
    from subhikshaSmartImpute import utils
    series = pd.Series([1, 2, np.nan, np.nan])
    result = utils.check_sufficient_data(series, min_non_null=2)
    assert result == True  # Use == instead of is
    assert utils.check_sufficient_data(series, min_non_null=10) == False


def test_smartimputer_no_missing_values_fix():
    """Fix: Handle case where DataFrame has no missing values."""
    from subhikshaSmartImpute import SmartImputer
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    imputer = SmartImputer(verbose=False)
    imputer.fit(df)
    # Should work even with empty fitted_strategies (no missing columns)
    result = imputer.transform(df)
    pd.testing.assert_frame_equal(df, result)


def test_smartimputer_categorical_handling_fix():
    """Fix: SmartImputer should use mode for categorical columns, not mean."""
    from subhikshaSmartImpute import SmartImputer
    df = pd.DataFrame({
        'Age': [25.0, np.nan, 35.0, 45.0],
        'Category': ['A', 'B', np.nan, 'A']
    })
    imputer = SmartImputer(evaluation=False, verbose=False)
    result = imputer.fit_transform(df)
    assert result.isna().sum().sum() == 0
    # Check that categorical was filled with mode (A)
    assert result['Category'].iloc[2] == 'A'


def test_transform_signature_fix():
    """Fix: All strategies now accept optional X parameter."""
    from subhikshaSmartImpute import MeanImputer
    series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
    imputer = MeanImputer()
    imputer.fit(series)
    
    # transform should accept X parameter (even if not used)
    result = imputer.transform(series, X=None)
    assert result.isna().sum() == 0


def test_forward_fill_deprecation_warning_fix():
    """Fix: Use ffill/bfill instead of deprecated fillna(method=...)."""
    from subhikshaSmartImpute import ForwardFillImputer
    series = pd.Series([1.0, 2.0, np.nan, 4.0, np.nan])
    imputer = ForwardFillImputer()
    imputer.fit(series)
    # Should work without FutureWarning
    result = imputer.transform(series)
    assert result.isna().sum() == 0
    assert result[2] == 2.0
    assert result[4] == 4.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])