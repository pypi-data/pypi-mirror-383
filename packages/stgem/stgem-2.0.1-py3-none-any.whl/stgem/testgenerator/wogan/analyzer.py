import copy
import importlib

import torch

from stgem import config
from stgem import filter_arguments


class Analyzer:
    """Base class for WOGAN analyzers."""

    default_parameters = {}

    def __init__(self, parameters: dict = None):
        if parameters is None:
            parameters = copy.deepcopy(self.default_parameters)
        self.parameters = parameters
        self.modelA = None

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__.get(name)
        if "parameters" in self.__dict__ and name in self.parameters:
            return self.parameters.get(name)
        raise AttributeError(name)

    def setup(self, rng=None):
        self.rng = rng
    
    def to_device(self, device):
        self.modelA = self.modelA.to(device)

    def train_with_batch(self, dataX, dataY, train_settings):
        raise NotImplementedError()

    def predict(self, test):
        raise NotImplementedError()


class Analyzer_NN(Analyzer):
    """Analyzer based on a neural network for regression."""

    def setup(self, rng=None):
        super().setup(rng=rng)

        # Load the specified analyzer machine learning model unless it is already loaded.
        if self.modelA is None:
            module = importlib.import_module("stgem.testgenerator.wogan.mlm")
            analyzer_class = getattr(module, self.analyzer_mlm)
            self.modelA = analyzer_class(rng=self.rng,
                                         **filter_arguments(self.analyzer_mlm_parameters, analyzer_class)).to(config.device)
        else:
            self.modelA = self.modelA.to(config.device)

        # Load the specified optimizer.
        module = importlib.import_module("torch.optim")
        optimizer_class = getattr(module, self.optimizer)
        self.optimizerA = optimizer_class(self.modelA.parameters(), **filter_arguments(self.parameters, optimizer_class))

        # Loss functions.
        def get_loss(loss_s):
            loss_s = loss_s.lower()
            if loss_s == "crossentropy":
                loss = torch.nn.CrossEntropyLoss()
            elif loss_s == "mse":
                loss = torch.nn.MSELoss()
            elif loss_s == "l1":
                loss = torch.nn.L1Loss()
            elif loss_s in ("mse,logit", "l1,logit"):
                # When doing regression with values in [0, 1], we can use a
                # logit transformation to map the values from [0, 1] to \R
                # to make errors near 0 and 1 more drastic. Since logit is
                # undefined in 0 and 1, we actually first transform the values
                # to the interval [0.01, 0.99].
                if loss_s == "mse,logit":
                    g = torch.nn.MSELoss()
                else:
                    g = torch.nn.L1Loss()

                def f(X, Y):
                    return g(torch.logit(0.98 * X + 0.01), torch.logit(0.98 * Y + 0.01))

                loss = f
            else:
                raise ValueError(f"Unknown loss function '{loss_s}'.")

            return loss

        try:
            self.loss_A = get_loss(self.loss)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize WOGAN analyzer loss function '{self.loss}': {e}") from e

    def analyzer_loss(self, dataX, dataY):
        """
        Computes the analyzer loss for dataX given real outputs dataY.
        """

        # Compute the configured loss.
        model_loss = self.loss_A(dataX, dataY)

        # Compute L2 regularization if needed.
        l2_regularization = 0
        if "l2_regularization_coef" in self.parameters and self.l2_regularization_coef != 0:
            for parameter in self.modelA.parameters():
                l2_regularization += torch.sum(torch.square(parameter))
        else:
            self.parameters["l2_regularization_coef"] = 0

        A_loss = model_loss + self.l2_regularization_coef * l2_regularization

        return A_loss

    def _train_with_batch(self, dataX, dataY, _train_settings=None):
        # Save the training modes for later restoring.
        training_A = self.modelA.training

        # Train the analyzer.
        # ---------------------------------------------------------------------
        self.modelA.train(True)
        A_loss = self.analyzer_loss(self.modelA(dataX), dataY)
        self.optimizerA.zero_grad()
        A_loss.backward()
        self.optimizerA.step()

        # Visualize the computational graph.
        # print(make_dot(A_loss, params=dict(self.modelA.named_parameters())))

        self.modelA.train(training_A)

        return A_loss.item()

    def train_with_batch(self, dataX, dataY, train_settings):
        """
        Train the analyzer part of the model with a batch of training data.

        Args:
            dataX (np.ndarray): Array of tests of shape
                (N, self.modelA.input_shape).
            dataY (np.ndarray): Array of test outputs of shape (N, 1).
                train_settings (dict): A dictionary for setting up the training.
                Currently, all keys are ignored.
            train_settings (bool)
        """

        dataX = torch.from_numpy(dataX).float().to(config.device)
        dataY = torch.from_numpy(dataY).float().to(config.device)
        return self._train_with_batch(dataX, dataY, _train_settings=train_settings)

    def predict(self, test):
        """
        Predicts the objective function value of the given test.

        Args:
            test (np.ndarray): Array with shape (1, N) or (N)
                where N is self.modelA.input_shape.

        Returns:
            output (np.ndarray): Array with shape (1).
        """

        test_tensor = torch.from_numpy(test).float().to(config.device)
        return self.modelA(test_tensor).cpu().detach().numpy().reshape(-1)


class Analyzer_NN_classifier(Analyzer_NN):
    """
    Analyzer using classification in place of regression.
    """

    def __init__(self, parameters: dict):
        super().__init__(parameters)

    def _put_to_class(self, Y):
        """
        Classifies the floats in Y.
        """

        Z = (Y * self.classes).int()
        return (Z - (Z == self.classes).int()).long()

    def train_with_batch(self, dataX, dataY, train_settings):
        """
        Train the analyzer part of the model with a batch of training data.

        Args:
            dataX (np.ndarray):   Array of tests of shape
                (N, self.modelA.input_shape).
            dataY (np.ndarray):   Array of test outputs of shape (N, 1).
            train_settings (dict): A dictionary for setting up the training.
                Currently all keys are ignored.
        """

        dataX = torch.from_numpy(dataX).float().to(config.device)
        dataY = self.put_to_class(torch.from_numpy(dataY).float().to(config.device))
        return self._train_with_batch(dataX, dataY, _train_settings=None)

    def predict(self, test):
        """
        Predicts the objective function value of the given test.

        Args:
            test (np.ndarray): Array of shape (N, self.modelA.input_shape).

        Returns:
            output (np.ndarray): Array of shape (N, 1).
        """

        training_A = self.modelA.training
        self.modelA.train(False)

        test_tensor = torch.from_numpy(test).float().to(config.device)
        p = self.modelA(test_tensor)
        result = torch.argmax(p, dim=1) / self.classes + 1 / (2 * self.classes)

        self.modelA.train(training_A)
        return result.cpu().detach().numpy().reshape(-1, 1)


class RandomAnalyzer(Analyzer):
    """Random analyzer that just guesses uniformly randomly."""

    default_parameters = {}

    def train_with_batch(self, dataX, dataY, train_settings):
        return [0]

    def predict(self, test):
        result = self.rng.get_rng("numpy").uniform(size=(test.shape[0], 1))
        return result
