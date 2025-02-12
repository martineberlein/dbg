from abc import ABC, abstractmethod
from typing import Any

from dbg.data.input import Input


class AbstractGrammar(ABC):
    """
    Abstract base class for all grammar implementations.
    """

    def __init__(self, grammar: Any, **kwargs):
        """
        Abstract constructor for grammar implementations.
        Must be implemented by subclasses.
        """
        self.grammar = grammar

    @abstractmethod
    def parse(self, input_string: str) -> Input | None:
        """
        Abstract method to parse an input string.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def fuzz(self) -> Input:
        """
        Abstract method to generate a string from the grammar.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def __str__(self):
        """
        Returns a string representation of the grammar.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_nonterminals(self):
        """
        Returns the nonterminals of the grammar.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_rules(self):
        """
        Returns the rules of the grammar.
        """
        raise NotImplementedError()