from fuzzingbook.GrammarFuzzer import GrammarFuzzer

from dbg.generator.generator import Generator

from alhazen import Grammar
from alhazen._data import AlhazenInput


class AlhazenGenerator(Generator):

    def __init__(self, grammar: Grammar, **kwargs):
        super().__init__(grammar, **kwargs)
        self.fuzzer = GrammarFuzzer(grammar)

    def generate(self, *args, **kwargs):
        return AlhazenInput(self.fuzzer.fuzz_tree())
