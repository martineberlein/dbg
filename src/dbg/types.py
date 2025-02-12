from typing import Callable, Union

from dbg.data.input import Input
from dbg.data.oracle import OracleResult

OracleType = Callable[[Union[Input, str]], OracleResult]
BatchOracleType = Callable[[Union[set[Input], set[str]]], dict[Input, OracleResult]]
