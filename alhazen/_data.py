from typing import Optional

from fuzzingbook.Parser import EarleyParser
from dbg.data.input import Input, OracleResult

from alhazen.features.features import FeatureVector
from alhazen import tree_to_string, DerivationTree

class AlhazenInput(Input):

    def __init__(self, tree: DerivationTree, oracle: Optional[OracleResult] = None):
        self._hash = hash(tree_to_string(tree))
        self._features = None
        super().__init__(tree, oracle)

    def __hash__(self) -> int:
        return self._hash

    @property
    def features(self) -> FeatureVector:
        return self._features

    @features.setter
    def features(self, features_: FeatureVector):
        self._features = features_

    @classmethod
    def from_str(cls, grammar, input_string, oracle: Optional[OracleResult] = None):
        tree = next(EarleyParser(grammar).parse(input_string))
        return cls(tree, oracle)

    def __repr__(self):
        return f"AlhazenInput({tree_to_string(self.tree)}, {self.oracle})"