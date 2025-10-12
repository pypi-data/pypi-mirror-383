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

import pandas as pd
import pytest

from pepflow import pep_context as pc
from pepflow.function import SmoothConvexFunction
from pepflow.scalar import Scalar
from pepflow.vector import Vector


@pytest.fixture
def pep_context() -> Iterator[pc.PEPContext]:
    """Prepare the pep context and reset the context to None at the end."""
    ctx = pc.PEPContext("test").set_as_current()
    yield ctx
    pc.set_current_context(None)


def test_tracked_points(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")

    p1 = Vector(is_basis=True, tags=["x_1"])
    p2 = Vector(is_basis=True, tags=["x_3"])
    p3 = Vector(is_basis=True, tags=["x_2"])
    p_star = Vector(is_basis=True, tags=["x_*"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)
    _ = f.generate_triplet(p3)
    _ = f.generate_triplet(p_star)

    assert pep_context.order_of_point(f) == ["x_1", "x_2", "x_3", "x_*"]
    assert pep_context.tracked_point(f) == [p1, p3, p2, p_star]


def test_triplets_to_dataframe(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")

    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x3"])
    p3 = Vector(is_basis=True, tags=["x2"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)
    _ = f.generate_triplet(p3)

    func_to_df, func_to_order = pep_context.triplets_to_df_and_order()
    expected_df = pd.DataFrame(
        {
            "constraint_name": [
                "f:x1,x3",
                "f:x1,x2",
                "f:x3,x1",
                "f:x3,x2",
                "f:x2,x1",
                "f:x2,x3",
            ],
            "col_point": ["x1", "x1", "x3", "x3", "x2", "x2"],
            "row_point": ["x3", "x2", "x1", "x2", "x1", "x3"],
            "row": [2, 1, 0, 1, 0, 2],
            "col": [0, 0, 2, 2, 1, 1],
        }
    )

    pd.testing.assert_frame_equal(func_to_df[f], expected_df)
    assert func_to_order[f] == ["x1", "x2", "x3"]


def test_triplets_to_dataframe_one_function(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")

    g = SmoothConvexFunction(L=1, is_basis=True)
    g.add_tag("g")

    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x3"])
    p3 = Vector(is_basis=True, tags=["x2"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)
    _ = f.generate_triplet(p3)

    df, order = pep_context.triplets_to_df_and_order_one_function(f)
    expected_df = pd.DataFrame(
        {
            "constraint_name": [
                "f:x1,x3",
                "f:x1,x2",
                "f:x3,x1",
                "f:x3,x2",
                "f:x2,x1",
                "f:x2,x3",
            ],
            "col_point": ["x1", "x1", "x3", "x3", "x2", "x2"],
            "row_point": ["x3", "x2", "x1", "x2", "x1", "x3"],
            "row": [2, 1, 0, 1, 0, 2],
            "col": [0, 0, 2, 2, 1, 1],
        }
    )

    pd.testing.assert_frame_equal(df, expected_df)
    assert order == ["x1", "x2", "x3"]

    with pytest.raises(
        ValueError,
        match="This function has no associate triplets for this given context.",
    ):
        pep_context.triplets_to_df_and_order_one_function(g)


def test_get_by_tag(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    p3 = p1 + p2

    triplet = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.get_by_tag("x1") == p1
    assert pep_context.get_by_tag("f(x1)") == triplet.func_val
    assert pep_context.get_by_tag("grad_f(x1)") == triplet.grad
    assert pep_context.get_by_tag("x1+x2") == p3
    pc.set_current_context(None)


def test_basis_vectors(pep_context: pc.PEPContext):
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    _ = p1 + p2  # not basis
    ps = Vector(is_basis=True, tags=["x_star"])
    p0 = Vector(is_basis=True, tags=["x0"])

    assert pep_context.basis_vectors() == [p1, p2, ps, p0]


def test_basis_scalars(pep_context: pc.PEPContext):
    p1 = Vector(is_basis=True, tags=["x1"])
    p2 = Vector(is_basis=True, tags=["x2"])
    _ = p1 * p2  # not basis
    s1 = Scalar(is_basis=True, tags=["s2"])
    s2 = Scalar(is_basis=True, tags=["s1"])

    assert pep_context.basis_scalars() == [s1, s2]


def test_tracked_point(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.tracked_point(f) == [p2, p1]


def tracked_grad(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    triplet1 = f.generate_triplet(p1)
    triplet2 = f.generate_triplet(p2)

    assert pep_context.tracked_grad(f) == [triplet2.grad, triplet1.grad]


def tracked_func_val(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    triplet1 = f.generate_triplet(p1)
    triplet2 = f.generate_triplet(p2)

    assert pep_context.tracked_func_val(f) == [triplet2.func_val, triplet1.func_val]


def test_order_of_point(pep_context: pc.PEPContext):
    f = SmoothConvexFunction(L=1, is_basis=True)
    f.add_tag("f")
    p1 = Vector(is_basis=True, tags=["x2"])
    p2 = Vector(is_basis=True, tags=["x1"])

    _ = f.generate_triplet(p1)
    _ = f.generate_triplet(p2)

    assert pep_context.order_of_point(f) == [p2.tag, p1.tag]
