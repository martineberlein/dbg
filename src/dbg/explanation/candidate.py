from abc import ABC, abstractmethod
from typing import Optional, Generic, TypeVar

from dbg.data.input import Input


class Explanation(ABC):
    """
    Represents a learned explanation.
    """

    def __init__(self, explanation):
        self.explanation = explanation
        self.__hash = hash(str(self.explanation))

        self.failing_inputs_eval_results = []
        self.passing_inputs_eval_results = []
        self.cache: dict[Input, bool] = {}

    @abstractmethod
    def evaluate(self, test_inputs: set[Input], *args, **kwargs):
        pass

    def recall(self) -> float:
        """
        Return the recall of the candidate.
        """
        if len(self.failing_inputs_eval_results) == 0:
            return 0.0
        return sum(int(entry) for entry in self.failing_inputs_eval_results) / len(
            self.failing_inputs_eval_results
        )

    def precision(self) -> float:
        """
        Return the precision of the candidate.
        """
        tp = sum(int(entry) for entry in self.failing_inputs_eval_results)
        fp = sum(int(entry) for entry in self.passing_inputs_eval_results)
        return tp / (tp + fp) if tp + fp > 0 else 0.0

    def specificity(self) -> float:
        """
        Return the specificity of the candidate.
        """
        if len(self.passing_inputs_eval_results) == 0:
            return 0.0
        return sum(not int(entry) for entry in self.passing_inputs_eval_results) / len(
            self.passing_inputs_eval_results
        )

    def __hash__(self):
        return self.__hash

    def __len__(self):
        return len(str(self.explanation))

    def __repr__(self):
        """
        Return a string representation of the explanation.
        """
        return f"Explanation({str(self.explanation)}, precision={self.precision()}, recall={self.recall()}"

    def __str__(self):
        """
        Return a string representation of the explanation.
        """
        return str(self.explanation)

    def __eq__(self, other):
        """
        Return whether two candidates are equal.
        """
        return isinstance(other, Explanation) and self.explanation == other.explanation

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __neg__(self):
        pass


T = TypeVar("T", bound=Explanation)

class ExplanationSet(Generic[T]):
    def __init__(self, explanations: Optional[list[T]] = None):
        self.explanation_hashes: dict[int, int] = {}
        self.explanations: list[T] = []

        explanations = explanations or []
        for idx, explanation in enumerate(explanations):
            explanation_hash = hash(explanation)
            if explanation_hash not in self.explanation_hashes:
                self.explanation_hashes[explanation_hash] = idx
                self.explanations.append(explanation)

    def __repr__(self) -> str:
        return f"ExplanationSet({repr(self.explanations)})"

    def __str__(self) -> str:
        return "\n".join(map(str, self.explanations))

    def __len__(self) -> int:
        return len(self.explanations)

    def __iter__(self):
        return iter(self.explanations)

    def __add__(self, other: "ExplanationSet[T]") -> "ExplanationSet[T]":
        return ExplanationSet(self.explanations + other.explanations)

    def append(self, candidate: T) -> None:
        candidate_hash = hash(candidate)
        if candidate_hash not in self.explanation_hashes:
            self.explanation_hashes[candidate_hash] = len(self.explanations)
            self.explanations.append(candidate)

    def remove(self, candidate: T) -> None:
        candidate_hash = hash(candidate)
        if candidate_hash in self.explanation_hashes:
            last_elem, idx = self.explanations[-1], self.explanation_hashes[candidate_hash]
            self.explanations[idx] = last_elem
            self.explanation_hashes[hash(last_elem)] = idx
            self.explanations.pop()
            del self.explanation_hashes[candidate_hash]