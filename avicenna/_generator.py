from typing import Set, Optional

from isla.fuzzer import GrammarFuzzer

from dbg.generator.generator import Generator
from dbg.types import Grammar

from avicenna import ISLaSolver
from avicenna._data import AvicennaInput
from avicenna._learner import AvicennaExplanation


class AvicennaGenerator(Generator):
    """
    A generator that uses the ISLa Solver to generate inputs.
    """

    def __init__(self, grammar: Grammar, enable_optimized_z3_queries=False, **kwargs):
        super().__init__(grammar)
        self.solver: Optional[ISLaSolver] = None
        self.enable_optimized_z3_queries = enable_optimized_z3_queries

    def generate(self, **kwargs) -> Optional[AvicennaInput]:
        """
        Generate an input to be used in the debugging process using the ISLa Solver.
        """
        try:
            tree = self.solver.solve()
            return AvicennaInput(tree=tree)
        except (StopIteration, RuntimeError):
            return None

    def generate_test_inputs(
        self, num_inputs: int = 5, explanation: AvicennaExplanation = None, **kwargs
    ) -> Set[AvicennaInput]:
        """
        Generate multiple inputs to be used in the debugging process.
        """
        test_inputs = set()
        if explanation is not None:
            self.initialize_solver(explanation.explanation)
            for _ in range(num_inputs):
                inp = self.generate(**kwargs)
                if inp:
                    test_inputs.add(inp)
        return test_inputs

    def initialize_solver(self, constraint):
        """
        Reset the generator with a new constraint.
        """
        self.solver = ISLaSolver(
            self.grammar,
            constraint,
            enable_optimized_z3_queries=self.enable_optimized_z3_queries,
        )


class AvicennaISLaGrammarBasedGenerator(Generator):
    """
    A generator that uses the ISLa Grammar-based Fuzzer to generate inputs.
    This generator directly produces the derivation trees, which is more efficient than the FuzzingbookBasedGenerator.
    """

    def __init__(self, grammar: Grammar, **kwargs):
        super().__init__(grammar)
        self.fuzzer = GrammarFuzzer(grammar, max_nonterminals=20)

    def generate(self, **kwargs) -> AvicennaInput:
        """
        Generate an input to be used in the debugging process.
        """
        return AvicennaInput(tree=self.fuzzer.fuzz_tree())