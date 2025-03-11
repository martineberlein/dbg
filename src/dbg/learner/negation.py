from abc import ABC, abstractmethod

from dbg.explanation.candidate import Explanation, ExplanationSet


class ExplanationNegation(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def negate_explanations(self, explanations: ExplanationSet) -> ExplanationSet:
        pass

class DefaultExplanationNegation(ExplanationNegation):

    def negate_explanations(self, explanations: ExplanationSet) -> ExplanationSet:
        return ExplanationSet([-explanation for explanation in explanations])