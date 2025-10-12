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

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import natsort
import pandas as pd

from pepflow import utils

if TYPE_CHECKING:
    from pepflow.function import Function, Triplet
    from pepflow.scalar import Scalar
    from pepflow.vector import Vector

# A global variable for storing the current context that manages objects
# such as vectors and scalars.
CURRENT_CONTEXT: PEPContext | None = None
# Keep the track of all previous created contexts.
GLOBAL_CONTEXT_DICT: dict[str, PEPContext] = {}


def get_current_context() -> PEPContext | None:
    """
    Return the current global :class:`PEPContext`.

    Returns:
        :class:`PEPContext`: The current global :class:`PEPContext`.
    """
    return CURRENT_CONTEXT


def set_current_context(ctx: PEPContext | None):
    """
    Change the current global :class:`PEPContext`.

    Args:
        ctx (:class:`PEPContext`): The :class:`PEPContext` to set as the new
            global :class:`PEPContext`.
    """
    global CURRENT_CONTEXT
    assert ctx is None or isinstance(ctx, PEPContext)
    CURRENT_CONTEXT = ctx


class PEPContext:
    """
    A :class:`PEPContext` object is a context manager which maintains
    the abstract mathematical objects of the Primal and Dual PEP.

    Attributes:
        name (str): The unique name of the :class:`PEPContext` object.
    """

    def __init__(self, name: str):
        self.name = name
        self.vectors: list[Vector] = []
        self.scalars: list[Scalar] = []
        self.triplets: dict[Function, list[Triplet]] = defaultdict(list)
        # self.triplets will contain all stationary_triplets. They are not mutually exclusive.
        self.stationary_triplets: dict[Function, list[Triplet]] = defaultdict(list)

        GLOBAL_CONTEXT_DICT[name] = self

    def set_as_current(self) -> PEPContext:
        """
        Set this :class:`PEPContext` object as the global context.

        Returns:
            :class:`PEPContext`: This :class:`PEPContext` object.
        """
        set_current_context(self)
        return self

    def add_vector(self, vector: Vector):
        self.vectors.append(vector)

    def add_scalar(self, scalar: Scalar):
        self.scalars.append(scalar)

    def add_triplet(self, function: Function, triplet: Triplet):
        self.triplets[function].append(triplet)

    def add_stationary_triplet(self, function: Function, stationary_triplet: Triplet):
        self.stationary_triplets[function].append(stationary_triplet)

    def get_by_tag(self, tag: str) -> Vector | Scalar:
        """
        Under this :class:`PEPContext`, get the :class:`Vector` or
        :class:`Scalar` object associated with the provided `tag`.

        Args:
            tag (str): The tag of the :class:`Vector` or :class:`Scalar` object
                we want to retrieve.

        Returns:
            :class:`Vector` | :class:`Scalar`: The :class:`Vector` or
            :class:`Scalar` object associated with the provided `tag`.
        """
        for p in self.vectors:
            if tag in p.tags:
                return p
        for s in self.scalars:
            if tag in s.tags:
                return s
        raise ValueError("Cannot find the vector, scalar, or function of given tag.")

    def clear(self):
        """Reset this :class:`PEPContext` object."""
        self.vectors.clear()
        self.scalars.clear()
        self.triplets.clear()
        self.stationary_triplets.clear()

    def tracked_point(self, func: Function) -> list[Vector]:
        """
        This function returns a list of the visited vectors :math:`\\{x_i\\}` under
        this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient.

        Args:
            func (:class:`Function`): The function associated with the set
                of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}`.

        Returns:
            list[:class:`Vector`]: The list of the visited vectors
            :math:`\\{x_i\\}`.
        """
        return natsort.natsorted(
            [t.point for t in self.triplets[func]], key=lambda x: x.tag
        )

    def tracked_grad(self, func: Function) -> list[Vector]:
        """
        This function returns a list of the visited
        gradients :math:`\\{\\nabla f(x_i)\\}` under this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient
        :math:`\\nabla f(x_i)`.

        Args:
            func (:class:`Function`): The function associated with the set
                of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}`.

        Returns:
            list[:class:`Vector`]: The list of the visited gradients
            :math:`\\{\\nabla f(x_i)\\}`.
        """
        return natsort.natsorted(
            [t.grad for t in self.triplets[func]], key=lambda x: x.tag
        )

    def tracked_func_val(self, func: Function) -> list[Scalar]:
        """
        This function returns a list of the visited
        function values :math:`\\{f(x_i)\\}` under this :class:`PEPContext`.

        Each function :math:`f` used in Primal and Dual PEP is associated with
        a set of triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}` visited by
        the considered algorithm. We can also consider a subgradient
        :math:`\\widetilde{\\nabla} f(x)` instead of the gradient
        :math:`\\nabla f(x_i)`.

        Args:
            func (:class:`Function`): The function associated with the set of
                triplets :math:`\\{x_i, f(x_i), \\nabla f(x_i)\\}`.

        Returns:
            list[:class:`Scalar`]: The list of the visited function values
            :math:`\\{f(x_i)\\}`.
        """
        return natsort.natsorted(
            [t.func_val for t in self.triplets[func]], key=lambda x: x.tag
        )

    def order_of_point(self, func: Function) -> list[str]:
        return natsort.natsorted([t.point.tag for t in self.triplets[func]])

    def triplets_to_df_and_order(
        self,
    ) -> tuple[dict[Function, pd.DataFrame], dict[Function, list[str]]]:
        func_to_df: dict[Function, pd.DataFrame] = {}
        func_to_order: dict[Function, list[str]] = {}

        for func, triplets in self.triplets.items():
            order = self.order_of_point(func)
            df = pd.DataFrame(
                [
                    (
                        constraint.name,
                        *utils.name_to_vector_tuple(constraint.name),
                    )
                    for constraint in func.get_interpolation_constraints(self)
                ],
                columns=["constraint_name", "col_point", "row_point"],
            )
            df["row"] = df["row_point"].map(lambda x: order.index(x))
            df["col"] = df["col_point"].map(lambda x: order.index(x))
            func_to_df[func] = df
            func_to_order[func] = order

        return func_to_df, func_to_order

    def triplets_to_df_and_order_one_function(
        self, func: Function
    ) -> tuple[pd.DataFrame, list[str]]:
        one_func_df: pd.DataFrame
        one_func_order: list[str]

        if func not in self.triplets.keys():
            raise ValueError(
                "This function has no associate triplets for this given context."
            )

        one_func_order = self.order_of_point(func)

        one_func_df = pd.DataFrame(
            [
                (
                    constraint.name,
                    *utils.name_to_vector_tuple(constraint.name),
                )
                for constraint in func.get_interpolation_constraints(self)
            ],
            columns=["constraint_name", "col_point", "row_point"],
        )
        one_func_df["row"] = one_func_df["row_point"].map(
            lambda x: one_func_order.index(x)
        )
        one_func_df["col"] = one_func_df["col_point"].map(
            lambda x: one_func_order.index(x)
        )

        return one_func_df, one_func_order

    def basis_vectors(self) -> list[Vector]:
        """
        Return a list of the basis :class:`Vector` objects managed by this
        :class:`PEPContext`.

        Returns:
            list[:class:`Vector`]: A list of the basis :class:`Vector` objects
            managed by this :class:`PEPContext`.
        """
        return [
            p for p in self.vectors if p.is_basis
        ]  # Note the order is always the same as added time

    def basis_scalars(self) -> list[Scalar]:
        """
        Return a list of the basis :class:`Scalar` objects managed by this
        :class:`PEPContext`.

        Returns:
            list[:class:`Scalar`]: A list of the basis :class:`Scalar` objects
            managed by this :class:`PEPContext`.
        """
        return [
            s for s in self.scalars if s.is_basis
        ]  # Note the order is always the same as added time
