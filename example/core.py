from typing import Set

from dbg.core import HypothesisBasedExplainer
from dbg.data.input import Input
from dbg.explanation.candidate import ExplanationSet


class GrammarFeatureExplainer(HypothesisBasedExplainer):

    def __init__(self, grammar, oracle, initial_inputs: Set[str], **kwargs):

        learner = None
        generator = None
        
        super().__init__(grammar, oracle, initial_inputs, **kwargs)