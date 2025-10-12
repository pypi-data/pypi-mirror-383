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

import time
from typing import Iterator

import numpy as np
import pytest

from pepflow import expression_manager as exm
from pepflow import parameter
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""
    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)


def test_vector_add_tag(pep_context: pc.PEPContext) -> None:
    p1 = vector.Vector(is_basis=True, eval_expression=None, tags=["p1"])
    p2 = vector.Vector(is_basis=True, eval_expression=None, tags=["p2"])

    p_add = p1 + p2
    assert p_add.tag == "p1+p2"

    p_sub = p1 - p2
    assert p_sub.tag == "p1-p2"

    p_sub = p1 - (p2 + p1)
    assert p_sub.tag == "p1-(p2+p1)"

    p_sub = p1 - (p2 - p1)
    assert p_sub.tag == "p1-(p2-p1)"


def test_vector_mul_tag(pep_context: pc.PEPContext) -> None:
    p = vector.Vector(is_basis=True, eval_expression=None, tags=["p"])

    p_mul = p * 0.1
    assert p_mul.tag == "p*0.1"

    p_rmul = 0.1 * p
    assert p_rmul.tag == "0.1*p"

    p_pow = p**2
    assert p_pow.tag == "|p|^2"

    p_neg = -p
    assert p_neg.tag == "-p"

    p_truediv = p / 0.1
    assert p_truediv.tag == "1/0.1*p"


def test_vector_add_and_mul_tag(pep_context: pc.PEPContext) -> None:
    p1 = vector.Vector(is_basis=True, eval_expression=None, tags=["p1"])
    p2 = vector.Vector(is_basis=True, eval_expression=None, tags=["p2"])

    p_add_mul = (p1 + p2) * 0.1
    assert p_add_mul.tag == "(p1+p2)*0.1"

    p_add_mul = (p1 + p2) * (p1 + p2)
    assert p_add_mul.tag == "(p1+p2)*(p1+p2)"

    p_add_pow = (p1 + p2) ** 2
    assert p_add_pow.tag == "|p1+p2|^2"

    p_add_mul = p1 + p2 * 0.1
    assert p_add_mul.tag == "p1+p2*0.1"

    p_neg_add = -(p1 + p2)
    assert p_neg_add.tag == "-(p1+p2)"

    p_rmul_add = 0.1 * (p1 + p2)
    assert p_rmul_add.tag == "0.1*(p1+p2)"


def test_vector_hash_different(pep_context: pc.PEPContext) -> None:
    p1 = vector.Vector(is_basis=True, eval_expression=None)
    p2 = vector.Vector(is_basis=True, eval_expression=None)
    assert p1.uid != p2.uid


def test_vector_tag(pep_context: pc.PEPContext) -> None:
    p1 = vector.Vector(is_basis=True, eval_expression=None)
    p1.add_tag(tag="my_tag")
    assert p1.tags == ["my_tag"]
    assert p1.tag == "my_tag"


def test_vector_repr(pep_context: pc.PEPContext) -> None:
    p1 = vector.Vector(is_basis=True)
    assert str(p1) is not None  # it should be fine without tag
    p1.add_tag("my_tag")
    assert str(p1) == "my_tag"


def test_vector_in_a_list(pep_context: pc.PEPContext):
    p1 = vector.Vector(is_basis=True, eval_expression=None)
    p2 = vector.Vector(is_basis=True, eval_expression=None)
    p3 = vector.Vector(is_basis=True, eval_expression=None)
    assert p1 in [p1, p2]
    assert p3 not in [p1, p2]


def test_expression_manager_on_basis_vector(pep_context: pc.PEPContext):
    p1 = vector.Vector(is_basis=True, eval_expression=None, tags=["p1"])
    p2 = vector.Vector(is_basis=True, eval_expression=None, tags=["p2"])
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0]))
    np.testing.assert_allclose(pm.eval_vector(p2).coords, np.array([0, 1]))

    p3 = vector.Vector(is_basis=True, eval_expression=None, tags=["p3"])  # noqa: F841
    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(pm.eval_vector(p1).coords, np.array([1, 0, 0]))
    np.testing.assert_allclose(pm.eval_vector(p2).coords, np.array([0, 1, 0]))


def test_expression_manager_eval_vector(pep_context: pc.PEPContext):
    p1 = vector.Vector(is_basis=True, tags=["p1"])
    p2 = vector.Vector(is_basis=True, tags=["p2"])
    p3 = 2 * p1 + p2 / 4
    p4 = p3 + p1

    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_vector(p3).coords, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_vector(p4).coords, np.array([3, 0.25]))


def test_scalar_eval_and_repr_with_parameter(pep_context: pc.PEPContext):
    p1 = vector.Vector(is_basis=True, tags=["p1"])
    pm1 = parameter.Parameter(name="pm1")
    pm2 = parameter.Parameter(name="pm2")
    p2 = p1 * pm1 - pm2 * p1

    eval_p2 = p2.eval(resolve_parameters={"pm1": 3.3, "pm2": 4.3})
    np.testing.assert_allclose(eval_p2, np.array([-1]))
    assert p2.repr_by_basis(resolve_parameters={"pm1": 3.3, "pm2": 4.3}) == "-p1"


def test_expression_manager_eval_vector_large_scale(pep_context):
    all_basis = [vector.Vector(is_basis=True, tags=[f"p_{i}"]) for i in range(100)]
    p = all_basis[0]
    for i in range(len(all_basis)):
        for j in range(i + 1, len(all_basis)):
            p += all_basis[i] * 2 + all_basis[j]
    pm = exm.ExpressionManager(pep_context)
    t = time.time()
    for pp in pep_context.vectors:
        pm.eval_vector(pp)

    assert (time.time() - t) < 0.5


def test_zero_vector(pep_context):
    _ = vector.Vector(is_basis=True, tags=["p1"])
    p0 = vector.Vector.zero()

    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_vector(p0).coords, np.array([0]))

    _ = vector.Vector(is_basis=True, tags=["p2"])
    pm = exm.ExpressionManager(pep_context)
    np.testing.assert_allclose(pm.eval_vector(p0).coords, np.array([0, 0]))
