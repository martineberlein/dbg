from typing import List, Iterable, Optional
from abc import ABC, abstractmethod

from dbg.explanation.candidate import ExplanationSet, Explanation
from dbg.learner.metric import FitnessStrategy, RecallPriorityLengthFitness
from dbg.data.input import Input


class Learner(ABC):
    """
    A candidate learner is responsible for learning candidate formulas from a set
    """
    def __init__(self, sorting_strategy: FitnessStrategy = RecallPriorityLengthFitness()):
        self.explanations: ExplanationSet = ExplanationSet()
        self.sorting_strategy = sorting_strategy

    @abstractmethod
    def learn_explanation(
        self, test_inputs: Iterable[Input], **kwargs
    ) -> Optional[ExplanationSet]:
        """
        Learn the candidates based on the test inputs.
        :param test_inputs: The test inputs to learn the candidates from.
        :return Optional[List[Candidate]]: The learned candidates.
        """
        raise NotImplementedError()

    def get_explanations(self) -> Optional[ExplanationSet]:
        """
        Get all explanations that have been learned.
        :return Optional[List[Candidate]]: The learned candidates.
        """
        return self.explanations

    def get_best_candidates(self) -> Optional[ExplanationSet]:
        """
        Get the best constraints that have been learned.
        :return Optional[List[Candidate]]: The best learned candidates.
        """
        result = ExplanationSet()
        if self.explanations:
            sorted_explanation = self._get_sorted_explanations()
            for explanation in sorted_explanation:
                if self.sorting_strategy.is_equal(explanation, sorted_explanation[0]):
                    result.append(explanation)
        return result

    def _get_sorted_explanations(self) -> Optional[List[Explanation]]:
        return sorted(self.explanations, key=lambda exp: self.sorting_strategy.evaluate(exp), reverse=True)