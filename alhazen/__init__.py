import re
import math

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


def tree_to_if_then_statement(clf, feature_names: list[str], indent_: int = 0) -> str:
    """
    Transforms a sklearn DecisionTreeClassifier into a readable if-else statement.

    Args:
        clf (DecisionTreeClassifier): The trained decision tree classifier.
        feature_names (List[str]): List of feature names corresponding to tree features.
        indent_ (int, optional): The starting indentation level. Defaults to 0.

    Returns:
        str: Readable if-else representation of the decision tree.
    """
    class_names = [str(OracleResult.PASSING), str(OracleResult.FAILING)]

    def _tree(index: int, indent: int) -> str:
        """Recursive function to traverse the decision tree and generate if-else statements."""
        tree = clf.tree_
        feature = tree.feature[index]

        # Leaf node check
        if feature == -2:
            class_ = int(tree.value[index][0][0])
            return " " * indent + class_names[class_] + "\n"

        feature_name = feature_names[feature]
        threshold = tree.threshold[index]
        left, right = tree.children_left[index], tree.children_right[index]

        s = " " * indent
        if math.isclose(threshold, 0.5):
            s += f"if {feature_name}:\n"
            s += _tree(right, indent + 2)
            s += " " * indent + "else:\n"
            s += _tree(left, indent + 2)
        else:
            s += f"if {feature_name} <= {threshold:.4f}:\n"
            s += _tree(left, indent + 2)
            s += " " * indent + "else:\n"
            s += _tree(right, indent + 2)

        return s

    return _tree(0, indent_)
