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

import uuid
from typing import TYPE_CHECKING, Any

import attrs
import numpy as np

from pepflow import constraint as ctr
from pepflow import pep_context as pc
from pepflow import utils

if TYPE_CHECKING:
    from pepflow.vector import Vector


def is_numerical_or_scalar(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, Scalar)


def is_numerical_or_evaluatedscalar(val: Any) -> bool:
    return utils.is_numerical_or_parameter(val) or isinstance(val, EvaluatedScalar)


@attrs.frozen
class ScalarRepresentation:
    op: utils.Op
    left_scalar: Vector | Scalar | float
    right_scalar: Vector | Scalar | float


@attrs.frozen
class ZeroScalar:
    """A special class to represent 0 in scalar."""

    pass


@attrs.frozen
class EvaluatedScalar:
    """
    The concrete representation of the abstract :class:`Scalar`.

    Each abstract basis :class:`Scalar` object has a unique concrete
    representation as a unit vector. The concrete representations of
    linear combinations of abstract basis :class:`Scalar` objects
    are linear combinations of the unit vectors. This information is
    stored in the `vector` attribute.

    Abstract :class:`Scalar` objects can be formed through taking the
    inner product of two abstract :class:`Vector` objects. The
    concrete representation of an abstract :class:`Scalar` object formed
    this way is the outer product of the concrete representations of the
    two abstract :class:`Vector` objects, i.e., a matrix. This information
    is stored in the `matrix` attribute.

    Abstract :class:`Scalar` objects can be added or subtracted with
    numeric data types. This information is stored in the `constant`
    attribute.

    :class:`EvaluatedScalar` objects can be constructed as linear combinations
    of other :class:`EvaluatedScalar` objects. Let `a` and `b` be some numeric
    data type. Let `u` and `v` be :class:`EvaluatedScalar` objects. Then, we
    can form a new :class:`EvaluatedScalar` object: `a*u+b*v`.

    Attributes:
        vector (np.ndarray): The vector component of the concrete
            representation of the abstract :class:`Scalar`.
        matrix (np.ndarray): The matrix component of the concrete
            representation of the abstract :class:`Scalar`.
        constant (float): The constant component of the concrete
            representation of the abstract :class:`Scalar`.
    """

    func_coords: np.ndarray
    inner_prod_coords: np.ndarray
    offset: float

    @property
    def matrix(self) -> np.ndarray:
        # A short alias for inner_prod_coords.
        return self.inner_prod_coords

    @classmethod
    def zero(cls, num_basis_scalars: int, num_basis_vectors: int):
        return EvaluatedScalar(
            func_coords=np.zeros(num_basis_scalars),
            inner_prod_coords=np.zeros((num_basis_vectors, num_basis_vectors)),
            offset=0.0,
        )

    def __add__(self, other):
        if not is_numerical_or_evaluatedscalar(other):
            return NotImplemented
        if utils.is_numerical(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=self.offset + other,
            )
        else:
            return EvaluatedScalar(
                func_coords=self.func_coords + other.func_coords,
                inner_prod_coords=self.inner_prod_coords + other.inner_prod_coords,
                offset=self.offset + other.offset,
            )

    def __radd__(self, other):
        if not is_numerical_or_evaluatedscalar(other):
            return NotImplemented
        if utils.is_numerical(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=other + self.offset,
            )
        else:
            return EvaluatedScalar(
                func_coords=other.func_coords + self.func_coords,
                inner_prod_coords=other.inner_prod_coords + self.inner_prod_coords,
                offset=other.offset + self.offset,
            )

    def __sub__(self, other):
        if not is_numerical_or_evaluatedscalar(other):
            return NotImplemented
        if utils.is_numerical(other):
            return EvaluatedScalar(
                func_coords=self.func_coords,
                inner_prod_coords=self.inner_prod_coords,
                offset=self.offset - other,
            )
        else:
            return EvaluatedScalar(
                func_coords=self.func_coords - other.func_coords,
                inner_prod_coords=self.inner_prod_coords - other.inner_prod_coords,
                offset=self.offset - other.offset,
            )

    def __rsub__(self, other):
        if not is_numerical_or_evaluatedscalar(other):
            return NotImplemented
        if utils.is_numerical(other):
            return EvaluatedScalar(
                func_coords=-self.func_coords,
                inner_prod_coords=-self.inner_prod_coords,
                offset=other - self.offset,
            )
        else:
            return EvaluatedScalar(
                func_coords=other.func_coords - self.func_coords,
                inner_prod_coords=other.inner_prod_coords - self.inner_prod_coords,
                offset=other.offset - self.offset,
            )

    def __mul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        return EvaluatedScalar(
            func_coords=self.func_coords * other,
            inner_prod_coords=self.inner_prod_coords * other,
            offset=self.offset * other,
        )

    def __rmul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        return EvaluatedScalar(
            func_coords=other * self.func_coords,
            inner_prod_coords=other * self.inner_prod_coords,
            offset=other * self.offset,
        )

    def __neg__(self):
        return self.__rmul__(other=-1)

    def __truediv__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        return EvaluatedScalar(
            func_coords=self.func_coords / other,
            inner_prod_coords=self.inner_prod_coords / other,
            offset=self.offset / other,
        )


@attrs.frozen
class Scalar:
    """
    A :class:`Scalar` object represents linear combination of functions values,
    inner products of , and constant scalar values.

    :class:`Scalar` objects can be constructed as linear combinations of
    other :class:`Scalar` objects. Let `a` and `b` be some numeric data type.
    Let `x` and `y` be :class:`Scalar` objects. Then, we can form a new
    :class:`Scalar` object: `a*x+b*y`.

    Attributes:
        is_basis (bool): True if this scalar is not formed through a linear
            combination of other scalars. False otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Vector` object. Tags should be unique.
    """

    # If true, the scalar is the basis for the evaluations of F
    is_basis: bool

    # The representation of scalar used for evaluation.
    eval_expression: ScalarRepresentation | ZeroScalar | None = None

    # Human tagged value for the scalar
    tags: list[str] = attrs.field(factory=list)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.eval_expression is None
        else:
            assert self.eval_expression is not None

        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.add_scalar(self)

    @staticmethod
    def zero() -> Scalar:
        return Scalar(is_basis=False, eval_expression=ZeroScalar(), tags=["0"])

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Scalar` object.
        """
        if len(self.tags) == 0:
            raise ValueError("Scalar should have a name.")
        return self.tags[-1]

    def add_tag(self, tag: str):
        """Add a new tag for this :class:`Scalar` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.
        """
        self.tags.append(tag)

    def __repr__(self):
        if self.tags:
            return self.tag
        return super().__repr__()

    def _repr_latex_(self):
        return utils.str_to_latex(repr(self))

    def __add__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            tag_other = utils.numerical_str(other)
        else:
            tag_other = other.tag
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.ADD, self, other),
            tags=[f"{self.tag}+{tag_other}"],
        )

    def __radd__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            tag_other = utils.numerical_str(other)
        else:
            tag_other = other.tag
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.ADD, other, self),
            tags=[f"{tag_other}+{self.tag}"],
        )

    def __sub__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        if utils.is_numerical_or_parameter(other):
            tag_other = utils.numerical_str(other)
        else:
            tag_other = utils.parenthesize_tag(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.SUB, self, other),
            tags=[f"{self.tag}-{tag_other}"],
        )

    def __rsub__(self, other):
        if not is_numerical_or_scalar(other):
            return NotImplemented
        tag_self = utils.parenthesize_tag(self)
        if utils.is_numerical_or_parameter(other):
            tag_other = utils.numerical_str(other)
        else:
            tag_other = other.tag
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.SUB, other, self),
            tags=[f"{tag_other}-{tag_self}"],
        )

    def __mul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        tag_self = utils.parenthesize_tag(self)
        tag_other = utils.numerical_str(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, self, other),
            tags=[f"{tag_self}*{tag_other}"],
        )

    def __rmul__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        tag_self = utils.parenthesize_tag(self)
        tag_other = utils.numerical_str(other)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, other, self),
            tags=[f"{tag_other}*{tag_self}"],
        )

    def __neg__(self):
        tag_self = utils.parenthesize_tag(self)
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.MUL, -1, self),
            tags=[f"-{tag_self}"],
        )

    def __truediv__(self, other):
        if not utils.is_numerical_or_parameter(other):
            return NotImplemented
        tag_self = utils.parenthesize_tag(self)
        tag_other = f"1/{utils.numerical_str(other)}"
        return Scalar(
            is_basis=False,
            eval_expression=ScalarRepresentation(utils.Op.DIV, self, other),
            tags=[f"{tag_other}*{tag_self}"],
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Scalar):
            return NotImplemented
        return self.uid == other.uid

    def le(self, other: Scalar | float | int, name: str) -> ctr.Constraint:
        """
        Generate a :class:`Constraint` object that represents the inequality
        `self` <= `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`Constraint` object.

        Returns:
            :class:`Constraint`: An object that represents the inequality
            `self` <= `other`.
        """
        return ctr.Constraint(self, other, cmp=utils.Comparator.LE, name=name)

    def lt(self, other: Scalar | float | int, name: str) -> ctr.Constraint:
        """
        Generate a :class:`Constraint` object that represents the inequality
        `self` < `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`Constraint` object.

        Returns:
            :class:`Constraint`: An object that represents the inequality
            `self` < `other`.
        """
        return ctr.Constraint(self, other, cmp=utils.Comparator.LE, name=name)

    def ge(self, other: Scalar | float | int, name: str) -> ctr.Constraint:
        """
        Generate a :class:`Constraint` object that represents the inequality
        `self` >= `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`Constraint` object.

        Returns:
            :class:`Constraint`: An object that represents the inequality
            `self` >= `other`.
        """
        return ctr.Constraint(self, other, cmp=utils.Comparator.GE, name=name)

    def gt(self, other: Scalar | float | int, name: str) -> ctr.Constraint:
        """
        Generate a :class:`Constraint` object that represents the inequality
        `self` > `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`Constraint` object.

        Returns:
            :class:`Constraint`: An object that represents the inequality
            `self` > `other`.
        """
        return ctr.Constraint(self, other, cmp=utils.Comparator.GE, name=name)

    def eq(self, other: Scalar | float | int, name: str) -> ctr.Constraint:
        """
        Generate a :class:`Constraint` object that represents the inequality
        `self` = `other`.

        Args:
            other (:class:`Scalar` | float | int): The other side of the
                relation.
            name (str): The name of the generated :class:`Constraint` object.

        Returns:
            :class:`Constraint`: An object that represents the inequality
            `self` = `other`.
        """
        return ctr.Constraint(self, other, cmp=utils.Comparator.EQ, name=name)

    def eval(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ) -> EvaluatedScalar:
        """
        Return the concrete representation of this :class:`Scalar`.

        Concrete representations of :class:`Scalar` objects are
        :class:`EvaluatedScalar` objects.

        Args:
            ctx (:class:`PEPContext` | None): The :class:`PEPContext` object
                we consider. `None` if we consider the current global
                :class:`PEPContext` object.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
                maps the name of parameters to the numerical values.

        Returns:
            :class:`EvaluatedScalar`: The concrete representation of
            this :class:`Scalar`.
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.eval_scalar(self)

    def repr_by_basis(
        self,
        ctx: pc.PEPContext | None = None,
        *,
        greedy_square: bool = True,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ) -> str:
        """Express this :class:`Scalar` object in terms of the basis :class:`Vector`
        and :class:`Scalar` objects of the given :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str` where,
        to refer to the basis :class:`Vector` and :class:`Scalar` objects, we
        use their tags.

        Args:
            ctx (:class:`PEPContext`): The :class:`PEPContext` object
                whose basis :class:`Vector` and :class:`Scalar` objects we
                consider. `None` if we consider the current global
                `PEPContext` object.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
                maps the name of parameters to the numerical values.

        Returns:
            str: The representation of this :class:`Scalar` object in terms of
            the basis :class:`Vector` and :class:`Scalar` objects of the given
            :class:`PEPContext`.
        """
        from pepflow.expression_manager import ExpressionManager

        # Note this can be inefficient.
        if ctx is None:
            ctx = pc.get_current_context()
        if ctx is None:
            raise RuntimeError("Did you forget to create a context?")
        em = ExpressionManager(ctx, resolve_parameters=resolve_parameters)
        return em.repr_scalar_by_basis(self, greedy_square=greedy_square)
