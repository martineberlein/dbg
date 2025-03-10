from typing import Iterable, Optional
from abc import ABC, abstractmethod

import pandas as pd

from dbg.data.input import Input
from dbg.explanation.candidate import ExplanationSet
from dbg.learner.learner import Learner
from dbg.data.oracle import OracleResult


class AlhazenLearner(Learner):

    def get_best_candidates(self) -> Optional[ExplanationSet]:
        pass

    def get_explanations(self) -> Optional[ExplanationSet]:
        pass

    def learn_explanation(self, test_inputs: Iterable[Input], **kwargs) -> Optional[ExplanationSet]:
        pass


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
            {**inp.features, "oracle": inp.oracle}
            for inp in test_inputs
            if inp.oracle != OracleResult.UNDEFINED
        ]

        if data_records:
            new_data = pd.DataFrame.from_records(data_records)
            self.data = pd.concat([self.data, new_data], sort=False) if not self.data.empty else new_data

        return self.data