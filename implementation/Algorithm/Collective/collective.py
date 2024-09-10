import math
from Problem.problem import Problem
from Algorithm.NE.shared import run_solve
from Algorithm.NE.utils import ratios

class CollectiveSynthesiser:
    def __init__(self, on_iteration, on_successful, on_failed) -> None:
        self.on_iteration = on_iteration
        self.on_successful = on_successful
        self.on_failed = on_failed

    def find_collective(self, problem: Problem):
        (prev_strategy_profile, execution_path, _) = run_solve(problem, -1, None, {})

        if prev_strategy_profile == None:
            self.on_failed("Encoding is not satifiable")
            return (None, None)

        self.on_successful()
        return (prev_strategy_profile, execution_path)
