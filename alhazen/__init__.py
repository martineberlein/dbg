from typing import Optional
import re

from dbg.data.input import Input
from dbg.data.oracle import OracleResult

Grammar = dict[str, list[str]]
DerivationTree = tuple[str, list["DerivationTree"]]
START_SYMBOL = "<start>"
RE_NONTERMINAL = re.compile(r"(<[^<> ]*>)")


def nonterminals(expansion: str):
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)


def reachable_nonterminals(
    grammar: Grammar, start_symbol: str = START_SYMBOL
) -> set[str]:
    reachable = set()

    def _find_reachable_nonterminals(_grammar, symbol):
        nonlocal reachable
        reachable.add(symbol)
        for expansion in _grammar.get(symbol, []):
            for nonterminal in nonterminals(expansion):
                if nonterminal not in reachable:
                    _find_reachable_nonterminals(_grammar, nonterminal)

    _find_reachable_nonterminals(grammar, start_symbol)
    return reachable


def is_nonterminal(s):
    return RE_NONTERMINAL.match(s)


def tree_to_string(tree: DerivationTree) -> str:
    symbol, children, *_ = tree
    if children:
        return ''.join(tree_to_string(c) for c in children)
    else:
        return '' if is_nonterminal(symbol) else symbol
