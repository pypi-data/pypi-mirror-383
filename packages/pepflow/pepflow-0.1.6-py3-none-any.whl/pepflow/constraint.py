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

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from pepflow.scalar import Scalar

from pepflow import utils


@attrs.frozen
class Constraint:
    """A :class:`Constraint` object that represents inequalities and
    equalities of :class:`Scalar` objects.

    Denote a arbitrary :class:`Scalar` objects as `x` and `y`. Constraints represent:
    `x <= y`, `x >= y`, and `x = y`.

    Attributes:
        lhs (:class:`Scalar`): The :class:`Scalar` object on the left hand side of
            the relation.
        rhs (:class:`Scalar`): The :class:`Scalar` object on the right hand side of
            the relation.
        cmp (:class:`Comparator`): :class:`Comparator` is an enumeration
            that can be either `GE`, `LE`, or `EQ`. They represent `>=`, `<=`,
            and `=` respectively.
        name (str): The unique name of the :class:`Comparator` object.
        associated_dual_var_constraints (list[tuple[utils.Comparator, float]]):
            A list of all the constraints imposed on the associated dual
            variable of this :class:`Constraint` object.
    """

    lhs: Scalar | float
    rhs: Scalar | float
    cmp: utils.Comparator
    name: str

    # Used to represent the constraint on primal variable in dual PEP.
    associated_dual_var_constraints: list[tuple[utils.Comparator, float]] = attrs.field(
        factory=list
    )

    @classmethod
    def make(
        cls: type[Constraint],
        lhs: Scalar | float,
        op: str,
        rhs: Scalar | float,
        name: str,
    ) -> Constraint:
        """
        A static method to construct a :class:`Constraint` object.

        Args:
            lhs (:class:`Scalar` | float): The :class:`Scalar` object on the
                left hand side of the relation.
            op (str): A `str` which represents the type of relation. Possible options
                are `le`, `ge`, `lt`, `gt`, `eq`, `<=`, `>=`, `<`, `>`, or `==`.
            rhs (:class:`Scalar` | float): The :class:`Scalar` object on the
                right hand side of the relation.
            name (str): The unique name of the constructed :class:`Comparator` object.
        """
        cmp = utils.Comparator.from_str(op)
        return cls(lhs, rhs, cmp, name)

    def dual_le(self, val: float) -> None:
        """
        Generates a `<=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd <= val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.LE, val))

    def dual_ge(self, val: float) -> None:
        """
        Generates a `>=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd >= val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.GE, val))

    def dual_eq(self, val: float) -> None:
        """
        Generates a `=` constraint on the dual variable associated with this
        constraint.

        Denote the associated dual variable of this constraint as `lambd`.
        This generates a relation of the form `lambd = val`.

        Args:
            val (float): The other object in the relation.
        """
        if not utils.is_numerical(val):
            raise ValueError(f"The input {val=} must be a numerical value")
        self.associated_dual_var_constraints.append((utils.Comparator.EQ, val))
