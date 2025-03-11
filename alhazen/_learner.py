from typing import Iterable, Optional
from abc import ABC, abstractmethod
import math

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from dbg.explanation.candidate import ExplanationSet, Explanation
from dbg.learner.learner import Learner
from dbg.data.oracle import OracleResult

from alhazen._data import AlhazenInput


class AlhazenExplanation(Explanation):

    def __init__(self, explanation: DecisionTreeClassifier):
        super().__init__(explanation)
        self.failing_inputs_eval_results = []
        self.passing_inputs_eval_results = []
        self.cache: dict[AlhazenInput, bool] = {}

    def evaluate(self, inputs):
        for inp in inputs:
            if inp in self.cache.keys():
                continue
            eval_result = self.explanation.predict(pd.DataFrame.from_records([{**inp.features.features}]))[0]
            eval_result = True if eval_result == str(OracleResult.FAILING) else False
            if inp.oracle == OracleResult.FAILING:
                self.failing_inputs_eval_results.append(eval_result)
            else:
                self.passing_inputs_eval_results.append(eval_result)
            self.cache[inp] = eval_result

    def __neg__(self):
        return self


class AlhazenLearner(Learner):

    def get_best_candidates(self) -> Optional[ExplanationSet]:
        pass

    def get_explanations(self) -> Optional[ExplanationSet]:
        pass

    def learn_explanation(self, test_inputs: set[AlhazenInput], **kwargs) -> Optional[ExplanationSet]:
        sk_learner = DecisionTreeLearner()
        diagnosis = sk_learner.train(test_inputs)
        sk_learner.print_decision_tree(diagnosis)
        explanation = AlhazenExplanation(diagnosis)
        explanation.evaluate(test_inputs)
        print(f"Explanation achieved: {explanation.precision()} Precision, {explanation.recall()} Recall")
        return ExplanationSet([explanation])


class SKLearnLearner(ABC):
    """Abstract base class for machine learning-based learners."""

    def __init__(self):
        self.data = pd.DataFrame()

    def train(self, test_inputs: Iterable[AlhazenInput], **kwargs):
        """Trains a model based on test inputs."""
        pass

    def _update_data(self, test_inputs: Iterable[AlhazenInput]) -> pd.DataFrame:
        """Updates and returns the training data DataFrame."""
        data_records = [
            {**inp.features.features, "oracle": inp.oracle}
            for inp in test_inputs
            if inp.oracle != OracleResult.UNDEFINED
        ]

        if data_records:
            new_data = pd.DataFrame.from_records(data_records)
            self.data = pd.concat([self.data, new_data], sort=False) if not self.data.empty else new_data

        return self.data


class DecisionTreeLearner(SKLearnLearner):
    """Decision tree learner using scikit-learn's DecisionTreeClassifier."""

    def __init__(
        self,
        min_sample_leaf: int = 1,
        min_samples_split: int = 2,
        max_features=None,
        max_depth: int = 5,
    ):
        super().__init__()
        self.min_sample_leaf = min_sample_leaf
        self.min_sample_split = min_samples_split
        self.max_features = max_features
        self.max_depth = max_depth

        self.clf: Optional[DecisionTreeClassifier] = None

    @staticmethod
    def _compute_class_weights(data: pd.DataFrame, test_inputs: set[AlhazenInput]) -> dict:
        """Computes class weights based on the distribution of failing and passing samples."""
        sample_bug_count = sum(1 for x in test_inputs if x.oracle == OracleResult.FAILING)
        sample_count = len(data)

        # if sample_bug_count == 0 or sample_count - sample_bug_count == 0:
        #     return None  # Avoid division by zero if data is imbalanced

        return {
            str(OracleResult.FAILING): 1.0 / sample_bug_count,
            str(OracleResult.PASSING): 1.0 / (sample_count - sample_bug_count),
        }

    def train(self, test_inputs: set[AlhazenInput], **kwargs) -> DecisionTreeClassifier:
        """
        Trains and returns a DecisionTreeClassifier on the provided test inputs.
        """
        data = self._update_data(test_inputs)
        if data.empty:
            raise ValueError("No valid data available for training.")

        data.fillna(0, inplace=True)
        x_train, y_train = data.drop(columns=["oracle"]), data["oracle"].astype(str)

        class_weights = self._compute_class_weights(data, test_inputs)

        self.clf = DecisionTreeClassifier(
            min_samples_leaf=self.min_sample_leaf,
            min_samples_split=self.min_sample_split,
            max_features=self.max_features,
            max_depth=self.max_depth,
            class_weight=class_weights,
        )

        self.clf.fit(x_train, y_train)
        return self.clf

    def print_decision_tree(self, tree: DecisionTreeClassifier=None):
        if tree is None:
            tree = self.clf
        print(self._friendly_decision_tree(tree, self.data.columns))

    @staticmethod
    def _friendly_decision_tree(clf, feature_names,
                               class_names=None,
                               indent=0):
        if class_names is None:
            class_names = [str(OracleResult.PASSING), str(OracleResult.FAILING)]
        def _tree(index, indent):
            s = ""
            feature = clf.tree_.feature[index]
            feature_name = feature_names[feature]
            threshold = clf.tree_.threshold[index]
            value = clf.tree_.value[index]
            class_ = int(value[0][0])
            class_name = class_names[class_]
            left = clf.tree_.children_left[index]
            right = clf.tree_.children_right[index]
            if left == right:
                # Leaf node
                s += " " * indent + class_name + "\n"
            else:
                if math.isclose(threshold, 0.5):
                    s += " " * indent + f"if {feature_name}:\n"
                    s += _tree(right, indent + 2)
                    s += " " * indent + f"else:\n"
                    s += _tree(left, indent + 2)
                else:
                    s += " " * indent + f"if {feature_name} <= {threshold:.4f}:\n"
                    s += _tree(left, indent + 2)
                    s += " " * indent + f"else:\n"
                    s += _tree(right, indent + 2)
            return s

        ROOT_INDEX = 0
        return _tree(ROOT_INDEX, indent)