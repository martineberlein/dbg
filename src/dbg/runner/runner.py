from abc import ABC, abstractmethod
from typing import Union, Set

from dbg.data.input import Input
from dbg.data.oracle import OracleResult
from dbg.types import OracleType, BatchOracleType


class ExecutionHandler(ABC):
    def __init__(
        self,
        oracle: OracleType | BatchOracleType,
    ):
        self.oracle: Union[OracleType, BatchOracleType] = oracle

    @abstractmethod
    def label(self, **kwargs):
        raise NotImplementedError


class SingleExecutionHandler(ExecutionHandler):
    def _get_label(self, test_input: Input) -> OracleResult:
        return self.oracle(test_input)

    def label(self, test_inputs: Set[Input], **kwargs):
        for inp in test_inputs:
            label = self._get_label(inp)
            inp.oracle = label
        return test_inputs


class BatchExecutionHandler(ExecutionHandler):
    def _get_label(self, test_inputs: Set[Input]) -> list[tuple[Input, OracleResult]]:
        results = self.oracle(test_inputs)

        return [
            (inp, results[inp]) for inp in test_inputs
        ]

    def label(self, test_inputs: Set[Input], **kwargs):
        test_results = self._get_label(test_inputs)

        for inp, test_result in test_results:
            inp.oracle = test_result
        return test_inputs