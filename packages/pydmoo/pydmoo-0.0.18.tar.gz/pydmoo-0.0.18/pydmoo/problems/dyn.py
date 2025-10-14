"""
Include modified code from [pymoo](https://github.com/anyoptimization/pymoo):
 [dyn.py](https://github.com/anyoptimization/pymoo/blob/main/pymoo/problems/dyn.py),
licensed under Apache License 2.0. Original copyright and license terms are preserved.
"""

from abc import ABC
from math import ceil

from mpmath import mp
from pymoo.core.callback import Callback
from pymoo.core.problem import Problem


class DynamicProblem(Problem, ABC):
    pass


class DynamicTestProblem(DynamicProblem, ABC):

    def __init__(self, nt, taut, t0=50, tau=1, time=None, add_time_perturbation=False, **kwargs):
        super().__init__(**kwargs)
        self.tau = tau
        self.nt = nt
        self.taut = taut
        self.t0 = t0  # added by DynOpt
        self._time = time

        self.add_time_perturbation = add_time_perturbation  # added by DynOpt

    def tic(self, elapsed=1):

        # increase the time counter by one
        self.tau += elapsed

        # remove the cache of the problem to recreate ps and pf
        self.__dict__["cache"] = {}

    @property
    def time(self):
        if self._time is not None:
            return self._time
        else:
            # return 1 / self.nt * (self.tau // self.taut)

            # added by DynOpt
            delta_time = 1 / self.nt
            count = max((self.tau + self.taut - (self.t0 + 1)), 0) // self.taut

            if not self.add_time_perturbation:
                ratio = 0

            else:
                mp.dps = max(ceil(10 + count), 10)
                mp_pi = 0 if count == 0 else int(str(mp.pi).split(".")[-1][count - 1])
                ratio = 0.5 * 1 / 9 * mp_pi

            return delta_time * count + delta_time * ratio

    @time.setter
    def time(self, value):
        self._time = value

    # added by DynOpt
    def update_to_next_time(self):

        # update to next time
        count = max((self.tau + self.taut - (self.t0 + 1)), 0) // self.taut

        elapsed = int(count * self.taut + (self.t0 + 1) - self.tau)

        self.tic(elapsed=elapsed)

        return elapsed


class TimeSimulation(Callback):

    def update(self, algorithm):
        problem = algorithm.problem

        # added by DynOpt
        # Designed to handle time-linkage properties within the GTS test suites.
        if hasattr(problem, "time_linkage") and hasattr(problem, "cal"):
            problem.cal(algorithm.opt.get("F"))

        if hasattr(problem, "tic"):
            problem.tic()
        else:
            raise Exception("TimeSimulation can only be used for dynamic test problems.")
