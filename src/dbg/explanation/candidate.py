from abc import ABC, abstractmethod
from typing import Optional

from dbg.data.input import Input
# from dbg.learner.metric import FitnessStrategy


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

    # def with_strategy(self, strategy: FitnessStrategy):
    #     """
    #     Return the evaluation of the candidate with a given fitness strategy.
    #     """
    #     return strategy.evaluate(self)

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


class ExplanationSet:

    def __init__(self, explanations: Optional[list[Explanation]] = None):
        self.explanation_hashes = dict()
        self.explanations = []

        explanations = explanations or []

        for idx, explanation in enumerate(explanations):
            explanation_hash = hash(explanation)
            if explanation_hash not in self.explanation_hashes:
                self.explanation_hashes[explanation_hash] = idx
                self.explanations.append(explanation)

    def __repr__(self):
        """
        Return a string representation of the candidate set and its candidates.
        """
        return f"CandidateSet({repr(self.explanations)})"

    def __str__(self):
        """
        Return a string representation of the candidate set and its candidates.
        """
        return "\n".join(map(str, self.explanations))

    def __len__(self):
        """
        Return the number of candidates in the candidate set.
        """
        return len(self.explanations)

    def __iter__(self):
        """
        Iterate over the candidates in the candidate set.
        """
        return iter(self.explanations)

    def __add__(self, other):
        """
        Add two candidate sets together.
        """
        return ExplanationSet(self.explanations + other.explanations)

    def append(self, candidate: Explanation):
        """
        Add a candidate to the candidate set.
        """
        candidate_hash = hash(candidate)
        if candidate_hash not in self.explanation_hashes:
            self.explanation_hashes[candidate_hash] = len(self.explanations)
            self.explanations.append(candidate)

    def remove(self, candidate: Explanation):
        """
        Remove a candidate from the candidate set.
        """
        candidate_hash = hash(candidate)
        if candidate_hash in self.explanation_hashes:
            last_elem, idx = self.explanations[-1], self.explanation_hashes[candidate_hash]
            self.explanations[idx] = last_elem
            self.explanation_hashes[hash(last_elem)] = idx
            self.explanations.pop()
            del self.explanation_hashes[candidate_hash]
