# Copyright: 2025 The PEPFlow Developers
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import functools
import math

import numpy as np

from pepflow import function
from pepflow import parameter as pm
from pepflow import pep
from pepflow import pep_context as pc
from pepflow.constraint import Constraint


def test_gd_e2e():
    ctx = pc.PEPContext("gd").set_as_current()
    pep_builder = pep.PEPBuilder()
    eta = 1
    N = 9

    f = pep_builder.declare_func(function.SmoothConvexFunction, "f", L=1)
    x = pep_builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(f.func_val(p) - f.func_val(x_star))
        result = pep_builder.solve_primal()
        expected_opt_value = 1 / (4 * i + 2)
        assert math.isclose(result.primal_opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(
            dual_result.dual_opt_value, expected_opt_value, rel_tol=1e-3
        )


def test_gd_diff_stepsize_e2e():
    pc.PEPContext("gd").set_as_current()
    pep_builder = pep.PEPBuilder()
    eta = 1 / pm.Parameter(name="L")
    N = 4

    f = pep_builder.declare_func(
        function.SmoothConvexFunction, "f", L=pm.Parameter(name="L")
    )
    x = pep_builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.grad(x)
        x.add_tag(f"x_{i + 1}")
    pep_builder.set_performance_metric(f(x) - f(x_star))

    for l_val in [1, 4, 0.25]:
        result = pep_builder.solve_primal(resolve_parameters={"L": l_val})
        expected_opt_value = l_val / (4 * N + 2)
        assert math.isclose(result.primal_opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(resolve_parameters={"L": l_val})
        assert math.isclose(
            dual_result.dual_opt_value, expected_opt_value, rel_tol=1e-3
        )


def test_pgm_e2e():
    ctx = pc.PEPContext("pgm").set_as_current()
    pep_builder = pep.PEPBuilder()
    eta = 1
    N = 1

    f = pep_builder.declare_func(function.SmoothConvexFunction, "f", L=1)
    g = pep_builder.declare_func(function.ConvexFunction, "g")

    h = f + g

    x = pep_builder.add_init_point("x_0")
    x_star = h.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        y = x - eta * f.grad(x)
        y.add_tag(f"y_{i + 1}")
        x = g.proximal_step(y, eta)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(h.func_val(p) - h.func_val(x_star))

        result = pep_builder.solve_primal()
        expected_opt_value = 1 / (4 * i)
        assert math.isclose(result.primal_opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(
            dual_result.dual_opt_value, expected_opt_value, rel_tol=1e-3
        )


def test_ogm_e2e():
    pep_builder = pep.PEPBuilder()
    ogm = pc.PEPContext("ogm").set_as_current()

    L = 1
    f = pep_builder.declare_func(function.SmoothConvexFunction, "f", L=1)

    N_range = 10

    theta = [pm.Parameter(f"theta_{i}") for i in range(N_range + 1)]

    @functools.cache
    def theta_ogm(i, N):
        if i == -1:
            return 0
        if i == N:
            return 1 / 2 * (1 + np.sqrt(8 * theta_ogm(N - 1, N) ** 2 + 1))
        return 1 / 2 * (1 + np.sqrt(4 * theta_ogm(i - 1, N) ** 2 + 1))

    x_0 = pep_builder.add_init_point("x_0")
    x = x_0
    z = x_0

    eta = 1 / L

    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        Constraint.make((x_0 - x_star) ** 2, "<=", 1, name="initial_condition")
    )

    for N in range(1, N_range):
        y = x - eta * f.grad(x)
        z = z - 2 * eta * theta[N - 1] * f.grad(x)
        x = (1 - 1 / theta[N]) * y + 1 / theta[N] * z

        z.add_tag(f"z_{N}")
        x.add_tag(f"x_{N}")

        x_N = ogm.get_by_tag(f"x_{N}")
        pep_builder.set_performance_metric(f(x_N) - f(x_star))

        result = pep_builder.solve_primal(
            resolve_parameters={f"theta_{i}": theta_ogm(i, N) for i in range(N + 1)}
        )
        expected_opt_value_N = L / (2 * theta_ogm(N, N) ** 2)
        assert math.isclose(result.primal_opt_value, expected_opt_value_N, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(
            resolve_parameters={f"theta_{i}": theta_ogm(i, N) for i in range(N + 1)}
        )
        assert math.isclose(
            dual_result.dual_opt_value, expected_opt_value_N, rel_tol=1e-3
        )


def test_ogm_g_e2e():
    pep_builder = pep.PEPBuilder()
    ogm_g = pc.PEPContext("ogm_g").set_as_current()

    L = 1
    f = pep_builder.declare_func(function.SmoothConvexFunction, "f", L=1)

    N_range = 10

    reversed_theta = [pm.Parameter(f"reversed_theta_{i}") for i in range(N_range + 1)]

    @functools.cache
    def theta_ogm(i, N):
        if i == -1:
            return 0
        if i == N:
            return 1 / 2 * (1 + np.sqrt(8 * theta_ogm(N - 1, N) ** 2 + 1))
        return 1 / 2 * (1 + np.sqrt(4 * theta_ogm(i - 1, N) ** 2 + 1))

    def reverse_theta_ogm(i, N):
        return theta_ogm(N - i, N)

    x_0 = pep_builder.add_init_point("x_0")
    x = x_0
    z = x_0

    eta = 1 / L
    z = z - eta * (reversed_theta[0] + 1) / 2 * f.grad(x)
    z.add_tag(f"z_{1}")

    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        Constraint.make(f(x_0) - f(x_star), "<=", 1, name="initial_condition")
    )

    def power_four(a):
        return a * a * a * a

    for N in range(1, N_range):
        y = x - eta * f.grad(x)
        # TODO: implement __pow__ for Parameter
        # x = (reversed_theta[N + 1] / reversed_theta[N]) ** 4 * y + (
        #     1 - (reversed_theta[N + 1] / reversed_theta[N]) ** 4
        # ) * z
        x = (
            power_four(reversed_theta[N + 1] / reversed_theta[N]) * y
            + (1 - power_four(reversed_theta[N + 1] / reversed_theta[N])) * z
        )
        z = z - eta * reversed_theta[N] * f.grad(x)

        x.add_tag(f"x_{N}")
        z.add_tag(f"z_{N + 1}")

        x_N = ogm_g.get_by_tag(f"x_{N}")
        pep_builder.set_performance_metric((f.grad(x_N)) ** 2)

        result = pep_builder.solve_primal(
            resolve_parameters={
                f"reversed_theta_{i}": reverse_theta_ogm(i, N) for i in range(N + 2)
            }
        )
        expected_opt_value_N = 2 * L / reverse_theta_ogm(0, N) ** 2
        assert math.isclose(result.primal_opt_value, expected_opt_value_N, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(
            resolve_parameters={
                f"reversed_theta_{i}": reverse_theta_ogm(i, N) for i in range(N + 2)
            }
        )
        assert math.isclose(
            dual_result.dual_opt_value, expected_opt_value_N, rel_tol=1e-3
        )
