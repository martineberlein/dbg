from abc import abstractmethod
from typing import Any, Optional, Iterable

from dbg.data.input import Input
from dbg.data.oracle import OracleResult
from dbg.learner.learner import Learner
from dbg.learner.metric import FitnessStrategy, RecallPriorityFitness
from dbg.explanation.candidate import ExplanationSet
from dbg.types import Grammar


class PatternLearner(Learner):

    def __init__(
        self,
        grammar: Grammar,
        patterns: Optional[Iterable[str] | Iterable[Any]] = None,
        min_precision: float = 0.6,
        min_recall: float = 0.9,
        sorting_strategy: FitnessStrategy = RecallPriorityFitness(),
    ):
        super().__init__(sorting_strategy)

        self.patterns = self.parse_patterns(patterns)

        self.grammar = grammar
        self.min_precision = min_precision
        self.min_recall = min_recall

    @abstractmethod
    def parse_patterns(self, patterns):
        """
        Parse the patterns into constraints.
        """
        raise NotImplementedError()

    def meets_minimum_criteria(self, precision_value_, recall_value_):
        """
        Checks if the precision and recall values meet the minimum criteria.
        :param precision_value_: The precision value.
        :param recall_value_: The recall value.
        """
        return (
            precision_value_ >= self.min_precision and recall_value_ >= self.min_recall
        )

    @abstractmethod
    def learn_explanation(self, test_inputs: Iterable[Input], **kwargs) -> Optional[ExplanationSet]:
        pass

    def reset(self):
        """
        Resets the precision and recall truth tables. This is useful when the learner is used for multiple runs.
        Minimum precision and recall values are not reset.
        """
        self.explanations = ExplanationSet()

    @staticmethod
    def categorize_inputs(
        test_inputs: set[Input],
    ) -> tuple[set[Input], set[Input]]:
        """
        Categorize the inputs into positive and negative inputs based on their oracle results.
        """
        positive_inputs = {
            inp for inp in test_inputs if inp.oracle == OracleResult.FAILING
        }
        negative_inputs = {
            inp for inp in test_inputs if inp.oracle == OracleResult.PASSING
        }
        return positive_inputs, negative_inputs
