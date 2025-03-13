from abc import ABC, abstractmethod
from typing import Union, Iterable, Set, Optional
import time

from dbg.data.input import Input
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType
from dbg.learner.learner import Learner
from dbg.learner.metric import RecallPriorityStringLengthFitness
from dbg.learner.negation import ExplanationNegation, DefaultExplanationNegation
from dbg.generator.generator import Generator
from dbg.generator.engine import Engine, SingleEngine
from dbg.runner.runner import ExecutionHandler, SingleExecutionHandler
from dbg.logger import LOGGER, LoggerLevel


class InputExplainer(ABC):
    """
    Interface for debugging input features that result in the failure of a program.
    """

    def __init__(
        self,
        grammar,
        oracle: OracleType,
        initial_inputs: Union[Iterable[str], Iterable[Input]],
        logger_level: LoggerLevel = LoggerLevel.INFO,
    ):
        """
        Initialize the input feature debugger with a grammar, oracle, and initial inputs.
        """
        LOGGER.setLevel(logger_level.value)

        self.grammar = grammar
        self.oracle = oracle
        self.initial_inputs: set[Input] = self.set_initial_inputs(initial_inputs)

    def set_initial_inputs(self, test_inputs: Union[Iterable[str], Iterable[Input]]) -> set[Input]:
        """
        Set the initial inputs for the input feature debugger.
        """
        if test_inputs is None:
            raise ValueError("The initial inputs cannot be None.")

        initial_inputs = set()
        for inp in initial_inputs:
            if isinstance(inp, str):
                initial_inputs.add(Input.from_str(self.grammar, inp))
            elif isinstance(inp, Input):
                initial_inputs.add(inp)

        return initial_inputs

    @abstractmethod
    def explain(self, *args, **kwargs) -> ExplanationSet:
        """
        Explain the input features that result in the failure of a program.
        """
        raise NotImplementedError()


class HypothesisBasedExplainer(InputExplainer, ABC):
    """
    A hypothesis-based input feature debugger.
    """

    def __init__(
        self,
        grammar,
        oracle: OracleType,
        initial_inputs: Union[Iterable[str], Iterable[Input]],
        learner: Learner,
        generator: Generator,
        timeout_seconds: int = 3600,
        max_iterations: Optional[int] = 10,
        **kwargs,
    ):
        """
        Initialize the hypothesis-based input feature debugger with a grammar, oracle, initial inputs,
        learner, generator, and runner.
        """
        super().__init__(grammar, oracle, initial_inputs, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.max_iterations = max_iterations
        self.strategy = RecallPriorityStringLengthFitness()

        self.learner: Learner = learner
        self.constraint_negation: ExplanationNegation = DefaultExplanationNegation()
        self.generator: Generator = generator
        self.engine: Engine = SingleEngine(generator)

        self.runner: ExecutionHandler = SingleExecutionHandler(self.oracle)

    def set_runner(self, runner: ExecutionHandler):
        """
        Set the runner for the hypothesis-based input feature debugger.
        """
        self.runner = runner

    def set_learner(self, learner: Learner):
        """
        Set the learner for the hypothesis-based input feature debugger.
        """
        self.learner = learner

    def set_generator(self, generator: Generator):
        """
        Set the generator for the hypothesis-based input feature debugger.
        """
        self.generator = generator

    def set_timeout(self) -> Optional[float]:
        """
        Set the timeout for the hypothesis-based input feature debugger.
        Returns the start time if the timeout is set, otherwise None.
        """
        if self.timeout_seconds is not None:
            return int(time.time())
        return None

    def check_timeout_reached(self, start_time) -> bool:
        """
        Check if the timeout has been reached.
        """
        if self.timeout_seconds is None:
            return False
        return time.time() - start_time >= self.timeout_seconds

    def check_iterations_reached(self, iteration) -> bool:
        """
        Check if the maximum number of iterations has been reached.
        """
        return iteration >= self.max_iterations

    def check_iteration_limits(self, iteration, start_time) -> bool:
        """
        Check if the iteration limits have been reached.
        :param iteration: The current iteration.
        :param start_time: The start time of the input feature debugger.
        """
        if self.check_iterations_reached(iteration):
            return False
        if self.check_timeout_reached(start_time):
            return False
        return True

    def explain(self) -> ExplanationSet:
        """
        Explain the input features that result in the failure of a program.
        """
        iteration = 0
        start_time = self.set_timeout()
        LOGGER.info("Starting the hypothesis-based input feature debugger.")
        try:
            test_inputs: Set[Input] = self.initial_inputs

            while self.check_iteration_limits(iteration, start_time):
                LOGGER.info(f"Starting iteration {iteration}.")
                new_test_inputs = self.hypothesis_loop(test_inputs)
                test_inputs.update(new_test_inputs)

                iteration += 1
        except TimeoutError as e:
            LOGGER.error(e)
        except Exception as e:
            LOGGER.error(e)
        finally:
            return self.get_best_candidates()

    def hypothesis_loop(self, test_inputs: Set[Input]) -> Set[Input]:
        """
        The main loop of the hypothesis-based input feature debugger.
        """
        test_inputs = self.prepare_test_inputs(test_inputs)
        candidates = self.learn_candidates(test_inputs)
        hypotheses = self.create_hypotheses(candidates)
        inputs = self.generate_test_inputs(hypotheses)
        labeled_test_inputs = self.run_test_inputs(inputs)
        return labeled_test_inputs

    def prepare_test_inputs(self, test_inputs) -> Set[Input]:
        """
        Prepare the input feature debugger.
        Default implementation returns the test inputs as is.
        """
        return test_inputs

    @abstractmethod
    def learn_candidates(self, test_inputs: Set[Input]) -> ExplanationSet:
        """
        Learn the candidates (failure diagnoses) from the test inputs.
        """
        raise NotImplementedError()

    @abstractmethod
    def generate_test_inputs(self, candidates: ExplanationSet) -> Set[Input]:
        """
        Generate the test inputs based on the learned candidates.
        :param candidates: The learned candidates.
        :return Set[Input]: The generated test inputs.
        """
        raise NotImplementedError()

    def create_hypotheses(self, candidates: ExplanationSet) -> ExplanationSet:
        """
        Create new hypotheses by negating the learned candidates.
        """
        negated_candidates = self.constraint_negation.negate_explanations(candidates)
        hypotheses = negated_candidates + candidates
        return hypotheses

    def run_test_inputs(self, test_inputs: Set[Input]) -> Set[Input]:
        """
        Run the test inputs.
        """
        LOGGER.debug("Running the test inputs.")
        return self.runner.label(test_inputs=test_inputs)

    def get_best_candidates(
        self
    ) -> ExplanationSet:
        """
        Return the best candidate.
        """
        return self.learner.get_best_candidates()

    def get_test_inputs_from_strings(self, inputs: Iterable[str]) -> Set[Input]:
        """
        Convert a list of input strings to a set of Input objects.
        """
        return set([Input.from_str(self.grammar, inp, None) for inp in inputs])

    @staticmethod
    def check_initial_conditions(test_inputs: Set[Input]):
        """
        Check the initial conditions for the input feature debugger.
        Raises a ValueError if the conditions are not met.
        """

        has_failing = any(inp.oracle.is_failing() for inp in test_inputs)
        has_passing = any(not inp.oracle.is_failing() for inp in test_inputs)

        if not (has_failing and has_passing):
            raise ValueError("The initial inputs must contain at least one failing and one passing input.")
