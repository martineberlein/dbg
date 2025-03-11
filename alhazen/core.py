from typing import Set, Iterable

from dbg.core import HypothesisBasedExplainer
from dbg.data.input import OracleResult
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType

from alhazen._learner import AlhazenLearner
from alhazen._generator import AlhazenGenerator
from alhazen import Grammar
from alhazen._data import AlhazenInput
from alhazen.features.collector import GrammarFeatureCollector


class Alhazen(HypothesisBasedExplainer):

    def __init__(
        self,
        grammar: Grammar,
        oracle: OracleType,
        initial_inputs: Iterable[str],
        **kwargs,
    ):

        learner = AlhazenLearner()
        generator = AlhazenGenerator(grammar)

        super().__init__(grammar, oracle, initial_inputs, learner, generator, **kwargs)

        self.collector = GrammarFeatureCollector(grammar)

    def set_initial_inputs(self, test_inputs: Iterable[str]) -> set[AlhazenInput]:
        return {
            AlhazenInput.from_str(self.grammar, inp, self.oracle(inp))
            for inp in test_inputs
        }

    def prepare_test_inputs(self, test_inputs: set[AlhazenInput]) -> Set[AlhazenInput]:
        for inp in test_inputs:
            inp.features = self.collector.collect_features(inp)
        return test_inputs

    def learn_candidates(self, test_inputs: Set[AlhazenInput]) -> ExplanationSet:
        print("Learning candidates")
        return self.learner.learn_explanation(test_inputs)

    def generate_test_inputs(self, explanations: ExplanationSet) -> Set[AlhazenInput]:
        print(f"Generating new test inputs for {len(explanations)} hypotheses.")
        test_inputs = self.engine.generate(explanations=explanations)
        return test_inputs
