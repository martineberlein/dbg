from typing import Iterable, Optional

from dbg.data.input import Input
from dbg.explanation.candidate import Explanation
from dbg.learner.learner import Learner


class AvicennaExplanation(Explanation):

    def evaluate(self, inputs):
        pass

    def __neg__(self):
        pass


class AvicennaLearner(Learner):
    def learn_explanation(self, test_inputs: Iterable[Input], **kwargs) -> Optional[ExplanationSet]:
        pass

