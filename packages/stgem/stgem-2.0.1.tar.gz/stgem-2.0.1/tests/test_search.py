import pandas as pd
import numpy as np
import pytest

from stgem.search import SearchSpace
from stgem.features import FeatureVector, Real, RealVector
from stgem.rng import RandomNumberGenerator


def test_search_space_creation():
    """Test SearchSpace creation with different parameters."""
    # Test with input_dimension
    ss1 = SearchSpace(input_dimension=3, output_dimension=2)
    assert ss1.input_dimension == 3
    assert ss1.output_dimension == 2
    assert ss1.recorded_inputs == 0
    
    # Test with input_vector
    ifv = FeatureVector(features=[Real('x1', -5, 5), Real('x2', 0, 10)])
    ss2 = SearchSpace(input_vector=ifv)
    assert ss2.input_dimension == 2
    assert ss2.output_dimension == 1  # default
    assert ss2.input_vector is not None
    
    # Test that we can't specify both
    with pytest.raises(AssertionError):
        SearchSpace(input_vector=ifv, input_dimension=2)


def test_record_normalized():
    """Test basic record_normalized functionality."""
    ss = SearchSpace(input_dimension=2, output_dimension=1)
    
    # Record some normalized data
    ss.record_normalized(np.array([-1.0, 0.5]), 0.3)
    ss.record_normalized(np.array([0.0, -0.8]), 0.9)
    
    assert ss.recorded_inputs == 2
    
    inputs = ss.known_inputs()
    outputs = ss.known_outputs()
    
    assert inputs.shape == (2, 2)
    assert outputs.shape == (2, 1)
    assert inputs[0, 0] == -1.0
    assert outputs[1, 0] == 0.9


def test_record_with_feature_vector():
    """Test record() method with FeatureVector."""
    ifv = FeatureVector(features=[Real('x', -10, 10)])
    ss = SearchSpace(input_vector=ifv)
    
    # Create a test input feature vector
    test_ifv = ss.new_ifv()
    test_ifv.x = 5.0  # This should be packed to 0.5: 2*((5-(-10))/(10-(-10)))-1 = 2*(15/20)-1 = 0.5
    
    ss.record(test_ifv, 0.7)
    
    assert ss.recorded_inputs == 1
    # The value 5.0 in range [-10, 10] should be packed to 0.5
    assert ss.known_inputs()[0, 0] == 0.5
    assert ss.known_outputs()[0, 0] == 0.7


def test_sampling():
    """Test input space sampling functionality."""
    ss = SearchSpace(input_dimension=3, output_dimension=1)
    
    # Sample from unconstrained space
    sample = ss.sample_input_space()
    assert len(sample) == 3
    assert np.all(sample >= -1.0) and np.all(sample <= 1.0)
    
    # Sample using FeatureVector method
    if ss.input_vector is None:
        # Create a simple input vector for testing
        ifv = FeatureVector(features=[Real(f'x{i}', -1, 1) for i in range(3)])
        ss.input_vector = ifv
        
    sample_fv = ss.sample_input_vector()
    assert isinstance(sample_fv, FeatureVector)


def test_constraint_validation():
    """Test constraint validation functionality."""
    def constraint(x):
        # Simple constraint: sum of inputs must be positive
        return np.sum(x) > 0
        
    ss = SearchSpace(input_dimension=2, constraint=constraint)
    
    # Test valid input
    valid_input = np.array([0.5, 0.5])
    assert ss.is_valid(valid_input) == True
    
    # Test invalid input
    invalid_input = np.array([-0.8, -0.8])
    assert ss.is_valid(invalid_input) == False
    
    # Test no constraint (default)
    ss_no_constraint = SearchSpace(input_dimension=2)
    assert ss_no_constraint.is_valid(np.array([0.5, 0.5])) == True
    assert ss_no_constraint.is_valid(np.array([-0.8, -0.8])) == True


def test_record_dataframe_basic():
    """Test basic record_dataframe functionality."""
    ss = SearchSpace(input_dimension=2, output_dimension=1)
    
    # Create normalized test data
    df = pd.DataFrame({
        'x1': [-1.0, 0.0, 1.0],
        'x2': [-0.5, 0.5, 0.0],
        'output': [0.1, 0.5, 0.9]
    })
    
    ss.record_dataframe(df)
    
    assert ss.recorded_inputs == 3
    expected_inputs = np.array([[-1.0, -0.5], [0.0, 0.5], [1.0, 0.0]])
    expected_outputs = np.array([[0.1], [0.5], [0.9]])
    
    np.testing.assert_array_equal(ss.known_inputs(), expected_inputs)
    np.testing.assert_array_equal(ss.known_outputs(), expected_outputs)


def test_record_dataframe_explicit_columns():
    """Test record_dataframe with explicit column specification."""
    ss = SearchSpace(input_dimension=2, output_dimension=1)
    
    df = pd.DataFrame({
        'feature_a': [-0.8, 0.3],
        'feature_b': [0.6, -0.9],
        'target': [0.2, 0.7],
        'ignore_me': [999, 888]
    })
    
    ss.record_dataframe(df, input_columns=['feature_a', 'feature_b'], output_columns=['target'])
    
    assert ss.recorded_inputs == 2
    expected_inputs = np.array([[-0.8, 0.6], [0.3, -0.9]])
    expected_outputs = np.array([[0.2], [0.7]])
    
    np.testing.assert_array_equal(ss.known_inputs(), expected_inputs)
    np.testing.assert_array_equal(ss.known_outputs(), expected_outputs)


def test_record_dataframe_validation():
    """Test record_dataframe input validation."""
    ss = SearchSpace(input_dimension=2, output_dimension=1)
    
    # Test dimension mismatch
    df_wrong_dims = pd.DataFrame({
        'x1': [0.0],
        'output': [0.5]  # Missing one input dimension
    })
    
    with pytest.raises(ValueError, match="DataFrame has 1 input columns, but search space expects 2"):
        ss.record_dataframe(df_wrong_dims)
    
    # Test range validation (inputs outside [-1, 1])
    df_bad_input = pd.DataFrame({
        'x1': [-1.5, 0.0],  # -1.5 is outside valid range
        'x2': [0.0, 0.5],
        'output': [0.3, 0.7]
    })
    
    with pytest.raises(AssertionError, match="Input data must be in range"):
        ss.record_dataframe(df_bad_input)
    
    # Test range validation (outputs outside [0, 1])
    df_bad_output = pd.DataFrame({
        'x1': [-0.5, 0.0],
        'x2': [0.0, 0.5],
        'output': [1.2, 0.7]  # 1.2 is outside valid range
    })
    
    with pytest.raises(AssertionError, match="Output data must be in range"):
        ss.record_dataframe(df_bad_output)


def test_rng_integration():
    """Test random number generator integration."""
    seed = 42
    rng = RandomNumberGenerator(seed=seed)
    ss = SearchSpace(input_dimension=2, rng=rng)
    
    # Test that we can get the RNG
    retrieved_rng = ss.get_rng("numpy")
    assert retrieved_rng is not None
    
    # Test reproducibility
    sample1 = ss.sample_input_space()
    
    # Reset RNG to same state
    rng2 = RandomNumberGenerator(seed=seed)
    ss2 = SearchSpace(input_dimension=2, rng=rng2)
    sample2 = ss2.sample_input_space()
    
    # Should be identical due to same seed
    np.testing.assert_array_equal(sample1, sample2)
