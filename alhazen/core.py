from typing import Set, Union, Iterable, Optional

from dbg.core import HypothesisBasedExplainer
from dbg.data.input import Input, OracleResult
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType

from alhazen._learner import AlhazenLearner
from alhazen._generator import AlhazenGenerator
from alhazen import Grammar
from alhazen._data import AlhazenInput
from alhazen.features.collector import GrammarFeatureCollector


class Alhazen(HypothesisBasedExplainer):

    def __init__(self, grammar: Grammar, oracle: OracleType,
                 initial_inputs: Union[Iterable[str], Iterable[Input]],
                 **kwargs):

        learner = AlhazenLearner()
        generator = AlhazenGenerator(grammar)
        super().__init__(grammar, oracle, initial_inputs, learner, generator, **kwargs)

        self.collector = GrammarFeatureCollector(grammar)

    def set_initial_inputs(self, test_inputs: Iterable[str]) -> set[Input]:
        return {AlhazenInput.from_str(self.grammar, inp, self.oracle(inp)) for inp in test_inputs}

    def prepare_test_inputs(self, test_inputs: set[AlhazenInput]) -> Set[AlhazenInput]:
        for inp in test_inputs:
            inp.features = self.collector.collect_features(inp)
        return test_inputs

    def learn_candidates(self, test_inputs: Set[AlhazenInput]) -> ExplanationSet:
        print("Learning candidates")
        return self.learner.learn_explanation(test_inputs)
        pass

    def generate_test_inputs(self, candidates: ExplanationSet) -> Set[Input]:
        pass

    def run_test_inputs(self, test_inputs: Set[Input]) -> Set[Input]:
        pass



if __name__ == "__main__":
    from fuzzingbook.GrammarFuzzer import is_valid_grammar
    import math

    def oracle(inp: AlhazenInput | str) -> OracleResult:
        try:
            eval(str(inp), {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan})
            return OracleResult.PASSING
        except ValueError:
            return OracleResult.FAILING

    grammar_alhazen = {
        "<start>": ["<arith_expr>"],
        "<arith_expr>": ["<function>(<number>)"],
        "<function>": ["sqrt", "sin", "cos", "tan"],
        "<number>": ["<maybe_minus><onenine><maybe_digits><maybe_frac>"],
        "<maybe_minus>": ["", "-"],
        "<onenine>": [str(num) for num in range(1, 10)],
        "<digit>": [str(num) for num in range(0, 10)],
        "<maybe_digits>": ["", "<digits>"],
        "<digits>": ["<digit>", "<digit><digits>"],
        "<maybe_frac>": ["", ".<digits>"],
    }
    is_valid_grammar(grammar_alhazen)

    from fuzzingbook.GrammarFuzzer import GrammarFuzzer

    initial_inputs = ["sqrt(-900)", "sin(-3)", "cos(10)", "tan(5)"]
    for _ in range(100):
        initial_inputs.append(GrammarFuzzer(grammar_alhazen).fuzz())

    alhazen = Alhazen(
        grammar=grammar_alhazen,
        initial_inputs=initial_inputs,
        oracle=oracle,
    )

    diagnosis = alhazen.explain()
