from alhazen.core import Alhazen
from alhazen._data import AlhazenInput, OracleResult


if __name__ == "__main__":
    from fuzzingbook.GrammarFuzzer import is_valid_grammar
    import math

    def oracle(inp: AlhazenInput | str) -> OracleResult:
        try:
            eval(
                str(inp),
                {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan},
            )
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

    initial_inputs = ["sqrt(-900)", "sin(-3)", "cos(10)", "tan(5)"]

    alhazen = Alhazen(
        grammar=grammar_alhazen,
        initial_inputs=initial_inputs,
        oracle=oracle,
        max_iterations=20,
    )

    diagnosis = alhazen.explain()
