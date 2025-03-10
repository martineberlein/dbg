from typing import Set, Union, Iterable

from dbg.core import HypothesisBasedExplainer
from dbg.data.input import Input
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType

from alhazen._learner import AlhazenLearner
from alhazen._generator import AlhazenGenerator
from alhazen import Grammar


class Alhazen(HypothesisBasedExplainer):

    def __init__(self, grammar: Grammar, oracle: OracleType,
                 initial_inputs: Union[Iterable[str], Iterable[Input]],
                 **kwargs):

        learner = AlhazenLearner()
        generator = AlhazenGenerator(grammar)
        super().__init__(grammar, oracle, initial_inputs, learner, generator, **kwargs)

    def learn_candidates(self, test_inputs: Set[Input]) -> ExplanationSet:
        pass

    def generate_test_inputs(self, candidates: ExplanationSet) -> Set[Input]:
        pass



if __name__ == "__main__":


    alhazen = Alhazen()
