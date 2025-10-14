#!/usr/bin/env python3
"""
Test to verify how signals and scalars work when mixed in STL formulas.
"""

import numpy as np
from stgem.features import FeatureVector, Real, Signal
from stgem.monitor.stl import STLRobustness

def test_mixed_signals_scalars():
    """Test mixed signals and scalars in STL formulas."""
    
    print("Testing mixed signals and scalars in STL formulas...")
    
    # Test 1: Mixed FeatureVector with both signals and scalars
    print("\n1. Testing FeatureVector with mixed signals and scalars")
    
    fv = FeatureVector(features=[
        Signal(name="signal1", min_value=0, max_value=10),
        Real("scalar1", min_value=0, max_value=20),
        Real("scalar2", min_value=-5, max_value=15)
    ])
    
    # Set values: signal with time-varying data, scalars with constant values
    signal_data = np.array([
        [0, 1, 2, 3, 4, 5],      # timestamps
        [2, 4, 6, 8, 7, 5]       # signal values
    ])
    fv.set([signal_data, 10, 8])  # signal, scalar1=10, scalar2=8
    
    # Test formula mixing signal and scalars
    formula1 = "always[0,3] (signal1 > scalar2) and (scalar1 > 5)"
    monitor1 = STLRobustness(formula1)
    
    result1 = monitor1(fv, scale=False)
    print(f"Formula: {formula1}")
    print(f"Robustness (unscaled): {result1}")
    
    result1_scaled = monitor1(fv, scale=True)
    print(f"Robustness (scaled): {result1_scaled}")
    
    # Test 2: Dictionary with mixed signals and scalars
    print("\n2. Testing dictionary with mixed signals and scalars")
    
    d = {
        "sig": [[0, 1, 2, 3, 4], [1, 3, 5, 4, 2]],  # signal with timestamps and values
        "val1": 6,                                    # scalar
        "val2": 2                                     # scalar
    }
    
    formula2 = "always[0,2] (sig > val2) and (val1 > 4)"
    monitor2 = STLRobustness(formula2)
    
    result2 = monitor2(d, scale=False)
    print(f"Formula: {formula2}")
    print(f"Robustness: {result2}")
    
    # Test 3: More complex mixing
    print("\n3. Testing more complex mixed formula")
    
    formula3 = "eventually[0,3] (signal1 >= scalar1) or always[0,2] (signal1 < scalar2 + 2)"
    monitor3 = STLRobustness(formula3)
    
    result3 = monitor3(fv, scale=False)
    print(f"Formula: {formula3}")
    print(f"Robustness (unscaled): {result3}")
    
    # Test 4: Check what happens with scalar comparison to signals
    print("\n4. Testing scalar comparisons in temporal operators")
    
    formula4 = "always[0,4] (signal1 <= scalar1)"
    monitor4 = STLRobustness(formula4)
    
    result4 = monitor4(fv, scale=False)
    print(f"Formula: {formula4}")
    print(f"Robustness: {result4}")
    
    # Test 5: Multiple signals and scalars
    print("\n5. Testing multiple signals and scalars")
    
    fv2 = FeatureVector(features=[
        Signal(name="sig1", min_value=0, max_value=10),
        Signal(name="sig2", min_value=0, max_value=10),
        Real("const1", min_value=0, max_value=20),
        Real("const2", min_value=0, max_value=20)
    ])
    
    sig1_data = np.array([[0, 1, 2, 3], [2, 4, 6, 3]])
    sig2_data = np.array([[0, 1, 2, 3], [1, 2, 3, 5]])
    fv2.set([sig1_data, sig2_data, 5, 7])
    
    formula5 = "always[0,2] ((sig1 > const1) -> eventually[0,1] (sig2 < const2))"
    monitor5 = STLRobustness(formula5)
    
    result5 = monitor5(fv2, scale=False)
    print(f"Formula: {formula5}")
    print(f"Robustness: {result5}")

if __name__ == "__main__":
    test_mixed_signals_scalars()
