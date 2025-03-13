from typing import Optional

from dbg.data.input import Input
from dbg.data.oracle import OracleResult

from avicenna import DerivationTree, EarleyParser
from avicenna.features.features import FeatureVector


class AvicennaInput(Input):
    """
    Class describing a test input.
    """

    def __init__(self, tree: DerivationTree, oracle: OracleResult = None):
        super().__init__(tree, oracle)
        self.__features: Optional[FeatureVector] = None

    @property
    def features(self) -> FeatureVector:
        return self.__features

    @features.setter
    def features(self, features_: FeatureVector):
        self.__features = features_

    def update_features(self, features_: FeatureVector) -> "Input":
        self.__features = features_
        return self

    def __hash__(self) -> int:
        return self.__tree.structural_hash()

    @classmethod
    def from_str(cls, grammar, input_string, oracle: Optional[OracleResult] = None):
        return cls(
            DerivationTree.from_parse_tree(
                next(EarleyParser(grammar).parse(input_string))
            ),
            oracle,
        )


__all__ = ["AvicennaInput"]