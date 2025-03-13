"""
The learning module provides the necessary tools to learn new failure inducing candidates.
"""
from isla.derivation_tree import DerivationTree, is_nonterminal
from isla.parser import EarleyParser
from isla.solver import ISLaSolver

import re
Grammar = dict[str, list[str]]
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



import importlib.resources as pkg_resources


def get_pattern_file_path():
    return pkg_resources.files("avicenna") / "patterns.toml"


def get_islearn_pattern_file_path():
    return pkg_resources.files("avicenna") / "patterns_islearn.toml"
