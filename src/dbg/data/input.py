from abc import ABC, abstractmethod
from typing import Generator, Optional, Final
from dbg.data.oracle import OracleResult

class Input(ABC):
    """
    Represents a test input comprising a derivation tree and an associated oracle result.
    The derivation tree represents the parsed structure of the input, and the oracle result
    provides the outcome when this input is processed by a system under test.
    """

    def __init__(self, tree, oracle: Optional[OracleResult] = None):
        """
        Initializes the Input instance with a derivation tree and an optional oracle result.

        :param tree: The derivation tree of the input.
        :param OracleResult oracle: The optional oracle result associated with the input.
        """
        self._tree: Final = tree  # Store the tree but don't enforce a specific type
        self._oracle: Optional[OracleResult] = oracle

    @property
    def tree(self):
        """Retrieves the derivation tree of the input."""
        return self._tree

    @property
    def oracle(self) -> Optional[OracleResult]:
        """Retrieves the oracle result associated with the input."""
        return self._oracle

    @oracle.setter
    def oracle(self, oracle_: OracleResult):
        """Sets the oracle result for the input."""
        self._oracle = oracle_

    @abstractmethod
    def traverse(self):
        """
        Abstract method for traversing the derivation tree.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self) -> int:
        """Abstract hash method that subclasses must implement."""
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        """
        Determines equality based on the structural hash of the derivation trees.
        """
        return isinstance(other, Input) and self.__hash__() == hash(other)

    def __iter__(self) -> Generator:
        """
        Allows tuple unpacking of the input, e.g., tree, oracle = input.
        """
        yield self.tree
        yield self.oracle

    def __getitem__(self, item: int):
        """
        Allows indexed access to the input's derivation tree and oracle.
        """
        assert item in (0, 1), "Index must be 0 (tree) or 1 (oracle)"
        return self.tree if item == 0 else self.oracle

    @classmethod
    @abstractmethod
    def from_str(cls, grammar, input_string, oracle: Optional[OracleResult] = None):
        """
        Abstract factory method to create an Input instance from a string.
        Subclasses must implement this method.
        """
        raise NotImplementedError()
