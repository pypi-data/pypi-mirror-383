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
from pepflow import pep as pep
from pepflow import pep_context as pc
from pepflow import scalar, utils
from pepflow.constraint import Constraint


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""
    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)


def test_constraint(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, tags=["s2"])
    s3 = 2 * s1 + s2 / 4 + 5

    c1 = Constraint.make(s3, "<=", 5, "c1")
    c2 = Constraint.make(s3, "<", 5, "c2")
    c3 = Constraint.make(s3, ">=", 5, "c3")
    c4 = Constraint.make(s3, ">", 5, "c4")
    c5 = Constraint.make(s3, "==", 5, "c5")

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(c1.lhs - c1.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c1.lhs - c1.rhs).offset, 0)
    assert c1.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c2.lhs - c2.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c2.lhs - c2.rhs).offset, 0)
    assert c2.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c3.lhs - c3.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c3.lhs - c3.rhs).offset, 0)
    assert c3.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c4.lhs - c4.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c4.lhs - c4.rhs).offset, 0)
    assert c4.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c5.lhs - c5.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c5.lhs - c5.rhs).offset, 0)
    assert c5.cmp == utils.Comparator.EQ


def test_constraint_from_scalar(pep_context: pc.PEPContext):
    s1 = scalar.Scalar(is_basis=True, tags=["s1"])
    s2 = scalar.Scalar(is_basis=True, tags=["s2"])
    s3 = 2 * s1 + s2 / 4 + 5

    c1 = s3.lt(5, "c2")
    c2 = s3.le(5, "c2")
    c3 = s3.gt(5, "c2")
    c4 = s3.ge(5, "c2")
    c5 = s3.eq(5, "c2")

    pm = exm.ExpressionManager(pep_context)

    np.testing.assert_allclose(
        pm.eval_scalar(c1.lhs - c1.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c1.lhs - c1.rhs).offset, 0)
    assert c1.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c2.lhs - c2.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c2.lhs - c2.rhs).offset, 0)
    assert c2.cmp == utils.Comparator.LE

    np.testing.assert_allclose(
        pm.eval_scalar(c3.lhs - c3.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c3.lhs - c3.rhs).offset, 0)
    assert c3.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c4.lhs - c4.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c4.lhs - c4.rhs).offset, 0)
    assert c4.cmp == utils.Comparator.GE

    np.testing.assert_allclose(
        pm.eval_scalar(c5.lhs - c5.rhs).func_coords, np.array([2, 0.25])
    )
    np.testing.assert_allclose(pm.eval_scalar(c5.lhs - c5.rhs).offset, 0)
    assert c5.cmp == utils.Comparator.EQ
