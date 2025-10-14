import time as time_measure

from stgem.features import FeatureVector, SignalRepresentation, PiecewiseConstantSignal, PiecewiseLinearSignal, Signal
from stgem.sut import SystemUnderTest
from fmpy import extract, read_model_description
import numpy as np

import sys
import os

class FMU(SystemUnderTest):
    """Class for testing Functional Mock-up Units using the FMI interface.

        Args:
            model_file (str): Path to the model file. Must be an .fmu file!
            inputs (FeatureVector): A FeatureVector describing the inputs to the model.
            outputs (FeatureVector): A FeatureVector describing the outputs from the model.

        Raises:
            Exception: If any of the inputs fail their type checks or if the files at the \
            given paths are missing
    """
    def __init__(self, model_file: str, inputs: FeatureVector, outputs: FeatureVector) -> None:
        super().__init__()

        if not isinstance(model_file, str):
            raise TypeError('Model file must be a string')
        if not isinstance(inputs, FeatureVector) or not isinstance(outputs, FeatureVector):
            raise TypeError('Inputs and outputs must be of type FeatureVector')

        self.inputs = inputs
        self.outputs = outputs
        self.model_file = model_file

        description = read_model_description(model_file)
        self._setup_value_references(description)
        self.version = self._get_fmi_version(description.fmiVersion)
        Model = self._get_model_class(description)
        unzipdir = self._prepare_binaries(model_file, description)
        self.model = self._create_model_instance(description, Model, unzipdir)

    def _setup_value_references(self, description):
        """Extract value references for inputs and outputs."""
        self.output_vrs = {}
        self.input_vrs = {}
        for var in description.modelVariables:
            if var.causality == 'output':
                self.output_vrs[var.name] = var.valueReference
            if var.causality == 'input':
                self.input_vrs[var.name] = var.valueReference

    def _get_fmi_version(self, version_string):
        """Extract FMI version number from version string."""
        if version_string.startswith('1.'):
            return 1
        if version_string.startswith('2.'):
            return 2
        if version_string.startswith('3.'):
            return 3
        
        raise ValueError('Invalid FMU version')

    def _get_model_class(self, description):
        """Get appropriate model class based on FMI version and type."""
        if self.version == 1:
            from fmpy.fmi1 import FMU1Model, FMU1Slave  # pylint: disable=import-outside-toplevel
            return FMU1Slave if description.coSimulation else FMU1Model
        if self.version == 2:
            from fmpy.fmi2 import FMU2Model, FMU2Slave  # pylint: disable=import-outside-toplevel
            return FMU2Slave if description.coSimulation else FMU2Model
        if self.version == 3:
            from fmpy.fmi3 import FMU3Model, FMU3Slave  # pylint: disable=import-outside-toplevel
            return FMU3Slave if description.coSimulation else FMU3Model
        
        raise ValueError(f'Unsupported FMI version: {self.version}')

    def _prepare_binaries(self, model_file, _description):
        """Prepare FMU binaries, compiling if necessary."""
        unzipdir = extract(model_file)
        binaries = os.path.join(unzipdir, 'binaries')
        subdirs = next(os.walk(binaries))[1]
        platform = sys.platform
        
        # Check if the binaries for the current platform exist
        # If not, compile them if source is available
        if not any(d.startswith(platform) for d in subdirs):
            if not os.path.exists(os.path.join(unzipdir, 'sources')):
                raise RuntimeError('FMU missing binary for this platform and no sources available.')
            unzipdir = self.compile_binaries(model_file)
        
        return unzipdir

    def _create_model_instance(self, description, Model, unzipdir):
        """Create and instantiate the FMU model."""
        identifier = description.coSimulation.modelIdentifier if description.coSimulation else description.modelExchange.modelIdentifier
        model = Model(guid=description.guid,
                      unzipDirectory=unzipdir,
                      modelIdentifier=identifier)
        model.instantiate()
        return model

    def compile_binaries(self, model_file: str) -> str:
        from fmpy.util import compile_platform_binary  # pylint: disable=import-outside-toplevel
        compile_platform_binary(model_file)
        return extract(model_file)

    def reset(self):
        self.model.terminate()
        self.setupExperiment()
        self.model.enterInitializationMode()
        self.model.exitInitializationMode()

    def new_ifv(self) -> FeatureVector:
        return self.inputs()

    def new_ofv(self) -> FeatureVector:
        return self.outputs()

    def from_ifv_to_testinput(self, input_fv: FeatureVector):
        inputs = []
        timestamps = None
        for feature in input_fv:
            if isinstance(feature, SignalRepresentation):
                timestamps, values = feature.synthesize_signal()
                inputs.append(list(values))
            else:
                inputs.append(feature.get())

        return (timestamps, inputs)

    def from_testouput_to_ofv(self, output) -> FeatureVector:
        fv = self.new_ofv()
        timestamps = output[0]
        values = output[1:]

        toSet = []
        for entry in values:
            toSet.append([timestamps, entry])

        fv.set(toSet)
        return fv

    def execute_test(self, test_input):
        results = []
        idx = 0

        timestamps, inputs = test_input
        start_time = timestamps[0]
        stop_time = timestamps[-1]
        step = timestamps[1] - start_time
        time = start_time

        input_vrs = [vr for i, vr in self.input_vrs.items()]
        output_vrs = [vr for o, vr in self.output_vrs.items()]

        # Reset the model prior to running a new experiment, as we reuse the same model
        self.reset()

        # Get initial state at time 0
        values = self.getReal(output_vrs)
        results.append((time, *values))

        start_time = time_measure.perf_counter()
        while time < stop_time:
            # Allow input to be a single value or an element in a list
            real = [i[idx] if isinstance(i, list) else i for i in inputs]
            self.setReal(input_vrs, real)
            self.model.doStep(currentCommunicationPoint=time, communicationStepSize=step)
            time += step
            idx += 1

            values = self.getReal(output_vrs)
            results.append((time, *values))

        return np.asarray(results).T, {"execution_time": time_measure.perf_counter() - start_time}

    def setupExperiment(self, start_time = 0):
        if self.version == 2:
            self.model.setupExperiment(startTime=start_time)

    # 64-bit float is probably the safest to use here without getting too convoluted
    # with types
    def setReal(self, vrs, values):
        if self.version == 3:
            self.model.setFloat64(vrs, values)
        else:
            self.model.setReal(vrs, values)

    def getReal(self, vrs):
        if self.version == 3:
            return self.model.getFloat64(vrs)
        return self.model.getReal(vrs)

    def __del__(self):
        # Free the model resources
        self.model.terminate()
        self.model.freeInstance()

def extract_fmu_features(model_path: str, input_representation: str = 'piecewise constant', 
                        pieces: int = 5, duration: int = None, 
                        sampling_period: float = None) -> FeatureVector:
    """Creates feature vectors for the FMU based on the model description

    Args:
        model_path (str): Path to the model file
        pieces (int, optional): How many pieces in the Piecewise Constant Signal. Defaults to 5.
        duration (int, optional): Duration of the simulation. Defaults to model's default experiment duration.
        sampling_period (float, optional): The step size for the model. Defaults to model's default experiment step size.

    Raises:
        Exception: If the model doesn't exist

    Returns:
        FeatureVector: input and output feature vectors, in that order.
    """

    if not isinstance(model_path, str):
        raise TypeError('Model file must be a string')
    
    match input_representation:
        case 'piecewise constant':
            C = PiecewiseConstantSignal
        case 'piecewise linear':
            C = PiecewiseLinearSignal
        case _:
            raise ValueError(f'Unknown input representation "{input_representation}".')

    description = read_model_description(model_path)

    if sampling_period is None:
        sampling_period = description.defaultExperiment.stepSize
    if duration is None:
        duration = description.defaultExperiment.stopTime
    piece_duration = duration / pieces

    input_features = []
    output_features = []
    for var in description.modelVariables:
        if var.causality == 'input':
            input_features.append(C(name=var.name,
                                    piece_durations=[piece_duration]*pieces,
                                    sampling_period=sampling_period,
                                    min_value=var.min,
                                    max_value=var.max))
        if var.causality == 'output':
            output_features.append(Signal(name=var.name,
                                          min_value=var.min,
                                          max_value=var.max))

    input_fv = FeatureVector(name='inputs', features=input_features)
    output_fv = FeatureVector(name='outputs', features=output_features)
    return input_fv, output_fv
