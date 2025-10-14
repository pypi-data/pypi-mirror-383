from typing import Union

import numpy as np
import pandas as pd

from stgem.features import FeatureVector
from stgem.rng import RandomNumberGenerator


class SearchSpace:
    """
    Represents an n-dimensional search space
    Every input (decision variable) is normalized in the interval [-1,1]
    The output (objective) is normalized in the interval [0,1]"""

    def __init__(self,  # pylint: disable=too-many-positional-arguments,too-many-arguments
                 input_vector: FeatureVector = None,
                 input_dimension: int = 0,
                 output_dimension: int = 1,
                 constraint=None,
                 rng: RandomNumberGenerator = None):
        """
        Initializes the SearchSpace object.

        Parameters:
        input_vector (FeatureVector): The input feature vector.
        input_dimension (int): The dimension of the input space.
        output_dimension (int): The dimension of the output space.
        constraint (function): A function to constrain valid inputs.
        rng (RandomNumberGenerator): A random number generator.
        """

        assert not (input_vector and input_dimension > 0)

        if input_vector:
            input_dimension = input_vector.dimension

        self.input_vector = input_vector
        self.input_dimension = input_dimension
        self.I = np.empty((0, self.input_dimension))  # noqa: E741

        self.output_dimension = output_dimension
        self.O = np.empty((0, self.output_dimension))  # noqa: E741

        self.rng = rng if rng is not None else RandomNumberGenerator(seed=None)

        self.constraint = constraint
    
    def __deepcopy__(self, memo=None):
        # We never expect to have independent copies of exactly the same search
        # space.
        if memo is not None and id(self) in memo:
            return memo[id(self)]
        input_vector = self.input_vector
        input_dimension = self.input_dimension if input_vector is None else 0
        ss = SearchSpace(
            input_vector=input_vector,
            input_dimension=input_dimension,
            output_dimension=self.output_dimension,
            constraint=self.constraint,
            rng=self.rng
        )
        ss.I = np.copy(self.I)  # noqa: E741
        ss.O = np.copy(self.O)  # noqa: E741
        memo[id(self)] = ss
        return ss

    def get_rng(self, rng_id):
        return self.rng.get_rng(rng_id)

    def new_ifv(self):
        """
        Creates a new input feature vector with the same features as the current one.

        Returns:
        FeatureVector: A new feature vector with the same features.
        """
        assert self.input_vector, "Input vector is not defined"
        return self.input_vector(name=self.input_vector.name)

    def is_valid(self, input_array: np.array) -> bool:
        """
        Checks if a given input is valid according to the constraint function.

        Parameters:
        input_array (np.array): The input to check.

        Returns:
        bool: True if the input is valid, False otherwise.
        """
        # This is here until valid tests are changed to preconditions. This
        # line ensures that model-based SUTs work and can be pickled.
        if self.constraint is None:
            return True
        return self.constraint(input_array)

    def sample_input_vector(self, max_trials=10000) -> FeatureVector:
        ifv = self.new_ifv()
        ifv.set_packed(self.sample_input_space(max_trials))
        return ifv

    def sample_input_space(self, max_trials=10000) -> np.array:
        """
        Samples a valid input from the input space.

        Parameters:
        max_trials (int): The maximum number of trials to find a valid input.

        Returns:
        np.array: A valid input.

        Raises:
        Exception: If a valid input cannot be found within max_trials.
        """

        rng = self.rng.get_rng("numpy")
        for _ in range(max_trials):
            candidate = rng.uniform(-1, 1, size=self.input_dimension)
            if self.is_valid(candidate):
                return candidate

        raise RuntimeError("sample_input_space: max_trials exceeded")

    def record_normalized(self, input_array: np.array, output: Union[np.array, float]):
        """
        Records a normalized input-output pair.

        Parameters:
        input_array (np.array): The normalized input.
        output (Union[np.array, float]): The normalized output.
        
        Raises:
        AssertionError: If the inputs are not in the range [-1, 1] or outputs are not in the range [0, 1].
        """
        if __debug__:
            def _min(x):
                return min(x) if not np.isscalar(x) else x

            def _max(x):
                return max(x) if not np.isscalar(x) else x

            assert _min(input_array) >= -1 and _max(input_array) <= 1 and \
                   _min(output) >= 0 and _max(output <= 1)
        self.I = np.append(self.I, [input_array], axis=0)  # noqa: E741
        if np.isscalar(output):
            self.O = np.append(self.O, [[output]], axis=0)  # noqa: E741
        else:
            self.O = np.append(self.O, [output], axis=0)  # noqa: E741

    def record(self, ifv: FeatureVector, output: Union[np.array, float]):
        """
        Records an input-output pair by normalizing the input feature vector.

        Parameters:
        ifv (FeatureVector): The input feature vector.
        output (Union[np.array, float]): The output.
        """
        self.record_normalized(ifv.pack(), output)

    @property
    def recorded_inputs(self):
        return len(self.I)

    def known_inputs(self):
        """
        Returns the known inputs recorded so far.

        Returns:
        np.array: The recorded inputs.
        """
        return self.I

    def known_outputs(self):
        """
        Returns the known outputs recorded so far.

        Returns:
        np.array: The recorded outputs.
        """
        return self.O

    def _determine_dataframe_columns(self, df: pd.DataFrame, input_columns=None, output_columns=None):
        if input_columns is None and output_columns is None:
            total_cols = len(df.columns)
            input_columns = df.columns[:total_cols - self.output_dimension].tolist()
            output_columns = df.columns[total_cols - self.output_dimension:].tolist()
        elif input_columns is None:
            remaining_columns = [col for col in df.columns if col not in output_columns]
            if len(remaining_columns) < self.input_dimension:
                raise ValueError(f"After excluding output columns, only {len(remaining_columns)} columns remain, "
                               f"but search space expects {self.input_dimension} input columns")
            input_columns = remaining_columns[:self.input_dimension]
        elif output_columns is None:
            remaining_columns = [col for col in df.columns if col not in input_columns]
            if len(remaining_columns) < self.output_dimension:
                raise ValueError(f"After excluding input columns, only {len(remaining_columns)} columns remain, "
                               f"but search space expects {self.output_dimension} output columns")
            output_columns = remaining_columns[:self.output_dimension]
            
        return input_columns, output_columns

    def _validate_dataframe_data(self, input_data: np.array, output_data: np.array):
        if not __debug__:
            return
            
        def _min(x):
            return np.min(x) if not np.isscalar(x) else x

        def _max(x):
            return np.max(x) if not np.isscalar(x) else x
            
        if len(input_data) > 0:
            input_min = _min(input_data)
            input_max = _max(input_data)
            assert input_min >= -1.0 and input_max <= 1.0, \
                f"Input data must be in range [-1, 1], got [{input_min:.3f}, {input_max:.3f}]"
        
        if len(output_data) > 0:
            output_min = _min(output_data)
            output_max = _max(output_data)
            assert output_min >= 0.0 and output_max <= 1.0, \
                f"Output data must be in range [0, 1], got [{output_min:.3f}, {output_max:.3f}]"

    def record_dataframe(self, df: pd.DataFrame, input_columns=None, output_columns=None):
        if df.empty:
            return
            
        input_columns, output_columns = self._determine_dataframe_columns(df, input_columns, output_columns)
            
        if len(input_columns) != self.input_dimension:
            raise ValueError(f"DataFrame has {len(input_columns)} input columns, "
                           f"but search space expects {self.input_dimension}")
                           
        if len(output_columns) != self.output_dimension:
            raise ValueError(f"DataFrame has {len(output_columns)} output columns, "
                           f"but search space expects {self.output_dimension}")
        
        input_data = df[input_columns].values
        output_data = df[output_columns].values
        
        self._validate_dataframe_data(input_data, output_data)
        
        for i in range(len(df)):
            input_row = input_data[i]
            output_row = output_data[i] if self.output_dimension > 1 else output_data[i, 0]
            self.record_normalized(input_row, output_row)
