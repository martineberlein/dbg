from typing import Set, Optional



from dbg.generator.generator import Generator


class ISLaSolverGenerator(Generator):
    """
    A generator that uses the ISLa Solver to generate inputs.
    """

    def __init__(self, grammar: Grammar, enable_optimized_z3_queries=False, **kwargs):
        super().__init__(grammar)
        self.solver: Optional[ISLaSolver] = None
        self.enable_optimized_z3_queries = enable_optimized_z3_queries

    def generate(self, **kwargs) -> Optional[Input]:
        """
        Generate an input to be used in the debugging process using the ISLa Solver.
        """
        try:
            tree = self.solver.solve()
            return Input(tree=tree)
        except (StopIteration, RuntimeError):
            return None

    def generate_test_inputs(
        self, num_inputs: int = 5, candidate: Candidate = None, **kwargs
    ) -> Set[Input]:
        """
        Generate multiple inputs to be used in the debugging process.
        """
        test_inputs = set()
        if candidate is not None:
            self.initialize_solver(candidate.formula)
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
