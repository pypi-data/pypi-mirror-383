import heapq
import time

from stgem import SearchSpace, logging, merge_dictionary
from stgem.exceptions import GenerationException

class ModelSampler:
    """A simple model sampler that merely samples a model until a valid test
    is found. This class also serves as a base class for more complex
    samplers."""

    default_parameters = {
        "invalid_threshold": 100
    }

    def __init__(self, parameters: dict = None):
        if parameters is None:
            parameters = {}
        self.parameters = merge_dictionary(parameters, self.default_parameters)
        
        self.search_space = None

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__.get(name)
        if "parameters" in self.__dict__ and name in self.parameters:
            return self.parameters.get(name)
        raise AttributeError(name)

    def setup(self, search_space: SearchSpace):
        self.search_space = search_space
        
    def __call__(self, model, remaining: float = 1.0):
        performance = {}
        N_generated = 0
        N_invalid = 0
        time_start = time.perf_counter()

        # Generate a test with generator until a valid test is found.
        while True:
            # If we have already generated many tests and all have been
            # invalid, we give up.
            if N_invalid >= self.invalid_threshold:
                raise GenerationException(f"Could not generate a valid test within {N_invalid} tests.")
            
            try:
                candidate_test = model.generate_test()
                N_generated += 1
            except Exception as e:
                raise RuntimeError(f"Model test generation failed after {N_generated} attempts: {e}") from e

            if self.search_space.is_valid(candidate_test) != 1.0:
                N_invalid += 1
                continue
            
            break
            
        performance["N_tests_generated"] = N_generated
        performance["N_invalid_tests_generated"] = N_invalid
        performance["generation_time"] = time.perf_counter() - time_start
        
        return candidate_test.reshape(-1), model.predict_objective(candidate_test)[0], performance

class RejectionSampler(ModelSampler):
    """A rejection sampler that samples a given model until a valid test with
    low enough estimated objective is found or until a certain maximum number
    of samples have been drawn. The sample with the best estimated objective is
    returned."""
    
    def __call__(self, model, remaining: float = 1.0):  # pylint: disable=too-many-locals
        performance = {}
        N_generated = 0
        N_invalid = 0
        time_start = time.perf_counter()

        heap = []
        target_objective = 0
        entry_count = 0  # this is to avoid comparing tests when two tests added to the heap have the same predicted objective

        logging.debug("Generating a test using rejection sampling.")

        while True:
            while True:
                # If we have already generated many tests and all have been
                # invalid, we give up.
                if N_invalid >= self.invalid_threshold:
                    raise GenerationException(f"Could not generate a valid test within {N_invalid} tests.")

                # Generate several tests along with their objective estimates
                # as long as a valid test is found.
                try:
                    candidate_test = model.generate_test()
                    N_generated += 1
                except Exception as e:
                    raise RuntimeError(f"Model test generation failed during objective-based sampling after {N_generated} attempts: {e}") from e

                if self.search_space.is_valid(candidate_test) != 1.0:
                    N_invalid += 1
                    continue
                
                break

            # Estimate the objective, and add the test to the heap.
            predicted_objective = model.predict_objective(candidate_test)[0]
            heapq.heappush(heap, (predicted_objective, entry_count, candidate_test.reshape(-1)))
            entry_count += 1

            # We go up from 0 like we would go down from 1 when multiplied by self.fitness_coef.
            target_objective = 1 - self.objective_coef * (1 - target_objective)

            # Check if the best predicted test is good enough.
            # Without eps we could get stuck if prediction is always 1.0.
            eps = 1e-4
            if heap[0][0] - eps <= target_objective: break

        performance["N_tests_generated"] = N_generated
        performance["N_invalid_tests_generated"] = N_invalid
        performance["generation_time"] = time.perf_counter() - time_start

        best_test = heap[0][2]
        best_estimated_objective = heap[0][0]
        
        logging.debug(f"Chose test {best_test} with predicted minimum objective "
                     f"{best_estimated_objective}. Generated total {N_generated} tests "
                     f"of which {N_invalid} were invalid.")

        return best_test, best_estimated_objective, performance
