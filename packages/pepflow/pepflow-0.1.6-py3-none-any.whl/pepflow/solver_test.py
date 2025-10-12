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

import numpy as np

from pepflow import pep as pep
from pepflow import solver as ps
from pepflow import vector as pp


def test_cvx_solver_case1():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Vector(is_basis=True, tags=["p1"])
        s1 = pp.Scalar(is_basis=True, tags=["s1"])
        s2 = -(1 + p1 * p1)
        constraints = [(p1 * p1).gt(1, name="x^2 >= 1"), s1.gt(0, name="s1 > 0")]

    solver = ps.CVXPrimalSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )

    # It is a simple `min_x 1 + x^2; s.t. x^2 >= 1` problem.
    problem = solver.build_problem()
    result = problem.solve()
    assert abs(-result - 2) < 1e-6

    assert np.isclose(solver.dual_var_manager.dual_value("x^2 >= 1"), 1)
    assert solver.dual_var_manager.dual_value("s1 > 0") == 0


def test_cvx_solver_case2():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Vector(is_basis=True, tags=["p1"])
        s1 = pp.Scalar(is_basis=True, tags=["s1"])
        s2 = -p1 * p1 + 2
        constraints = [(p1 * p1).lt(1, name="x^2 <= 1"), s1.gt(0, name="s1 > 0")]

    solver = ps.CVXPrimalSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )

    # It is a simple `min_x x^2-2; s.t. x^2 <= 1` problem.
    problem = solver.build_problem()
    result = problem.solve()
    assert abs(-result + 2) < 1e-6

    assert np.isclose(solver.dual_var_manager.dual_value("x^2 <= 1"), 0)
    assert solver.dual_var_manager.dual_value("s1 > 0") == 0


def test_cvx_dual_solver_case1():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Vector(is_basis=True, tags=["p1"])
        s1 = pp.Scalar(is_basis=True, tags=["s1"])
        s2 = -(1 + p1 * p1)
        constraints = [(p1 * p1).gt(1, name="x^2 >= 1"), s1.gt(0, name="s1 > 0")]

    dual_solver = ps.CVXDualSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )
    problem = dual_solver.build_problem()
    result = problem.solve()
    assert abs(-result - 2) < 1e-6

    assert np.isclose(dual_solver.dual_var_manager.dual_value("x^2 >= 1"), 1)
    assert np.isclose(dual_solver.dual_var_manager.dual_value("s1 > 0"), 0)


def test_cvx_dual_solver_case2():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        p1 = pp.Vector(is_basis=True, tags=["p1"])
        s1 = pp.Scalar(is_basis=True, tags=["s1"])
        s2 = -p1 * p1 + 2
        constraints = [(p1 * p1).lt(1, name="x^2 <= 1"), s1.gt(0, name="s1 > 0")]

    dual_solver = ps.CVXDualSolver(
        perf_metric=s2,
        constraints=constraints,
        context=pep_builder.get_context("test"),
    )

    # It is a simple `min_x x^2-2; s.t. x^2 <= 1` problem.
    problem = dual_solver.build_problem()
    result = problem.solve()
    assert abs(-result + 2) < 1e-6

    assert np.isclose(dual_solver.dual_var_manager.dual_value("x^2 <= 1"), 0, atol=1e-7)
    assert np.isclose(dual_solver.dual_var_manager.dual_value("s1 > 0"), 0, atol=1e-7)
