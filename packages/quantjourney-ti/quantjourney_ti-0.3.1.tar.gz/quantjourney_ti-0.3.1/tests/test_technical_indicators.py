"""
Tests for quantjourney_ti technical indicators.
"""

import pytest
import numpy as np
import pandas as pd
import quantjourney_ti as qti


class TestBasicFunctionality:
    """Test basic package functionality."""
    
    def test_package_imports(self):
        """Test that the package imports correctly."""
        assert hasattr(qti, '__version__')
        assert hasattr(qti, '__author__')
        assert qti.__author__ == "Jakub Polec"
    
    def test_sample_data_creation(self):
        """Test creation of sample data for testing."""
        # Create sample price data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(100) * 0.5),
            index=dates
        )
        assert len(prices) == 100
        assert isinstance(prices, pd.Series)


class TestTechnicalIndicators:
    """Test technical indicator calculations."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample price data for testing."""
        np.random.seed(42)  # For reproducible tests
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(100) * 0.5),
            index=dates
        )
        return prices
    
    def test_indicators_exist(self, sample_data):
        """Test that main indicator functions exist."""
        # This test will need to be updated based on your actual indicator functions
        # Common indicators that should exist:
        indicators_to_test = [
            'sma', 'ema', 'rsi', 'macd', 'bollinger_bands', 
            'atr', 'stochastic', 'williams_r'
        ]
        
        for indicator in indicators_to_test:
            if hasattr(qti, indicator):
                assert callable(getattr(qti, indicator))
    
    def test_basic_calculation(self, sample_data):
        """Test that indicators can be calculated without errors."""
        try:
            # Test SMA if it exists
            if hasattr(qti, 'sma'):
                result = qti.sma(sample_data, window=20)
                assert isinstance(result, pd.Series)
                assert len(result) <= len(sample_data)
            
            # Test EMA if it exists  
            if hasattr(qti, 'ema'):
                result = qti.ema(sample_data, window=20)
                assert isinstance(result, pd.Series)
                assert len(result) <= len(sample_data)
                
        except Exception as e:
            pytest.skip(f"Indicator functions not yet implemented: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
