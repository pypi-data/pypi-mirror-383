import traceback

from stgem.features import *
from stgem.sut import as_SystemUnderTest
import numpy as np


def test_annotation_failure():
    # Test some failures in annotation.

    def f(x, y) -> Signal(name="o", min_value=0, max_value=20):
        return np.array(x) * 2

    try:
        sut = as_SystemUnderTest(f)
    except Exception as E:
        if E.args[0] != "No annotation for all input values.":
            traceback.print_exc()
            raise

    def f(x: PiecewiseConstantSignal(piece_durations=[6] * 5, min_value=0, max_value=10)):
        return np.array(x) * 2

    try:
        sut = as_SystemUnderTest(f)
    except Exception as E:
        if E.args[0] != "No annotation specified for the return value.":
            traceback.print_exc()
            raise


def test_1():
    # Test that a wrapped Python function does what is expected.

    def f(x: PiecewiseConstantSignal(piece_durations=[6] * 5, min_value=0, max_value=10)) \
            -> FeatureVector(features=[
                RealVector(name="y", dimension=5, min_value=0, max_value=20),
                Real(name="z", min_value=0, max_value=5 * 20)
            ]):
        return np.array(x) * 2, np.sum(x)

    sut = as_SystemUnderTest(f)

    ifv = sut.new_ifv()
    ifv.set_packed([-1, -1, 0, 0, 1])

    ofv, _ = sut.execute_test_fv(ifv)
    assert np.all(ofv["y"] == np.array([0.0, 0.0, 5.0, 5.0, 10.0]) * 2)
    assert ofv["z"] == np.sum(np.array([0.0, 0.0, 5.0, 5.0, 10.0]))


def test_2():
    # Another test that tests the case when the output is a single real.

    def f(x: Real(min_value=0, max_value=10)) -> FeatureVector(features=[Real(name="o", min_value=0, max_value=20)]):
        return x * 2

    sut = as_SystemUnderTest(f)

    ifv = sut.new_ifv()
    ifv.set_packed([0.0])

    ofv, _ = sut.execute_test_fv(ifv)
    assert ofv["o"] == 10.0


def test_3():
    # Test that a function can accept a list input with RealVector

    def f(x: RealVector(dimension=3, min_value=0, max_value=10)) -> FeatureVector(features=[
        Real(name="sum", min_value=0, max_value=30),
        Real(name="product", min_value=0, max_value=1000)
    ]):
        return np.sum(x), np.prod(x)

    sut = as_SystemUnderTest(f)

    ifv = sut.new_ifv()
    ifv.set_packed([0.0, 0.5, 1.0])  # Should map to [5.0, 7.5, 10.0] after unpacking

    ofv, _ = sut.execute_test_fv(ifv)
    # Check that the sum and product are calculated correctly
    assert ofv["sum"] == 22.5  # 5.0 + 7.5 + 10.0
    assert ofv["product"] == 375.0  # 5.0 * 7.5 * 10.0


def test_4():
    # Test what happens when argument name is different from the feature name
    # The feature name should be set to match the argument name

    def f(input_param: Real(name="original_name", min_value=0, max_value=10)) -> FeatureVector(features=[
        Real(name="output", min_value=0, max_value=20)
    ]):
        return input_param * 2

    sut = as_SystemUnderTest(f)

    # Check that the input feature name was changed to match the argument name
    assert sut.input_features[0]._name == "input_param"
    
    ifv = sut.new_ifv()
    # Access by the argument name, not the original feature name
    assert "input_param" in ifv
    
    ifv.set_packed([0.5])
    ofv, _ = sut.execute_test_fv(ifv)
    assert ofv["output"] == 15.0


def test_5():
    # Test multiple list inputs with different dimensions

    def f(
        x: RealVector(dimension=2, min_value=0, max_value=5), 
        y: RealVector(dimension=3, min_value=-1, max_value=1)
    ) -> FeatureVector(features=[
        Real(name="x_sum", min_value=0, max_value=10),
        Real(name="y_sum", min_value=-3, max_value=3)
    ]):
        return np.sum(x), np.sum(y)

    sut = as_SystemUnderTest(f)

    ifv = sut.new_ifv()
    # 5 total dimensions: 2 for x, 3 for y
    ifv.set_packed([0.0, 1.0, -1.0, 0.0, 1.0])

    ofv, _ = sut.execute_test_fv(ifv)
    # x should be [2.5, 5.0], y should be [-1.0, 0.0, 1.0]
    assert ofv["x_sum"] == 7.5
    assert ofv["y_sum"] == 0.0
