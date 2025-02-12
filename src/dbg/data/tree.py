from abc import ABC, abstractmethod
from typing import Any, Generator

class DerivationTree(ABC):
    """
    Abstract base class for all derivation tree implementations.
    """

    @abstractmethod
    def traverse(self) -> Generator[Any, None, None]:
        """
        Abstract method for traversing the derivation tree.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def structural_hash(self) -> int:
        """
        Abstract method to compute a unique hash of the tree structure.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a string representation of the derivation tree.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def parse(cls, grammar: Any, input_string: str) -> "DerivationTree":
        """
        Abstract factory method to create a derivation tree from a string using a grammar.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()
