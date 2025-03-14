import time
from abc import ABC, abstractmethod
from queue import Queue, Empty
from typing import Set, Union, List

from dbg.data.input import Input
from dbg.explanation.candidate import Explanation
from dbg.data.grammar import AbstractGrammar


class Generator(ABC):
    """
    A generator is responsible for generating inputs to be used in the debugging process.
    """

    def __init__(self, grammar: AbstractGrammar, **kwargs):
        """
        Initialize the generator with a grammar.
        """
        self.grammar = grammar

    @abstractmethod
    def generate(self, *args, **kwargs) -> Input:
        """
        Generate an input to be used in the debugging process.
        """
        raise NotImplementedError

    def generate_test_inputs(self, num_inputs: int = 2, **kwargs) -> Set[Input]:
        """
        Generate multiple inputs to be used in the debugging process.
        """
        test_inputs = set()
        for _ in range(num_inputs):
            inp = self.generate(**kwargs)
            if inp:
                test_inputs.add(inp)
        return test_inputs

    def run_with_engine(self, candidate_queue: Queue[Explanation], output_queue: Union[Queue, List]):
        """
        Run the generator within an engine. This is useful for parallelizing the generation process.
        :param candidate_queue:
        :param output_queue:
        :return:
        """
        try:
            while True:
                test_inputs = self.generate_test_inputs(explanation=candidate_queue.get_nowait())
                if isinstance(output_queue, Queue):
                    output_queue.put(test_inputs)
                else:
                    output_queue.append(test_inputs)
        except Empty:
            pass

    def reset(self, **kwargs):
        """
        Reset the generator.
        """
        pass
