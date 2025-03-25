import time
import random
import os
from abc import ABC, abstractmethod
import hashlib
from pathlib import Path
from typing import Iterable

from dbg.data.input import Input
from dbg.learner.learner import Learner
from dbg.types import OracleType
from dbg_evaluation.util import format_results


def stable_hash(value: str, length: int = 8) -> str:
    return hashlib.sha1(value.encode()).hexdigest()[:length]


class Experiment(ABC):

    def __init__(self, name: str, subject_name: str, learner: Learner, grammar, initial_inputs: set, oracle: OracleType, evaluation_inputs: set = None):
        self.name: str = name
        self.subject_name: str = subject_name
        self.learner: Learner = learner

        self.grammar = grammar
        self.oracle = oracle
        self.initial_inputs = initial_inputs

        self.evaluation_inputs = evaluation_inputs if evaluation_inputs else self.get_evaluation_inputs()

    def evaluate(self, seed = 1, **kwargs):
        random.seed(seed)
        start_time_learning = time.time()

        explanations = self.learner.learn_explanation(
            test_inputs=self.initial_inputs,
            **kwargs,
        )

        end_time_learning = time.time()

        # round time
        time_in_seconds = round(end_time_learning - start_time_learning, 4)

        return format_results(
            "Calculator", explanations, time_in_seconds, self.evaluation_inputs
        )

    @abstractmethod
    def get_evaluation_inputs(self, **kwargs):
        """
        Generate the evaluation inputs.
        """
        pass

    @staticmethod
    def write_to_file(inputs: Iterable[Input], subject_name: str):
        base_path = Path.home() / ".dbgbench" / subject_name
        os.makedirs(base_path/ "positive_inputs", exist_ok=True)
        os.makedirs(base_path / "negative_inputs", exist_ok=True)

        for inp in inputs:
            try:
                filename = f"{subject_name}_{stable_hash(str(inp))}.txt"
                directory = "positive_inputs" if inp.oracle.is_failing() else "negative_inputs"
                filepath = os.path.join(base_path, directory, filename)

                with open(filepath, "w") as f:
                    f.write(str(inp))

            except Exception as e:
                print(f"Error writing input: {inp}\nException: {e}")

    def load(self) -> list[tuple[str, bool]]:
        base_path = Path.home() / ".dbgbench" / self.subject_name
        inputs = []
        for inp in self.load_from_files(base_path / "positive_inputs")[:200]:
            inputs.append((inp, True))
        for inp in self.load_from_files(base_path / "negative_inputs")[:200]:
            inputs.append((inp, False))
        return inputs

    @staticmethod
    def load_from_files(directory: str) -> list[str]:
        inputs = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    try:
                        inputs.append(content)
                    except Exception as e:
                        print(f"Failed to load {filepath}: {e}")
        return inputs