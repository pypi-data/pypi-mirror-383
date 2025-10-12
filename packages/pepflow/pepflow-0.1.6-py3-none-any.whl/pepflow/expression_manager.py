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

from pepflow import parameter as pm
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils
from pepflow import vector as vt


class ExpressionManager:
    """
    A class handling concrete representations of abstract :class:`Vector` and
    :class:`Scalar` objects managed by a particular :class:`PEPContext` object.

    Attributes:
        context (:class:`PEPContext`): The :class:`PEPContext` object which
            manages the abstract :class:`Vector` and :class:`Scalar` objects
            of interest.
        resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
            maps the name of parameters to the numerical values.
    """

    def __init__(
        self,
        pep_context: pc.PEPContext,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ):
        self.context = pep_context
        self._basis_vectors = []
        self._basis_vector_uid_to_index = {}
        self._basis_scalars = []
        self._basis_scalar_uid_to_index = {}
        self.resolve_parameters = resolve_parameters or {}
        for vector in self.context.vectors:
            if vector.is_basis:
                self._basis_vectors.append(vector)
                self._basis_vector_uid_to_index[vector.uid] = (
                    len(self._basis_vectors) - 1
                )
        for scalar in self.context.scalars:
            if scalar.is_basis:
                self._basis_scalars.append(scalar)
                self._basis_scalar_uid_to_index[scalar.uid] = (
                    len(self._basis_scalars) - 1
                )

        self._num_basis_vectors = len(self._basis_vectors)
        self._num_basis_scalars = len(self._basis_scalars)

    def get_index_of_basis_vector(self, vector: vt.Vector) -> int:
        return self._basis_vector_uid_to_index[vector.uid]

    def get_index_of_basis_scalar(self, scalar: sc.Scalar) -> int:
        return self._basis_scalar_uid_to_index[scalar.uid]

    def get_tag_of_basis_vector_index(self, index: int) -> str:
        return self._basis_vectors[index].tag

    def get_tag_of_basis_scalar_index(self, index: int) -> str:
        return self._basis_scalars[index].tag

    @functools.cache
    def eval_vector(self, vector: vt.Vector | pm.Parameter | float | int):
        """
        Return the concrete representation of the :class:`Vector`, `float`, or `int`.

        Concrete representations of :class:`Vector` objects are
        :class:`EvaluatedVector` objects. Concrete representations of `float` or `int`
        arguments are themselves.

        Args:
            vector (:class:`Vector`, float, int): The abstract :class:`Vector`,
                `float`, or `int` object whose concrete representation we want
                to find.

        Returns:
            :class:`EvaluatedVector` | float | int: The concrete representation of
            the `vector` argument.
        """
        if utils.is_numerical(vector):
            return vector
        if isinstance(vector, pm.Parameter):
            return vector.get_value(self.resolve_parameters)
        if not isinstance(vector, vt.Vector):
            raise ValueError(
                f"Encounter unknown type of vector to evaludated with: {type(vector)=}"
            )

        if vector.is_basis:
            index = self.get_index_of_basis_vector(vector)
            array = np.zeros(self._num_basis_vectors)
            array[index] = 1
            return vt.EvaluatedVector(coords=array)
        assert vector.eval_expression is not None  # To make typecheck happy

        if isinstance(vector.eval_expression, vt.ZeroVector):
            return vt.EvaluatedVector.zero(num_basis_vectors=self._num_basis_vectors)

        op = vector.eval_expression.op
        left_evaled_vector = self.eval_vector(vector.eval_expression.left_vector)
        right_evaled_vector = self.eval_vector(vector.eval_expression.right_vector)
        if op == utils.Op.ADD:
            return left_evaled_vector + right_evaled_vector
        if op == utils.Op.SUB:
            return left_evaled_vector - right_evaled_vector
        if op == utils.Op.MUL:
            return left_evaled_vector * right_evaled_vector
        if op == utils.Op.DIV:
            return left_evaled_vector / right_evaled_vector

        raise ValueError(f"Encountered unknown {op=} when evaluation the vector.")

    @functools.cache
    def eval_scalar(self, scalar: sc.Scalar | pm.Parameter | float | int):
        """
        Return the concrete representation of the :class:`Scalar`, `float`, or `int`.

        Concrete representations of :class:`Scalar` objects are
        :class:`EvaluatedScalar` objects. Concrete representations of `float` or `int`
        arguments are themselves.

        Args:
            scalar (:class:`Vector`, float, int): The abstract :class:`Scalar`,
                `float`, or `int` object whose concrete representation we want
                to find.

        Returns:
            :class:`EvaluatedScalar` | float | int: The concrete representation of
            the `scalar` argument.
        """
        if utils.is_numerical(scalar):
            return scalar
        if isinstance(scalar, pm.Parameter):
            return scalar.get_value(self.resolve_parameters)
        if not isinstance(scalar, sc.Scalar):
            raise ValueError(
                f"Encounter unknown type of scalar to evaludated with: {type(scalar)=}"
            )

        if scalar.is_basis:
            index = self.get_index_of_basis_scalar(scalar)
            array = np.zeros(self._num_basis_scalars)
            array[index] = 1
            matrix = np.zeros((self._num_basis_vectors, self._num_basis_vectors))
            return sc.EvaluatedScalar(
                func_coords=array,
                inner_prod_coords=matrix,
                offset=float(0.0),
            )
        assert scalar.eval_expression is not None  # To make typecheck happy

        if isinstance(scalar.eval_expression, sc.ZeroScalar):
            return sc.EvaluatedScalar.zero(
                num_basis_scalars=self._num_basis_scalars,
                num_basis_vectors=self._num_basis_vectors,
            )

        op = scalar.eval_expression.op
        # The special inner product usage.
        if (
            op == utils.Op.MUL
            and isinstance(scalar.eval_expression.left_scalar, vt.Vector)
            and isinstance(scalar.eval_expression.right_scalar, vt.Vector)
        ):
            array = np.zeros(self._num_basis_scalars)
            return sc.EvaluatedScalar(
                func_coords=array,
                inner_prod_coords=utils.SOP(
                    self.eval_vector(scalar.eval_expression.left_scalar).coords,
                    self.eval_vector(scalar.eval_expression.right_scalar).coords,
                ),
                offset=float(0.0),
            )

        left_evaled_scalar = self.eval_scalar(scalar.eval_expression.left_scalar)
        right_evaled_scalar = self.eval_scalar(scalar.eval_expression.right_scalar)
        if op == utils.Op.ADD:
            return left_evaled_scalar + right_evaled_scalar
        if op == utils.Op.SUB:
            return left_evaled_scalar - right_evaled_scalar
        if op == utils.Op.MUL:
            return left_evaled_scalar * right_evaled_scalar
        if op == utils.Op.DIV:
            return left_evaled_scalar / right_evaled_scalar

        raise ValueError(f"Encountered unknown {op=} when evaluation the scalar.")

    @functools.cache
    def repr_vector_by_basis(self, vector: vt.Vector) -> str:
        """
        Express the :class:`Vector` object as the linear combination of
        the basis :class:`Vector` objects of the associated :class:`PEPContext`.

        This linear combination is expressed as a `str` where, to refer to the
        basis :class:`Vector` objects, we use their tags.

        Args:
            vector (:class:`Vector`): The :class:`Vector` object which we want
                to express in terms of the basis :class:`Vector` objects.

        Returns:
            str: The representation of `vector` in terms of the basis
            :class:`Vector` objects of the :class:`PEPContext` associated
            with this :class:`ExpressionManager`.
        """
        assert isinstance(vector, vt.Vector)
        evaluated_vector = self.eval_vector(vector)
        return self.repr_evaluated_vector_by_basis(evaluated_vector)

    def repr_evaluated_vector_by_basis(
        self, evaluated_vector: vt.EvaluatedVector
    ) -> str:
        """
        Express the :class:`EvaluatedVector` object as the linear combination of
        the basis :class:`Vector` objects of the associated :class:`PEPContext`.

        This linear combination is expressed as a `str` where, to refer to the
        basis :class:`Vector` objects, we use their tags.

        Args:
            evaluated_vector (:class:`EvaluatedVector`): The
                :class:`EvaluatedVector` object which we want to express in
                terms of the basis :class:`Vector` objects.

        Returns:
            str: The representation of `evaluated_vector` in terms of
            the basis :class:`Vector` objects of the :class:`PEPContext`
            associated with this :class:`ExpressionManager`.
        """
        repr_str = ""
        for i, v in enumerate(evaluated_vector.coords):
            ith_tag = self.get_tag_of_basis_vector_index(i)
            repr_str += utils.tag_and_coef_to_str(ith_tag, v)

        # Post processing
        if repr_str == "":
            return "0"
        if repr_str.startswith("+ "):
            repr_str = repr_str[2:]
        if repr_str.startswith("- "):
            repr_str = "-" + repr_str[2:]
        return repr_str.strip()

    @functools.cache
    def repr_scalar_by_basis(
        self, scalar: sc.Scalar, greedy_square: bool = True
    ) -> str:
        """Express the :class:`Scalar` object using the basis :class:`Vector`
        and :class:`Scalar` objects of the associated :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str` where,
        to refer to the basis :class:`Vector` and :class:`Scalar` objects,
        we use their tags.

        Args:
            scalar (:class:`Scalar`): The :class:`Scalar` object which we want
                to express in terms of the basis :class:`Vector` and
                :class:`Scalar` objects.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.

        Returns:
            str: The representation of `scalar` in terms of the basis :class:`Vector`
            and :class:`Scalar` objects of the :class:`PEPContext` associated with this
            :class:`ExpressionManager`.
        """
        assert isinstance(scalar, sc.Scalar)
        evaluated_scalar = self.eval_scalar(scalar)
        return self.repr_evaluated_scalar_by_basis(
            evaluated_scalar, greedy_square=greedy_square
        )

    def repr_evaluated_scalar_by_basis(
        self, evaluated_scalar: sc.EvaluatedScalar, greedy_square: bool = True
    ) -> str:
        """Express the :class:`EvaluatedScalar` object using the basis :class:`Vector`
        and :class:`Scalar` objects of the associated :class:`PEPContext`.

        A :class:`Scalar` can be formed by linear combinations of basis
        :class:`Scalar` objects. A :class:`Scalar` can also be formed through
        the inner product of two basis :class:`Vector` objects. This function
        returns the representation of this :class:`Scalar` object in terms of
        the basis :class:`Vector` and :class:`Scalar` objects as a `str` where,
        to refer to the basis :class:`Vector` and :class:`Scalar` objects,
        we use their tags.

        Args:
            evaluated_scalar (:class:`EvaluatedScalar`): The
                :class:`EvaluatedScalar` object which we want to express in
                terms of the basis :class:`Vector` and :class:`Scalar` objects.
            greedy_square (bool): If `greedy_square` is true, the function will
                try to return :math:`\\|a-b\\|^2` whenever possible. If not,
                the function will return
                :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
                `True` by default.

        Returns:
            str: The representation of `evaluated_scalar` in terms of
            the basis :class:`Vector` and :class:`Scalar` objects of the
            :class:`PEPContext` associated with this :class:`ExpressionManager`.
        """
        repr_str = ""
        if not math.isclose(evaluated_scalar.offset, 0, abs_tol=1e-5):
            repr_str += utils.numerical_str(evaluated_scalar.offset)

        for i, v in enumerate(evaluated_scalar.func_coords):
            # Note the tag is from scalar basis.
            ith_tag = self.get_tag_of_basis_scalar_index(i)
            repr_str += utils.tag_and_coef_to_str(ith_tag, v)

        if greedy_square:
            diag_elem = np.diag(evaluated_scalar.inner_prod_coords).copy()
            for i in range(evaluated_scalar.inner_prod_coords.shape[0]):
                ith_tag = self.get_tag_of_basis_vector_index(i)
                # j starts from i+1 since we want to handle the diag elem at last.
                for j in range(i + 1, evaluated_scalar.inner_prod_coords.shape[0]):
                    jth_tag = self.get_tag_of_basis_vector_index(j)
                    v = float(evaluated_scalar.inner_prod_coords[i, j])
                    # We want to minimize the diagonal elements to zero greedily.
                    if diag_elem[i] * v > 0:  # same sign with diagonal elem
                        diag_elem[i] -= v
                        diag_elem[j] -= v
                        repr_str += utils.tag_and_coef_to_str(
                            f"|{ith_tag}+{jth_tag}|^2", v
                        )
                    else:  # different sign
                        diag_elem[i] += v
                        diag_elem[j] += v
                        repr_str += utils.tag_and_coef_to_str(
                            f"|{ith_tag}-{jth_tag}|^2", -v
                        )
                # Handle the diagonal elements
                repr_str += utils.tag_and_coef_to_str(f"|{ith_tag}|^2", diag_elem[i])
        else:
            for i in range(evaluated_scalar.inner_prod_coords.shape[0]):
                ith_tag = self.get_tag_of_basis_vector_index(i)
                for j in range(i, evaluated_scalar.inner_prod_coords.shape[0]):
                    jth_tag = self.get_tag_of_basis_vector_index(j)
                    v = float(evaluated_scalar.inner_prod_coords[i, j])
                    if i == j:
                        repr_str += utils.tag_and_coef_to_str(f"|{ith_tag}|^2", v)
                    else:
                        repr_str += utils.tag_and_coef_to_str(
                            f"<{ith_tag}, {jth_tag}>", 2 * v
                        )

        # Post processing
        if repr_str == "":
            return "0"
        if repr_str.startswith("+ "):
            repr_str = repr_str[2:]
        if repr_str.startswith("- "):
            repr_str = "-" + repr_str[2:]
        return repr_str.strip()


def represent_matrix_by_basis(
    matrix: np.ndarray, ctx: pc.PEPContext, greedy_square: bool = True
) -> str:
    """Express the `matrix` in terms of the basis :class:`Vector` objects
    of the :class:`PEPContext`.

    The concrete representation of the inner product of two abstract
    basis :class:`Vector` objects is a matrix (the outer product of the
    basis vectors corresponding to the concrete representations of the abstract
    basis :class:`Vector` objects). The matrix can then be expressed
    as a linear combination of the inner products of abstract basis
    :class:`Vector` objects. This is provided as a `str` where, to refer to
    the basis :class:`Vector` objects, we use their tags.

    Args:
        matrix (np.ndarray): The matrix which we want to express in terms of
            the basis :class:`Vector` objects of the :class:`PEPContext`.
        ctx (:class:`PEPContext`): The :class:`PEPContext` whose basis
            :class:`Vector` objects we consider.
        greedy_square (bool): If `greedy_square` is true, the function will
            try to return :math:`\\|a-b\\|^2` whenever possible. If not,
            the function will return
            :math:`\\|a\\|^2 - 2 * \\langle a, b \\rangle + \\|b\\|^2` instead.
            `True` by default.

    Returns:
        str: The representation of `matrix` in terms of the basis
        :class:`Vector` objects of `ctx`.
    """
    em = ExpressionManager(ctx)
    matrix_shape = (len(em._basis_vectors), len(em._basis_vectors))
    if matrix.shape != matrix_shape:
        raise ValueError(
            "The valid matrix for given context should have shape {matrix_shape}"
        )
    if not np.allclose(matrix, matrix.T):
        raise ValueError("Input matrix must be symmetric.")

    return em.repr_evaluated_scalar_by_basis(
        sc.EvaluatedScalar(
            func_coords=np.zeros(len(em._basis_scalars)),
            inner_prod_coords=matrix,
            offset=0.0,
        ),
        greedy_square=greedy_square,
    )
