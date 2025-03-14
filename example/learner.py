from typing import Iterable, Optional

from dbg.data.input import Input
from dbg.explanation.candidate import ExplanationSet
from dbg.learner.learner import Learner


class GrammarFeatureLearner(Learner):
    def learn_explanation(self, test_inputs: Iterable[Input], **kwargs) -> Optional[ExplanationSet]:
        pass