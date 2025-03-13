from abc import ABC, abstractmethod
from typing import Generator, Optional, Final, Any
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
        self._tree: Final = tree
        self._oracle: Optional[OracleResult] = oracle

    @property
    def tree(self) -> Any:
        """
        Retrieves the derivation tree of the input.
        :return DerivationTree: The derivation tree.
        """
        return self._tree

    @property
    def oracle(self) -> OracleResult:
        """
        Retrieves the oracle result associated with the input.
        :return OracleResult: The oracle result, or None if not set.
        """
        return self._oracle

    @oracle.setter
    def oracle(self, oracle_: OracleResult):
        """
        Sets the oracle result for the input.
        :param OracleResult oracle_: The new oracle result to set.
        """
        self._oracle = oracle_

    def update_oracle(self, oracle_: OracleResult) -> "Input":
        """
        Updates the oracle result for the input and returns the modified input instance.
        :param OracleResult oracle_: The new oracle result to set.
        :return Input: The current input instance with the updated oracle.
        """
        self._oracle = oracle_
        return self

    def __repr__(self) -> str:
        """
        Provides the canonical string representation of the Input instance.
        :return str: A string representation that can recreate the Input instance.
        """
        return f"Input({repr(self.tree)}, {repr(self.oracle)})"

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Input's derivation tree.
        :return str: The string representation of the derivation tree.
        """
        return str(self._tree)

    @abstractmethod
    def __hash__(self) -> int:
        """Abstract hash method that subclasses must implement."""
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        """
        Determines equality based on the structural hash of the derivation trees.
        :param other: The object to compare against.
        :return bool: True if the other object is an Input with an equal derivation tree.
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
