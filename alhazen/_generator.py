import numpy as np
from itertools import product
from fuzzingbook.GrammarFuzzer import GrammarFuzzer

from dbg.explanation.candidate import ExplanationSet
from dbg.generator.generator import Generator

from alhazen import Grammar
from alhazen._data import AlhazenInput


class AlhazenGenerator(Generator):

    def __init__(self, grammar: Grammar, **kwargs):
        super().__init__(grammar, **kwargs)
        self.fuzzer = GrammarFuzzer(grammar)

    def generate(self, explanation, *args, **kwargs):
        return AlhazenInput(self.fuzzer.fuzz_tree())


class Property:

    def __init__(self, feature, operator, value):
        self.feature = feature
        self.operator = operator
        self.value = value

    def __str__(self):
        return f"{self.feature} {self.operator} {self.value}"

    def __neg__(self):
        operator = "<=" if self.operator == ">" else ">"
        return Property(self.feature, operator, self.value)


class HypothesisProducer:

    def produce(self, explanations: ExplanationSet) -> list[list[Property]]:
        positive = []
        for explanation in explanations:
            positive_hypotheses = get_positive_paths(explanation.explanation, explanation.feature_names)
            positive.extend(positive_hypotheses)

        negated = []
        for hypothesis in positive:
            negated_hypotheses: list[list[Property]] = self.negate(hypothesis)
            negated.extend(negated_hypotheses)

        hypotheses = positive + negated
        return hypotheses

    @staticmethod
    def negate(hypothesis: list[Property]) -> list[list[Property]]:
        negated_hypotheses = [
            [-prop if bit else prop for prop, bit in zip(hypothesis, combination)]
            for combination in product([0, 1], repeat=len(hypothesis))
            if any(combination)
        ]
        return negated_hypotheses

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
                paths.append(path)
            return

        # Get child nodes
        left, right = tree_.children_left[node], tree_.children_right[node]

        # Get predicted classes for left and right nodes
        left_prediction = int(np.argmax(tree_.value[left]))
        right_prediction = int(np.argmax(tree_.value[right]))

        # Stop if both children predict the same class (redundant split)
        if remove_redundant_split and left_prediction == right_prediction:
            if left_prediction == class_label:
                paths.append(path)
            return

        # Otherwise, continue traversing
        feature = feature_names[tree_.feature[node]]
        threshold = tree_.threshold[node]

        traverse(left, path + [Property(feature, "<=", threshold)])
        traverse(right, path + [Property(feature, ">", threshold)])

    paths = []
    traverse(0, [])
    return paths