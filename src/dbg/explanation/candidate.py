from abc import ABC, abstractmethod
from typing import Optional


class Explanation(ABC):
    """
    Represents a learned explanation.
    """

    def __init__(self, explanation):
        self.explanation = explanation
        self.__hash = hash(str(self.explanation))

    @abstractmethod
    def evaluate(self, inputs):
        pass

    @abstractmethod
    def precision(self):
        pass

    @abstractmethod
    def recall(self):
        pass

    @abstractmethod
    def specificity(self):
        pass

    @abstractmethod
    def __and__(self, other):
        pass

    @abstractmethod
    def __or__(self, other):
        pass

    @abstractmethod
    def __neg__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __len__(self):
        return len(self.explanation)


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
