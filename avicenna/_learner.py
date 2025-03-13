from typing import Iterable, Optional

from dbg.data.input import Input
from dbg.explanation.candidate import Explanation, ExplanationSet
from dbg.learner.learner import Learner
from dbg.data.oracle import OracleResult

from isla.evaluator import evaluate
from isla.language import ISLaUnparser
from grammar_graph import gg

from avicenna._data import AvicennaInput


class AvicennaExplanation(Explanation):

    def __init__(
            self, explanation: Explanation, failing_inputs_eval_results: list[bool]=None,
            passing_inputs_eval_results: list[bool]=None, cache: dict[Input, bool]=None
            ):
        super().__init__(explanation)
        self.explanation = explanation
        self.failing_inputs_eval_results = failing_inputs_eval_results or []
        self.passing_inputs_eval_results = passing_inputs_eval_results or []
        self.cache = cache or {}

    def evaluate(self, test_inputs: set[AvicennaInput], graph: gg.GrammarGraph = None, **kwargs):
        for inp in test_inputs:
            if inp in self.cache:
                continue
            eval_result = evaluate(
                self.explanation, inp.tree, graph.grammar, graph=graph
            ).is_true()
            self._update_eval_results(eval_result, inp)

    def _update_eval_results(self, eval_result: bool, inp: Input):
        """
        Update the evaluation results and combination with a new input and its evaluation result.
        """
        if inp.oracle == OracleResult.FAILING:
            self.failing_inputs_eval_results.append(eval_result)
        else:
            self.passing_inputs_eval_results.append(eval_result)
        self.cache[inp] = eval_result

    def __neg__(self):
        """
        Return the negation of the candidate formula.
        """
        new_cache = {inp: not result for inp, result in self.cache.items()}
        failing = [not eval_result for eval_result in self.failing_inputs_eval_results]
        passing = [not eval_result for eval_result in self.passing_inputs_eval_results]

        negated_explanation = -self.explanation
        return self.__new_explanation(negated_explanation, failing, passing, new_cache)

    def __and__(self, other):
        """
        Return the conjunction of the candidate formula with another candidate formula.
        """
        new_cache = {}
        failing = []
        passing = []

        for inp in self.cache.keys():
            r = self.cache[inp] and other.cache[inp]
            if inp.oracle == OracleResult.FAILING:
                failing.append(r)
            else:
                passing.append(r)
            new_cache[inp] = r

        conjunction = self.explanation & other.explanation
        return self.__new_explanation(conjunction, failing, passing, new_cache)

    def __or__(self, other):
        """
        Return the disjunction of the candidate formula with another candidate formula.
        """
        new_cache = {inp: result or other.cache[inp] for inp, result in self.cache.items()}
        failing = [eval_result or other.cache[inp] for inp, eval_result in self.failing_inputs_eval_results]
        passing = [eval_result or other.cache[inp] for inp, eval_result in self.passing_inputs_eval_results]

        disjunction = self.explanation | other.explanation
        return self.__new_explanation(disjunction, failing, passing, new_cache)

    @staticmethod
    def __new_explanation(explanation, failing_inputs_eval_results, passing_inputs_eval_results, cache):
        return AvicennaExplanation(explanation=explanation, failing_inputs_eval_results=failing_inputs_eval_results, passing_inputs_eval_results=passing_inputs_eval_results, cache=cache)

    def __repr__(self):
        return f"AvicennaExplanation({ISLaUnparser(self.explanation).unparse()})"

    def __str__(self):
        return ISLaUnparser(self.explanation).unparse()


class AvicennaLearner(Learner):
    def learn_explanation(self, test_inputs: Iterable[Input], **kwargs) -> Optional[ExplanationSet]:
        pass

