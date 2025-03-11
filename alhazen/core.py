from typing import Set, Iterable
import numpy as np

from dbg.core import HypothesisBasedExplainer
from dbg.explanation.candidate import ExplanationSet
from dbg.types import OracleType
from dbg.logger import LOGGER

from alhazen._learner import AlhazenLearner
from alhazen._generator import AlhazenGenerator
from alhazen import Grammar
from alhazen._data import AlhazenInput
from alhazen.features.collector import GrammarFeatureCollector


class Alhazen(HypothesisBasedExplainer):
    """
    Alhazen is an implementation of a hypothesis-based explanation system.
    It utilizes a learner, generator, and grammar-based feature collection
    to generate test inputs and derive explanations.
    """

    def __init__(
        self,
        grammar: Grammar,
        oracle: OracleType,
        initial_inputs: Iterable[str],
        **kwargs,
    ):
        """
        Initializes the Alhazen explainer.

        Args:
            grammar (Grammar): The grammar used to generate test inputs.
            oracle (OracleType): The oracle function to classify test inputs.
            initial_inputs (Iterable[str]): The initial set of test inputs.
            **kwargs: Additional parameters for the parent class.
        """
        learner = AlhazenLearner()
        generator = AlhazenGenerator(grammar)

        super().__init__(grammar, oracle, initial_inputs, learner, generator, **kwargs)

        self.collector = GrammarFeatureCollector(grammar)

    def set_initial_inputs(self, test_inputs: Iterable[str]) -> set[AlhazenInput]:
        """
        Converts a set of string test inputs into AlhazenInput objects,
        incorporating oracle classification.

        Args:
            test_inputs (Iterable[str]): The test inputs as strings.

        Returns:
            set[AlhazenInput]: The converted test inputs as AlhazenInput objects.
        """
        return {
            AlhazenInput.from_str(self.grammar, inp, self.oracle(inp))
            for inp in test_inputs
        }

    def prepare_test_inputs(self, test_inputs: set[AlhazenInput]) -> Set[AlhazenInput]:
        """
        Prepares test inputs by collecting their grammar-based features.

        Args:
            test_inputs (set[AlhazenInput]): The test inputs to process.

        Returns:
            Set[AlhazenInput]: The updated set of test inputs with extracted features.
        """
        for inp in test_inputs:
            inp.features = self.collector.collect_features(inp)
        return test_inputs

    def learn_candidates(self, test_inputs: Set[AlhazenInput]) -> ExplanationSet:
        """
        Learns the decision tree from the given test inputs.

        Args:
            test_inputs (Set[AlhazenInput]): The set of test inputs to analyze.

        Returns:
            ExplanationSet: The learned decision tree
        """
        LOGGER.info("Learning candidates.")
        explanations = self.learner.learn_explanation(test_inputs)
        return explanations

    def generate_test_inputs(self, explanations: ExplanationSet) -> Set[AlhazenInput]:
        """
        Generates new test inputs based on a given set of explanations.

        Args:
            explanations (ExplanationSet): The explanations to guide test generation.

        Returns:
            Set[AlhazenInput]: The generated test inputs.
        """
        LOGGER.info("Generating test inputs.")
        test_inputs = self.engine.generate(explanations=explanations)
        return test_inputs

    def create_hypotheses(self, explanations: ExplanationSet) -> ExplanationSet:
        """
        Creates new hypotheses based on the learned decision tree.
        """
        for explanation in explanations:
            paths = get_positive_paths(explanation.explanation, explanation.feature_names)
            print(str(explanation))
            for path in paths:
                print(path)
        return explanations


def get_positive_paths(tree, feature_names=None, class_label=0, remove_redundant_split: bool=True):
    """Extracts paths leading to a positive prediction (class_label).

    Args:
        tree: Fitted DecisionTreeClassifier model.
        feature_names: List of feature names.
        class_label: The target class for which to extract paths.
        remove_redundant_split: Whether to remove redundant splits.

    Returns:
        A list of paths as readable conditions.
    """
    tree_ = tree.tree_
    if feature_names is None:
        feature_names = [f'feature_{i}' for i in range(tree_.n_features_in_)]

    def traverse(node, path):
        if tree_.feature[node] == -2:  # Leaf node
            predicted_class = np.argmax(tree_.value[node])  # Get predicted class
            if predicted_class == class_label:
                paths.append(" AND ".join(path))
            return

        # Get child nodes
        left, right = tree_.children_left[node], tree_.children_right[node]

        # Get predicted classes for left and right nodes
        left_prediction = int(np.argmax(tree_.value[left]))
        right_prediction = int(np.argmax(tree_.value[right]))

        # Stop if both children predict the same class (redundant split)
        if remove_redundant_split and left_prediction == right_prediction:
            if left_prediction == class_label:
                paths.append(" AND ".join(path))
            return

        # Otherwise, continue traversing
        feature = feature_names[tree_.feature[node]]
        threshold = tree_.threshold[node]

        traverse(left, path + [f"{feature} <= {threshold:.2f}"])
        traverse(right, path + [f"{feature} > {threshold:.2f}"])

    paths = []
    traverse(0, [])
    return paths