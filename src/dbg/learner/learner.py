from typing import List, Iterable, Optional
from abc import ABC, abstractmethod

from dbg.explanation.candidate import ExplanationSet
from dbg.data.input import Input


class Learner(ABC):
    """
    A candidate learner is responsible for learning candidate formulas from a set
    """
    def __init__(self):
        self.explanations: ExplanationSet = ExplanationSet()

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

    @abstractmethod
    def get_explanations(self) -> Optional[ExplanationSet]:
        """
        Get all explanations that have been learned.
        :return Optional[List[Candidate]]: The learned candidates.
        """
        return self.explanations

    @abstractmethod
    def get_best_candidates(self) -> Optional[ExplanationSet]:
        """
        Get the best constraints that have been learned.
        :return Optional[List[Candidate]]: The best learned candidates.
        """
        raise NotImplementedError()