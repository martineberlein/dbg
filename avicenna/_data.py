from typing import Optional

from dbg.data.input import Input
from dbg.data.oracle import OracleResult


class AvicennaInput(Input):
    def __hash__(self) -> int:
        pass

    @classmethod
    def from_str(cls, grammar, input_string, oracle: Optional[OracleResult] = None):
        pass