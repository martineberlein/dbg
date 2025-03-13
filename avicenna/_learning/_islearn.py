from typing import List, Tuple, Optional, Iterable, Set
import itertools

from isla.language import Formula, ConjunctiveFormula
from grammar_graph import gg
from isla import language

from dbg.logger import LOGGER
from dbg.types import Grammar
from dbg.explanation.candidate import ExplanationSet
from dbg.learner.pattern_learner import PatternLearner

from avicenna._data import AvicennaInput
from avicenna._learner import AvicennaExplanation
from avicenna._learning._constructor import AtomicFormulaInstantiation
from avicenna import get_pattern_file_path


class OptimizedISLearnLearner(
    PatternLearner
):

    def __init__(
        self,
        grammar: Grammar,
        pattern_file: str = None,
        min_recall: float = 0.9,
        min_specificity: float = 0.6,
    ):
        if not pattern_file:
            pattern_file = get_pattern_file_path()

        super().__init__(
            grammar,
            patterns=pattern_file,
            min_recall=min_recall,
            min_precision=min_specificity,
        )

        self.atomic_candidate_constructor = AtomicFormulaInstantiation(grammar, pattern_file=pattern_file)

        self.max_conjunction_size = 2
        self.all_negative_inputs: Set[AvicennaInput] = set()
        self.all_positive_inputs: Set[AvicennaInput] = set()
        self.graph = gg.GrammarGraph.from_grammar(grammar)
        self.exclude_nonterminals: Set[str] = set()
        self.positive_examples_for_learning: List[language.DerivationTree] = []

        self.removed_explanations: set[AvicennaExplanation] = set()

    def parse_patterns(self, patterns):
        print(patterns)

    def learn_explanation(self,
          test_inputs: set[AvicennaInput],
          exclude_nonterminals: Optional[Iterable[str]] = None,
          **kwargs
    ) -> Optional[ExplanationSet]:
        """
        Learn candidates from the test inputs.
        """
        positive_inputs, negative_inputs = self.categorize_inputs(test_inputs)
        self.update_inputs(positive_inputs, negative_inputs)
        self.exclude_nonterminals = exclude_nonterminals or set()

        explanations: ExplanationSet = self._learn_invariants(positive_inputs, negative_inputs)
        return explanations

    def update_inputs(self, positive_inputs: set[AvicennaInput], negative_inputs: set[AvicennaInput]):
        self.all_positive_inputs.update(positive_inputs)
        self.all_negative_inputs.update(negative_inputs)

    def _learn_invariants(self,
        positive_inputs: Set[AvicennaInput],
        negative_inputs: Set[AvicennaInput],
    ) -> ExplanationSet[AvicennaExplanation]:

        LOGGER.info("Starting creating atomic candidates")
        atomic_formulas = self.atomic_candidate_constructor.construct_candidates(
            self.all_positive_inputs, self.exclude_nonterminals
        )
        new_explanations = {AvicennaExplanation(formula) for formula in atomic_formulas}
        new_explanations = new_explanations - self.removed_explanations

        LOGGER.info("Starting filtering atomic candidates")
        filtered_explanations = set()
        for explanation in new_explanations:
            explanation.evaluate(self.all_positive_inputs, self.graph)
            if explanation.recall() >= self.min_recall:
                filtered_explanations.add(explanation)
            else:
                self.removed_explanations.add(explanation)

        explanations_to_evaluate: List[AvicennaExplanation] = (
            [] + self.explanations.explanations
        )
        for explanation in filtered_explanations:
            if explanation not in explanations_to_evaluate:
                explanations_to_evaluate.append(explanation)

        LOGGER.info("Evaluating %s candidates", len(explanations_to_evaluate))
        self.validate_and_add_new_candidates(
            explanations_to_evaluate, positive_inputs, negative_inputs
        )

        conjunction_candidates = self.get_conjunctions(self.explanations)
        for candidate in conjunction_candidates:
            self.explanations.append(candidate)

        return self.explanations

    def validate_and_add_new_candidates(
            self,
            candidates: List[AvicennaExplanation],
            positive_inputs: set[AvicennaInput],
            negative_inputs: set[AvicennaInput],
    ) -> None:
        """
        Generates constraint candidates based on instantiated patterns and evaluates them.

        Args:
            candidates (Set[FandangoConstraintCandidate]): A set of new candidates.
            positive_inputs (Set[FandangoInput]): A set of positive inputs.
            negative_inputs (Set[FandangoInput]): A set of negative inputs.
        """
        for candidate in candidates:
            if candidate not in self.explanations:
                if self.evaluate_candidate(
                        candidate, self.all_positive_inputs, self.all_negative_inputs
                ):
                    self.explanations.append(candidate)
                    LOGGER.debug("Added new candidate: %s", candidate)
                else:
                    self.removed_explanations.add(candidate)
            else:
                if not self.evaluate_candidate(
                        candidate, positive_inputs, negative_inputs
                ):
                    self.explanations.remove(candidate)
                    self.removed_explanations.add(candidate)

    def evaluate_candidate(
            self, candidate: AvicennaExplanation, positive_inputs, negative_inputs
    ):
        try:
            candidate.evaluate(positive_inputs, graph=self.graph)
            if candidate.recall() >= self.min_recall:
                candidate.evaluate(negative_inputs, graph=self.graph)
                return True
        except Exception as e:
            LOGGER.info(
                "Error when evaluation candidate %s: %s", candidate.explanation, e
            )
        return False

    def sort_candidates(self):
        """
        Sorts the candidates based on the sorting strategy.
        """
        sorted_candidates = sorted(
            self.explanations,
            key=lambda candidate: candidate.with_strategy(self.sorting_strategy),
            reverse=True,
        )
        return sorted_candidates

    def get_disjunctions(self):
        """
        Calculate the disjunctions of the formulas.
        """
        pass

    def check_minimum_recall(self, candidates: tuple[AvicennaExplanation, ...]) -> bool:
        """
        Check if the recall of the candidates in the combination is greater than the minimum
        """
        return all(candidate.recall() >= self.min_recall for candidate in candidates)

    def is_new_conjunction_valid(
        self, conjunction: AvicennaExplanation, combination: tuple[AvicennaExplanation, ...]
    ) -> bool:
        """
        Check if the new conjunction is valid based on the minimum specificity and the recall of the candidates in
        the combination. The specificity of the new conjunction should be greater than the minimum specificity and
        the specificity of the conjunction should be greater than the specificity of the individual formula.
        """
        new_specificity = conjunction.specificity()
        return new_specificity >= self.min_precision and all(
            new_specificity > candidate.specificity() for candidate in combination
        )

    def get_conjunctions(
        self, explanations: ExplanationSet[AvicennaExplanation]
    ) -> list[AvicennaExplanation]:
        conjunctions: list[AvicennaExplanation] = []

        combinations = self.get_possible_conjunctions(explanations)

        con_counter = 0
        for combination in combinations:
            # check min recall
            if not self.check_minimum_recall(combination):
                continue
            conjunction: AvicennaExplanation = combination[0]
            for candidate in combination[1:]:
                conjunction = conjunction & candidate

            conjunction.explanation = language.ensure_unique_bound_variables(
                conjunction.explanation
            )

            if self.is_new_conjunction_valid(conjunction, combination):
                con_counter += 1
                conjunctions.append(conjunction)


        return conjunctions

    def get_possible_conjunctions(self, explanation_set: ExplanationSet[AvicennaExplanation]) -> List[Tuple[AvicennaExplanation, ...]]:
        """
        Get all possible conjunctions of the candidate set with a maximum size of max_conjunction_size.
        """
        combinations = []
        candidate_set_without_conjunctions = [
            explanation
            for explanation in explanation_set
            if not isinstance(explanation.explanation, ConjunctiveFormula)
        ]
        for level in range(2, self.max_conjunction_size + 1):
            for comb in itertools.combinations(
                candidate_set_without_conjunctions, level
            ):
                combinations.append(comb)
        return combinations

    def reset(self):
        """
        Reset the learner to its initial state.
        """
        self.all_negative_inputs: Set[AvicennaInput] = set()
        self.all_positive_inputs: Set[AvicennaInput] = set()
        self.exclude_nonterminals: Set[str] = set()
        self.positive_examples_for_learning: List[language.DerivationTree] = []
        self.explanations = ExplanationSet()
        self.removed_explanations = set()
        super().reset()
