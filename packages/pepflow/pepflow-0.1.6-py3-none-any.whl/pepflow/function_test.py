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

from typing import Iterator

import numpy as np
import pytest

from pepflow import expression_manager as exm
from pepflow import function as fc
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""
    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)


def test_function_add_tag(pep_context: pc.PEPContext) -> None:
    f1 = fc.Function(is_basis=True, tags=["f1"])
    f2 = fc.Function(is_basis=True, tags=["f2"])

    f_add = f1 + f2
    assert f_add.tag == "f1+f2"

    f_sub = f1 - f2
    assert f_sub.tag == "f1-f2"

    f_sub = f1 - (f2 + f1)
    assert f_sub.tag == "f1-(f2+f1)"

    f_sub = f1 - (f2 - f1)
    assert f_sub.tag == "f1-(f2-f1)"


def test_function_mul_tag(pep_context: pc.PEPContext) -> None:
    f = fc.Function(is_basis=True, tags=["f"])

    f_mul = f * 0.1
    assert f_mul.tag == "0.1*f"

    f_rmul = 0.1 * f
    assert f_rmul.tag == "0.1*f"

    f_neg = -f
    assert f_neg.tag == "-f"

    f_truediv = f / 0.1
    assert f_truediv.tag == "1/0.1*f"


def test_function_add_and_mul_tag(pep_context: pc.PEPContext) -> None:
    f1 = fc.Function(is_basis=True, tags=["f1"])
    f2 = fc.Function(is_basis=True, tags=["f2"])

    f_add_mul = (f1 + f2) * 0.1
    assert f_add_mul.tag == "0.1*(f1+f2)"

    f_add_mul = f1 + f2 * 0.1
    assert f_add_mul.tag == "f1+0.1*f2"

    f_neg_add = -(f1 + f2)
    assert f_neg_add.tag == "-(f1+f2)"

    f_rmul_add = 0.1 * (f1 + f2)
    assert f_rmul_add.tag == "0.1*(f1+f2)"

    f_rmul_add = f1 + 5 * (f2 + 3 * f1)
    assert f_rmul_add.tag == "f1+5*(f2+3*f1)"

    f_multiple_add = f1 + f1 + f1 + f1 + f1 + f1
    assert f_multiple_add.tag == "f1+f1+f1+f1+f1+f1"


def test_function_call(pep_context: pc.PEPContext) -> None:
    f = fc.Function(is_basis=True, tags=["f"])
    x = vector.Vector(is_basis=True, eval_expression=None, tags=["x"])
    assert f.func_val(x) == f(x)


def test_function_repr(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
    )
    print(f)  # it should be fine without tag
    f.add_tag("f")
    assert str(f) == "f"


def test_stationary_point(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    f.set_stationary_point("x_star")

    assert len(pep_context.triplets) == 1
    assert len(pep_context.triplets[f]) == 1

    f_triplet = pep_context.triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert f_triplet.grad.tag == "grad_f(x_star)"
    assert f_triplet.func_val.tag == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_stationary_point_scaled(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
        tags=["f"],
    )
    g = 5 * f
    g.set_stationary_point("x_star")

    assert len(pep_context.triplets) == 1
    assert len(pep_context.triplets[f]) == 1

    f_triplet = pep_context.triplets[f][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert f_triplet.grad.tag == "grad_f(x_star)"
    assert f_triplet.func_val.tag == "f(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0]))
    np.testing.assert_allclose(em.eval_vector(f_triplet.point).coords, np.array([1]))


def test_stationary_point_additive(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True)
    f.add_tag("f")
    g = fc.Function(is_basis=True)
    g.add_tag("g")
    h = f + g
    h.add_tag("h")

    h.set_stationary_point("x_star")
    assert len(pep_context.triplets) == 2
    assert len(pep_context.triplets[f]) == 1
    assert len(pep_context.triplets[g]) == 1

    f_triplet = pep_context.triplets[f][0]
    g_triplet = pep_context.triplets[g][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert g_triplet.name == "x_star_g(x_star)_grad_g(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0, 1]))
    np.testing.assert_allclose(em.eval_vector(g_triplet.grad).coords, np.array([0, -1]))


def test_stationary_point_linear_combination(pep_context: pc.PEPContext):
    f = fc.Function(
        is_basis=True,
    )
    f.add_tag("f")
    g = fc.Function(
        is_basis=True,
    )
    g.add_tag("g")
    h = 3 * f + 2 * g
    h.add_tag("h")

    h.set_stationary_point("x_star")
    assert len(pep_context.triplets) == 2
    assert len(pep_context.triplets[f]) == 1
    assert len(pep_context.triplets[g]) == 1

    f_triplet = pep_context.triplets[f][0]
    g_triplet = pep_context.triplets[g][0]
    assert f_triplet.name == "x_star_f(x_star)_grad_f(x_star)"
    assert g_triplet.name == "x_star_g(x_star)_grad_g(x_star)"

    em = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(em.eval_vector(f_triplet.grad).coords, np.array([0, 1]))
    np.testing.assert_allclose(
        em.eval_vector(g_triplet.grad).coords, np.array([0, -1.5])
    )


def test_function_generate_triplet(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True)
    f.add_tag("f")
    g = fc.Function(is_basis=True)
    g.add_tag("g")
    h = 5 * f + 5 * g
    h.add_tag("h")

    p1 = vector.Vector(is_basis=True)
    p1.add_tag("p1")
    p1_triplet = h.generate_triplet(p1)
    p1_triplet_1 = h.generate_triplet(p1)

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0]))

    np.testing.assert_allclose(
        pm.eval_vector(p1_triplet.grad).coords, np.array([0, 5, 5])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(p1_triplet.func_val).func_coords, np.array([5, 5])
    )

    np.testing.assert_allclose(
        pm.eval_vector(p1_triplet_1.grad).coords, np.array([0, 5, 5])
    )
    np.testing.assert_allclose(
        pm.eval_scalar(p1_triplet_1.func_val).func_coords, np.array([5, 5])
    )


def test_function_add_stationary_point(pep_context: pc.PEPContext):
    f = fc.Function(is_basis=True)
    f.add_tag("f")
    x_opt = f.set_stationary_point("x_opt")

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(x_opt).coords, np.array([1]))


def test_smooth_interpolability_constraints(pep_context: pc.PEPContext):
    f = fc.SmoothConvexFunction(L=1)
    f.add_tag("f")
    _ = f.set_stationary_point("x_opt")

    x_0 = vector.Vector(is_basis=True)
    x_0.add_tag("x_0")
    _ = f.generate_triplet(x_0)

    all_interpolation_constraints = f.get_interpolation_constraints()

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).func_coords,
        [1, -1],
    )
    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).inner_prod_coords,
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.5]],
    )

    np.testing.assert_allclose(
        pm.eval_scalar(
            all_interpolation_constraints[1].lhs - all_interpolation_constraints[1].rhs
        ).offset,
        0,
    )
