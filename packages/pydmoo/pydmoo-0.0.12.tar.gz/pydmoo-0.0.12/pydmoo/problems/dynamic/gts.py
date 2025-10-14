from math import floor

import numpy as np
from pymoo.util.remote import Remote
from scipy.spatial.distance import cdist

from pydmoo.problems.dyn import DynamicTestProblem
from pydmoo.problems.dynamic.df import get_PF


def knee_point(F):
    ideal_point = np.min(F, axis=0)
    distances = cdist(F, [ideal_point])
    knee_idx = np.argmax(distances)
    return F[knee_idx]


def G_t(t):
    """G(t) = sin(0.5πt)"""
    return np.sin(0.5 * np.pi * t)


def H_t(t):
    """H(t) = 1.5 + G(t)"""
    return 1.5 + G_t(t)


def alpha_t(t):
    """αt = 5cos(0.5πt)"""
    return 5 * np.cos(0.5 * np.pi * t)


def beta_t(t):
    """βt = 0.2 + 2.8|G(t)|"""
    return 0.2 + 2.8 * np.abs(G_t(t))


def omega_t(t):
    """ωt = ⌊10G(t)⌋"""
    return np.floor(10 * G_t(t))


def a_t(t):
    """a = sin(0.5πt)"""
    return np.sin(0.5 * np.pi * t)


def b_t(t):
    """b = 1 + |cos(0.5πt)|"""
    return 1 + np.abs(np.cos(0.5 * np.pi * t))


def y_t(x1, t):
    """y = 0.5 + G(t)(x1 - 0.5)"""
    return 0.5 + G_t(t) * (x1 - 0.5)


def p_t(t):
    """pt = ⌊6G(t)⌋"""
    return np.floor(6 * G_t(t))


class GTS(DynamicTestProblem):

    def __init__(self,
                 part_idx,
                 bounds,
                 R_case="one",
                 add_time_perturbation=True,
                 n_var=10,
                 nt=10,
                 taut=20,
                 **kwargs):
        super().__init__(nt,
                         taut,
                         add_time_perturbation=add_time_perturbation,
                         n_var=n_var,
                         n_obj=2,
                         xl=0,
                         xu=1,
                         **kwargs)

        self.time_linkage = 1

        self.sub_vec_1, self.sub_vec_2, self.sub_vec_3 = self._partition_dimension(part_idx)

        # positive semidefinite matrices
        if R_case == "one":
            self.R_2 = np.eye(len(self.sub_vec_2))
            self.R_3 = np.eye(len(self.sub_vec_3))
        elif R_case == "two":
            self.R_2 = np.diag([i + 1 for i in range(len(self.sub_vec_2))])
            self.R_3 = np.diag([i + 1 for i in range(len(self.sub_vec_3))])
        elif R_case == "three":
            diag_matrix = np.diag(len(self.sub_vec_2) + np.arange(len(self.sub_vec_2)))
            ones_matrix = np.ones((len(self.sub_vec_2), len(self.sub_vec_2)))
            self.R_2 = np.where(np.eye(len(self.sub_vec_2), dtype=bool), diag_matrix, ones_matrix)

            diag_matrix = np.diag(len(self.sub_vec_3) + np.arange(len(self.sub_vec_3)))
            ones_matrix = np.ones((len(self.sub_vec_3), len(self.sub_vec_3)))
            self.R_3 = np.where(np.eye(len(self.sub_vec_3), dtype=bool), diag_matrix, ones_matrix)
        else:
            raise ValueError(f"{R_case} must be `one`, `two` or `three`.")

        # norm
        self.p = 1

        self.xl[self.sub_vec_1] = bounds[0][0]
        self.xu[self.sub_vec_1] = bounds[0][1]
        self.xl[self.sub_vec_2] = bounds[1][0]
        self.xu[self.sub_vec_2] = bounds[1][1]
        self.xl[self.sub_vec_3] = bounds[2][0]
        self.xu[self.sub_vec_3] = bounds[2][1]

    def _calc_pareto_front(self, *args, **kwargs):
        return Remote.get_instance().load("pydmoo", "pf", "GTS", f"{str(self.__class__.__name__)}.pf")

    def _calc_pareto_set(self, *args, **kwargs):
        return Remote.get_instance().load("pydmoo", "ps", "GTS", f"{str(self.__class__.__name__)}.ps")

    # Designed to handle time-linkage properties within the GTS test suites.
    def cal(self, F):
        self.time_linkage = 1 + np.linalg.norm(knee_point(self.pareto_front()) - knee_point(F))

    def _partition_dimension(self, part_idx):
        fd = floor(self.n_var / 2)
        sub_vec_1 = range(0, part_idx)
        sub_vec_2 = range(part_idx, fd + (part_idx - 1))
        sub_vec_3 = range(fd + (part_idx - 1), self.n_var)
        return sub_vec_1, sub_vec_2, sub_vec_3


class GTS1(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=1, bounds=((0, 1), (-1, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = np.cos(0.5 * np.pi * self.time)
        xj = G_t(self.time) + np.power(x[:, 0], H_t(self.time))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = x[:, 0]
        f2 = g * (1 - np.power(x[:, 0] / g, H_t(self.time)))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        x = np.linspace(0, 1, n_pareto_points)
        f1 = x
        f2 = 1 - np.power(x, H_t(self.time))
        return np.array([f1, f2]).T

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.cos(0.5 * np.pi * self.time))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS2(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (0, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        t = 3 * np.pi * self.time ** 2
        cot = np.cos(t) / (np.sin(t) + (np.sin(t) == 0) * 1e-32)

        xi = (1 / np.pi) * np.abs(np.arctan(cot))
        xj = G_t(self.time) + np.power(x[:, 0], H_t(self.time))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = 0.5 * x[:, 0] + x[:, 1]
        f2 = g * (2.8 - np.power(f1 / g, H_t(self.time)))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')

        f1 = 0.5 * x1 + x2
        f2 = 2.8 - np.power(f1, H_t(self.time))
        return get_PF(np.array([f1, f2]), False)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        t = 3 * np.pi * self.time ** 2
        cot = np.cos(t) / (np.sin(t) + (np.sin(t) == 0) * 1e-32)

        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), (1 / np.pi) * np.abs(np.arctan(cot)))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS3(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=1, bounds=((0, 1), (-1, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = (G_t(self.time) * np.sin(4 * np.pi * x[:, 0])) / (1 + np.abs(G_t(self.time)))
        xj = G_t(self.time) + np.power(x[:, 0], H_t(self.time))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = g * np.power(x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0]), beta_t(self.time))
        f2 = g * np.power(1 - x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0]), beta_t(self.time))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        x = np.linspace(0, 1, n_pareto_points)
        f1 = np.power(x + 0.1 * np.sin(3 * np.pi * x), beta_t(self.time))
        f2 = np.power(1 - x + 0.1 * np.sin(3 * np.pi * x), beta_t(self.time))

        return get_PF(np.array([f1, f2]), True)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = (G_t(self.time) * np.sin(4 * np.pi * x_vec1)) / (1 + np.abs(G_t(self.time)))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS4(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=1, bounds=((0, 1), (0, 1), (-1, 1)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = np.abs(G_t(self.time))
        xj = (G_t(self.time) * np.sin(4 * np.pi * x[:, 0])) / (1 + np.abs(G_t(self.time)))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        g += (-0.5 + 0.25 * np.sin(0.3 * np.pi * self.time))

        f1 = g * ((1 + self.time) / (x[:, 0] + 3))
        f2 = g * ((x[:, 0] + 3) / (1 + self.time))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        x = np.linspace(0, 1, n_pareto_points)
        g = 1 + (-0.5 + 0.25 * np.sin(0.3 * np.pi * self.time))

        f1 = g * ((1 + self.time) / (x + 3))
        f2 = g * ((x + 3) / (1 + self.time))

        return np.array([f1, f2]).T

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.abs(G_t(self.time)))
        x_vec3 = (G_t(self.time) * np.sin(4 * np.pi * x_vec1)) / (1 + np.abs(G_t(self.time)))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS5(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (-1, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = np.cos(0.5 * np.pi * self.time)
        xj = G_t(self.time) + np.power(x[:, 0], H_t(self.time))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        g += 0.5 + 0.5 * G_t(self.time)

        x12 = 0.5 * x[:, 0] + x[:, 1]
        _sin = 0.02 * np.sin(omega_t(self.time) * np.pi * x12)
        f1 = g * (x12 + _sin)
        f2 = g * (1.6 - x12 + _sin)

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')
        g = 1 + 0.5 + 0.5 * G_t(self.time)

        x12 = 0.5 * x1 + x2
        _sin = 0.02 * np.sin(omega_t(self.time) * np.pi * x12)
        f1 = g * (x12 + _sin)
        f2 = g * (1.6 - x12 + _sin)

        return get_PF(np.array([f1, f2]), True)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.cos(0.5 * np.pi * self.time))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS6(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=1, bounds=((0, 1), (-1, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = self.time_linkage * np.cos(0.5 * np.pi * self.time)
        xj = self.time_linkage * (G_t(self.time) + np.power(x[:, 0], H_t(self.time)))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = x[:, 0]
        f2 = g * (1 - np.power(f1 / g, H_t(self.time)))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        f1 = np.linspace(0, 1, n_pareto_points)
        f2 = 1 - np.power(f1, H_t(self.time))
        return np.array([f1, f2]).T

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.cos(0.5 * np.pi * self.time))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS7(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=1, bounds=((-1, 2.5), (-1, 1), (0, 1)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = self.time_linkage * np.cos(0.5 * np.pi * self.time)
        xj = self.time_linkage * 1 / (1 + np.exp(alpha_t(self.time) * (x[:, 0] - 0.5)))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = g * np.power(np.abs(x[:, 0] - a_t(self.time)), H_t(self.time))
        f2 = g * np.power(np.abs(x[:, 0] - a_t(self.time) - b_t(self.time)), H_t(self.time))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        x = np.linspace(a_t(self.time), a_t(self.time) + b_t(self.time), n_pareto_points)

        f1 = np.power(np.abs(x - a_t(self.time)), H_t(self.time))
        f2 = np.power(np.abs(x - a_t(self.time) - b_t(self.time)), H_t(self.time))

        return np.array([f1, f2]).T

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(a_t(self.time), a_t(self.time) + b_t(self.time), n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.cos(0.5 * np.pi * self.time))
        x_vec3 = 1 / (1 + np.exp(alpha_t(self.time) * (x_vec1 - 0.5)))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS8(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (0, 1), (-1, 2)), **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        xi = self.time_linkage * 1 / (1 + np.exp(alpha_t(self.time) * (x[:, 0] - 0.5)))
        xj = self.time_linkage * (G_t(self.time) + np.power(x[:, 0], H_t(self.time)))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        g += 0.25 * np.abs(np.cos(0.3 * np.pi * self.time))

        f1 = 0.5 * x[:, 0] + x[:, 1]
        f2 = g * (2.8 - np.power(f1 / g, H_t(self.time)))

        out["F"] = np.column_stack([f1, f2])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')

        f1 = 0.5 * x1 + x2
        g = 1 + 0.25 * np.abs(np.cos(0.3 * np.pi * self.time))
        f2 = g * (2.8 - np.power(f1 / g, H_t(self.time)))
        return get_PF(np.array([f1, f2]), False)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = 1 / (1 + np.exp(alpha_t(self.time) * (x_vec1 - 0.5)))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


# modified DF12
class GTS9(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (0, 1), (-1, 1)), **kwargs)
        self.n_obj = 3

    def _evaluate(self, x, out, *args, **kwargs):
        xi = 1 / (1 + np.exp(alpha_t(self.time) * (x[:, 0] - 0.5)))
        xj = np.sin(self.time * x[:, 0])

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        g += np.abs(np.cos(0.27 * np.pi * self.time))

        f1 = g * np.cos(0.5 * np.pi * x[:, 1]) * np.cos(0.5 * np.pi * x[:, 0])
        f2 = g * np.sin(0.5 * np.pi * x[:, 1]) * np.cos(0.5 * np.pi * x[:, 0])
        f3 = g * np.sin(0.5 * np.pi * x[:, 0])

        out["F"] = np.column_stack([f1, f2, f3])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')

        g = 1
        g += np.abs(np.cos(0.27 * np.pi * self.time))

        f1 = np.multiply(np.multiply(g, np.cos(0.5 * np.pi * x2)), np.cos(0.5 * np.pi * x1))
        f2 = np.multiply(np.multiply(g, np.sin(0.5 * np.pi * x2)), np.cos(0.5 * np.pi * x1))
        f3 = np.multiply(g, np.sin(0.5 * np.pi * x1))

        return get_PF(np.array([f1, f2, f3]), True)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = 1 / (1 + np.exp(alpha_t(self.time) * (x_vec1 - 0.5)))
        x_vec3 = np.sin(self.time * x_vec1)
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


# modified DF13
class GTS10(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (0, 1), (-1, 1)), **kwargs)
        self.n_obj = 3

    def _evaluate(self, x, out, *args, **kwargs):
        xi = np.abs(G_t(self.time))
        xj = -0.5 + np.abs(G_t(self.time) * np.sin(4 * np.pi * x[:, 1])) / (0.5 * (1 + np.abs(G_t(self.time))))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        f1 = g * np.cos(0.5 * np.pi * x[:, 0]) ** 2
        f2 = g * np.cos(0.5 * np.pi * x[:, 1]) ** 2

        _sin1 = np.sin(0.5 * np.pi * x[:, 0])
        _sin2 = np.sin(0.5 * np.pi * x[:, 1])
        _cos1 = np.cos(p_t(self.time) * np.pi * x[:, 0])
        _cos2 = np.cos(p_t(self.time) * np.pi * x[:, 1])
        f3 = g * (_sin1 ** 2 + _sin1 * _cos1 ** 2 + _sin2 ** 2 + _sin2 * _cos2 ** 2)

        out["F"] = np.column_stack([f1, f2, f3])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')
        G = np.sin(0.5 * np.pi * self.time)
        p = np.floor(6 * G)

        f1 = np.cos(0.5 * np.pi * x1) ** 2
        f2 = np.cos(0.5 * np.pi * x2) ** 2
        f3 = np.sin(0.5 * np.pi * x1) ** 2 + np.sin(0.5 * np.pi * x1) * np.cos(p * np.pi * x1) ** 2 + np.sin(
            0.5 * np.pi * x2) ** 2 + np.sin(0.5 * np.pi * x2) * np.cos(p * np.pi * x2) ** 2

        return get_PF(np.array([f1, f2, f3]), True)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.abs(G_t(self.time)))
        x_vec3 = -0.5 + np.abs(G_t(self.time) * np.sin(4 * np.pi * x_vec1)) / (0.5 * (1 + np.abs(G_t(self.time))))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


# modified DF14
class GTS11(GTS):
    def __init__(self, **kwargs):
        super().__init__(part_idx=2, bounds=((0, 1), (0, 1), (-1, 2)), **kwargs)
        self.n_obj = 3

    def _evaluate(self, x, out, *args, **kwargs):
        xi = np.abs(G_t(self.time))
        xj = G_t(self.time) + np.power(x[:, 0], H_t(self.time))

        x2, x3 = (x[:, self.sub_vec_2] - xi.reshape(-1, 1)), (x[:, self.sub_vec_3] - xj.reshape(-1, 1))

        # quadratic form
        diag_x2_R2_x2T = np.einsum('ij,jk,ik->i', x2, self.R_2, x2)
        diag_x3_R3_x3T = np.einsum('ij,jk,ik->i', x3, self.R_3, x3)
        g = 1 + np.power(diag_x2_R2_x2T, self.p) + np.power(diag_x3_R3_x3T, self.p)

        y = y_t(x[:, 0], self.time)
        f1 = g * (1.05 - y + 0.05 * np.sin(6 * np.pi * y))
        f2 = g * (1.05 - x[:, 1] + 0.05 * np.sin(6 * np.pi * x[:, 1])) * (y + 0.05 * np.sin(6 * np.pi * y))
        f3 = g * (x[:, 1] + 0.05 * np.sin(6 * np.pi * x[:, 1])) * (y + 0.05 * np.sin(6 * np.pi * y))

        out["F"] = np.column_stack([f1, f2, f3])

    def _calc_pareto_front(self, *args, n_pareto_points=100, **kwargs):
        H = 20
        x1, x2 = np.meshgrid(np.linspace(0, 1, H), np.linspace(0, 1, H), indexing='xy')

        y = y_t(x1, self.time)
        f1 = 1.05 - y + 0.05 * np.sin(6 * np.pi * y)
        f2 = np.multiply(1.05 - x2 + 0.05 * np.sin(6 * np.pi * x2), y + 0.05 * np.sin(6 * np.pi * y))
        f3 = np.multiply(x2 + 0.05 * np.sin(6 * np.pi * x2), y + 0.05 * np.sin(6 * np.pi * y))

        return get_PF(np.array([f1, f2, f3]), False)

    def _calc_pareto_set(self, *args, n_pareto_points=100, **kwargs):
        x_vec1 = np.linspace(0, 1, n_pareto_points)
        x_vec2 = np.full(len(x_vec1), np.abs(G_t(self.time)))
        x_vec3 = G_t(self.time) + np.power(x_vec1, H_t(self.time))
        X, Y, Z = x_vec1, x_vec2, x_vec3
        return np.array([X.flatten(order='F'), Y.flatten(order='F'), Z.flatten(order='F')]).T


class GTS1_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS2_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS3_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS4_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS5_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS6_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS7_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS8_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS9_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS10_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS11_2(GTS1):
    def __init__(self, R_case="two", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS1_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS2_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS3_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS4_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS5_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS6_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS7_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS8_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS9_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS10_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)


class GTS11_3(GTS1):
    def __init__(self, R_case="three", **kwargs):
        super().__init__(R_case=R_case, **kwargs)
