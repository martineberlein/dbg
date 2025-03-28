from typing import List, Set
import os
import csv

from dbg.explanation.candidate import Explanation, ExplanationSet
from dbg.data.input import Input
from dbg.learner.metric import RecallPriorityFitness


def print_constraints(
    candidates: List[Explanation], initial_inputs: Set[Input]
):
    """
    Print the constraints.
    """
    failing_inputs = {inp for inp in initial_inputs if inp.oracle.is_failing()}
    print(
        f"Learned Fandango Constraints (based on {len(initial_inputs)} initial inputs ({len(failing_inputs)} failing)):"
    )
    for candidate in candidates:
        print(candidate)


# def evaluate_candidates(
#     candidates: List[Explanation], grammar, oracle, num_inputs=2000
# ):
#     """
#     Evaluate the candidates.
#     """
#     start_time = time.time()
#     evaluation_inputs = generate_evaluation_inputs(grammar, oracle, num_inputs)
#
#     for candidate in candidates:
#         candidate.evaluate(evaluation_inputs)
#     eval_time = time.time() - start_time
#
#     print(
#         "Evaluate Constraints with:",
#         len(evaluation_inputs),
#         "inputs",
#         f"(Time taken: {eval_time:.4f} seconds)",
#     )
#     for candidate in candidates:
#         print(candidate)


# def generate_evaluation_inputs(grammar, oracle: Callable, num_inputs=2000):
#     """
#     Generate the evaluation inputs.
#     """
#     random.seed(1)
#     evaluation_inputs = []
#     for _ in range(num_inputs):
#         inp = grammar.fuzz()
#         oracle_result = oracle(str(inp))
#         if oracle_result != OracleResult.UNDEFINED:
#             evaluation_inputs.append((str(inp), oracle_result))
#
#     return {
#         Input.from_str(grammar, inp, result)
#         for inp, result in evaluation_inputs
#     }
#
#
# def get_inputs(
#     grammar, oracle: Callable, num_failing=5, num_passing=10
# ) -> (Set[Input], Set[Input]):
#     """
#     Get the inputs.
#     """
#     failing_inputs = set()
#     passing_inputs = set()
#     while len(failing_inputs) < num_failing or len(passing_inputs) < num_passing:
#         tree = grammar.fuzz()
#         inp = Input.from_str(grammar, str(tree), oracle(str(tree)))
#         if inp.oracle.is_failing():
#             failing_inputs.add(inp) if len(failing_inputs) < num_failing else None
#         else:
#             passing_inputs.add(inp) if len(passing_inputs) < num_passing else None
#
#     return failing_inputs, passing_inputs


def format_results(
    name: str,
    candidates: List[Explanation] | ExplanationSet,
    time_in_seconds: float,
    evaluation_inputs: set[Input],
    seed: int,
    **kwargs,
):
    sorting_strategy = RecallPriorityFitness()

    candidates = candidates or []

    explanations = []
    for candidate in candidates:
        candidate.reset()
        try:
            candidate.evaluate(evaluation_inputs, **kwargs)
            explanations.append(candidate)
        except Exception:
            continue

    sorted_candidates = sorted(
        explanations,
        key=lambda c: sorting_strategy.evaluate(c),
        reverse=True,
    )
    best_candidate = [
        candidate
        for candidate in sorted_candidates
        if sorting_strategy.is_equal(candidate, sorted_candidates[0])
    ]

    return {
        "name": name,
        "seed": seed,
        "candidates": candidates if candidates else None,
        "time_in_seconds": time_in_seconds,
        "best_candidates": best_candidate if candidates else None,
        "precision": best_candidate[0].precision() if candidates else None,
        "recall": best_candidate[0].recall() if candidates else None,
    }


def save_results_to_csv(results, filename):
    keys = [
        "name",
        "seed",
        "time_in_seconds",
        "precision",
        "recall",
        "num_candidates",
        "num_best_candidates"
    ]

    file_exists = os.path.isfile(filename)
    is_empty = not file_exists or os.stat(filename).st_size == 0

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)

        if is_empty:
            writer.writeheader()

        for result in results:
            row = {
                "name": result.get("name"),
                "seed": result.get("seed"),
                "time_in_seconds": result.get("time_in_seconds"),
                "precision": result.get("precision"),
                "recall": result.get("recall"),
                "num_candidates": len(result.get("candidates") or []),
                "num_best_candidates": len(result.get("best_candidates") or []),
            }
            writer.writerow(row)

