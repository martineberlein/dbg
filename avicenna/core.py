from typing import Iterable, Set



from dbg.core import HypothesisBasedExplainer
from dbg.logger import LOGGER
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType, Grammar

from avicenna._data import AvicennaInput
from avicenna.features.feature_collector import GrammarFeatureCollector


class Avicenna(HypothesisBasedExplainer):
    """
    Avicenna is a hypothesis-based input feature debugger that uses a pattern-based candidate learner to explain
    the input features that result in the failure of a program.
    """

    def __init__(
        self,
        grammar: Grammar,
        oracle: OracleType,
        initial_inputs: Iterable[AvicennaInput | str],
        top_n_relevant_features: int = 3,
        min_recall: float = 0.9,
        min_specificity: float = 0.6,
        **kwargs,
    ):
        learner = ExhaustivePatternCandidateLearner()
        generator = ISLaGrammarBasedGenerator(grammar)

        super().__init__(
            grammar,
            oracle,
            initial_inputs,
            learner=learner,
            generator=generator,
            **kwargs,
        )

        self.feature_learner = DecisionTreeRelevanceLearner(
            self.grammar,
            top_n_relevant_features=top_n_relevant_features,
        )
        self.collector = GrammarFeatureCollector(self.grammar)

    def set_initial_inputs(self, test_inputs: Iterable[str]) -> set[AvicennaInput]:
        """
        Converts a set of string test inputs into AlhazenInput objects,
        incorporating oracle classification.

        Args:
            test_inputs (Iterable[str]): The test inputs as strings.

        Returns:
            set[AlhazenInput]: The converted test inputs as AlhazenInput objects.
        """
        return {
            AvicennaInput.from_str(self.grammar, inp, self.oracle(inp))
            for inp in test_inputs
        }

    def prepare_test_inputs(self, test_inputs: set[AvicennaInput]) -> set[AvicennaInput]:
        """
        Prepares test inputs by collecting their grammar-based features.

        Args:
            test_inputs (set[AvicennaInput]): The test inputs to process.

        Returns:
            Set[AlhazenInput]: The updated set of test inputs with extracted features.
        """
        for inp in test_inputs:
            inp.features = self.collector.collect_features(inp)
        return test_inputs

    def get_relevant_features(self, test_inputs: Set[AvicennaInput]) -> Set[str]:
        """
        Get the relevant features based on the test inputs.
        """
        relevant_features = self.feature_learner.learn(test_inputs)
        relevant_feature_non_terminals = {
            feature.non_terminal for feature in relevant_features
        }
        return relevant_feature_non_terminals

    def get_irrelevant_features(self, test_inputs: Set[AvicennaInput]) -> Set[str]:
        """
        Get the irrelevant features based on the test inputs.
        """
        relevant_feature_non_terminals = self.get_relevant_features(test_inputs)

        irrelevant_features = set(self.grammar.keys()).difference(
            relevant_feature_non_terminals
        )
        return irrelevant_features

    def learn_candidates(self, test_inputs: Set[AvicennaInput]) -> ExplanationSet:
        """
        Learn the candidates based on the test inputs. The candidates are ordered based on their scores.
        :param test_inputs: The test inputs to learn the candidates from.
        :return Optional[List[Candidate]]: The learned candidates.
        """
        irrelevant_features = self.get_irrelevant_features(test_inputs)
        _ = self.learner.learn_explanation(
            test_inputs, exclude_nonterminals=irrelevant_features
        )
        explanations = self.learner.get_best_candidates()
        return explanations

    def generate_test_inputs(self, explanations: ExplanationSet) -> Set[AvicennaInput]:
        """
        Generate the test inputs based on the learned candidates.
        :param explanations: The learned explanations.
        :return Set[Input]: The generated test inputs.
        """
        LOGGER.info("Generating test inputs.")
        test_inputs = self.engine.generate(explanations=explanations)
        return test_inputs
