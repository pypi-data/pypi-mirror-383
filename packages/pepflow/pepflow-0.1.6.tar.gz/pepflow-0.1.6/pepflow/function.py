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

import numbers
import uuid
from typing import TYPE_CHECKING

import attrs
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pepflow import pep
from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import utils
from pepflow import vector as vt

if TYPE_CHECKING:
    from pepflow.constraint import Constraint


@attrs.frozen
class Triplet:
    """
    A data class that represents, for some given function :math:`f`,
    the tuple :math:`\\{x, f(x), \\nabla f(x)\\}`.

    Subgradients :math:`\\widetilde{\\nabla} f(x)` are represented by gradients as they
    are effectively treated the same in the context of PEP.

    Attributes:
        point (:class:`Vector`): A vector :math:`x`.
        func_val (:class:`Scalar`): The function value :math:`f(x)`.
        grad (:class:`Vector`): The gradient :math:`\\nabla f(x)` or
            a subgradient :math:`\\widetilde{\\nabla} f(x)`.
        name (str): The unique name of the :class:`Triplet` object.
    """

    point: vt.Vector
    func_val: sc.Scalar
    grad: vt.Vector
    name: str | None
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)


@attrs.frozen
class AddedFunc:
    """Represents left_func + right_func."""

    left_func: Function
    right_func: Function


@attrs.frozen
class ScaledFunc:
    """Represents scalar * base_func."""

    scale: float
    base_func: Function


@attrs.mutable
class Function:
    """A :class:`Function` object represents a function.

    :class:`Function` objects can be constructed as linear combinations
    of other :class:`Function` objects. Let `a` and `b` be some numeric
    data type. Let `f` and `g` be :class:`Function` objects. Then, we
    can form a new :class:`Function` object: `a*f+b*g`.

    A :class:`Function` object should never be explicitly constructed. Only
    children of :class:`Function` such as :class:`ConvexFunction` or
    :class:`SmoothConvexFunction` should be constructed. See their respective
    documentation to see how.

    Attributes:
        is_basis (bool): `True` if this function is not formed through a linear
            combination of other functions. `False` otherwise.
        tags (list[str]): A list that contains tags that can be used to
            identify the :class:`Function` object. Tags should be unique.
    """

    is_basis: bool

    composition: AddedFunc | ScaledFunc | None = None

    # Human tagged value for the function
    tags: list[str] = attrs.field(factory=list)

    # Generate an automatic id
    uid: uuid.UUID = attrs.field(factory=uuid.uuid4, init=False)

    def __attrs_post_init__(self):
        if self.is_basis:
            assert self.composition is None
        else:
            assert self.composition is not None

    @property
    def tag(self):
        """Returns the most recently added tag.

        Returns:
            str: The most recently added tag of this :class:`Function` object.
        """
        if len(self.tags) == 0:
            raise ValueError("Function should have a name.")
        return self.tags[-1]

    def add_tag(self, tag: str) -> None:
        """Add a new tag for this :class:`Function` object.

        Args:
            tag (str): The new tag to be added to the `tags` list.
        """
        self.tags.append(tag)

    def __repr__(self):
        if self.tags:
            return self.tag
        return super().__repr__()

    def _repr_latex_(self):
        s = repr(self)
        return rf"$\displaystyle {s}$"

    def get_interpolation_constraints(self, pep_context: pc.PEPContext | None = None):
        raise NotImplementedError(
            "This method should be implemented in the children class."
        )

    def add_triplet_to_func(self, triplet: Triplet) -> None:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        pep_context.triplets[self].append(triplet)

    def add_point_with_grad_restriction(
        self, point: vt.Vector, desired_grad: vt.Vector
    ) -> Triplet:
        # todo find a better tagging approach.
        if self.is_basis:
            func_val = sc.Scalar(is_basis=True)
            func_val.add_tag(f"{self.tag}({point.tag})")
            triplet = Triplet(
                point,
                func_val,
                desired_grad,
                name=f"{point.tag}_{func_val.tag}_{desired_grad.tag}",
            )
            self.add_triplet_to_func(triplet)
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                next_desired_grad = desired_grad - left_triplet.grad
                next_desired_grad.add_tag(
                    utils.grad_tag(f"{self.composition.right_func.tag}({point.tag})")
                )
                right_triplet = (
                    self.composition.right_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    left_triplet.func_val + right_triplet.func_val,
                    desired_grad,
                    name=f"{point.tag}_{self.tag}_{desired_grad.tag}",
                )
            elif isinstance(self.composition, ScaledFunc):
                next_desired_grad = desired_grad / self.composition.scale
                next_desired_grad.add_tag(
                    utils.grad_tag(f"{self.composition.base_func.tag}({point.tag})")
                )
                base_triplet = (
                    self.composition.base_func.add_point_with_grad_restriction(
                        point, next_desired_grad
                    )
                )
                triplet = Triplet(
                    point,
                    base_triplet.func_val * self.composition.scale,
                    desired_grad,
                    name=f"{point.tag}_{self.tag}_{desired_grad.tag}",
                )
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )
        return triplet

    def set_stationary_point(self, name: str) -> vt.Vector:
        """
        Return a stationary point for this :class:`Function` object.

        A :class:`Function` object can only have one stationary point.

        Args:
            name (str): The tag for the :class:`Vector` object which
                 will serve as the stationary point.

        Returns:
            :class:`Vector`: The stationary point for this :class:`Function`
            object.
        """
        # assert we can only add one stationary point?
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        if len(pep_context.stationary_triplets[self]) > 0:
            raise ValueError(
                "You are trying to add a stationary point to a function that already has a stationary point."
            )
        point = vt.Vector(is_basis=True)
        point.add_tag(name)
        desired_grad = vt.Vector.zero()  # zero point
        desired_grad.add_tag(utils.grad_tag(f"{self.tag}({name})"))
        triplet = self.add_point_with_grad_restriction(point, desired_grad)
        pep_context.add_stationary_triplet(self, triplet)
        return point

    def generate_triplet(self, point: vt.Vector) -> Triplet:
        pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")

        if not isinstance(point, vt.Vector):
            raise ValueError("The Function can only take point as input.")

        if self.is_basis:
            for triplet in pep_context.triplets[self]:
                if triplet.point.uid == point.uid:
                    return triplet

            func_val = sc.Scalar(is_basis=True)
            func_val.add_tag(f"{self.tag}({point.tag})")
            grad = vt.Vector(is_basis=True)
            grad.add_tag(utils.grad_tag(f"{self.tag}({point.tag})"))

            new_triplet = Triplet(
                point,
                func_val,
                grad,
                name=f"{point.tag}_{func_val.tag}_{grad.tag}",
            )
            self.add_triplet_to_func(new_triplet)
        else:
            if isinstance(self.composition, AddedFunc):
                left_triplet = self.composition.left_func.generate_triplet(point)
                right_triplet = self.composition.right_func.generate_triplet(point)
                func_val = left_triplet.func_val + right_triplet.func_val
                grad = left_triplet.grad + right_triplet.grad
            elif isinstance(self.composition, ScaledFunc):
                base_triplet = self.composition.base_func.generate_triplet(point)
                func_val = self.composition.scale * base_triplet.func_val
                grad = self.composition.scale * base_triplet.grad
            else:
                raise ValueError(
                    f"Unknown composition of functions: {self.composition}"
                )

        return Triplet(point, func_val, grad, name=None)

    def grad(self, point: vt.Vector) -> vt.Vector:
        """
        Returns a :class:`Vector` object that is the gradient of the
        :class:`Function` at the given :class:`Vector`.

        This function should be used to return subgradients as well as they gradients
        and subgradients are effectively treated the same in the context of PEP.

        Args:
            point (:class:`Vector`): Any :class:`Vector`.

        Returns:
            :class:`Vector`: The gradient of the :class:`Function` at the
            given :class:`Vector`.
        """
        triplet = self.generate_triplet(point)
        return triplet.grad

    def func_val(self, point: vt.Vector) -> sc.Scalar:
        """
        Returns a :class:`Scalar` object that is the function value of the
        :class:`Function` at the given :class:`Vector`.

        Args:
            point (:class:`Vector`): Any :class:`Vector`.

        Returns:
            :class:`Vector`: The function value of the :class:`Function` at the
            given :class:`Vector`.
        """
        triplet = self.generate_triplet(point)
        return triplet.func_val

    def get_dual_fig_and_df_from_result(
        self,
        ctx: pc.PEPContext,
        result: pep.PEPResult | pep.DualPEPResult,
        builder: pep.PEPBuilder,
    ) -> tuple[go.Figure, pd.DataFrame]:
        df, order = ctx.triplets_to_df_and_order_one_function(self)

        df["constraint"] = df.constraint_name.map(
            lambda x: "inactive" if x in builder.relaxed_constraints else "active"
        )
        df["dual_value"] = df.constraint_name.map(
            lambda x: result.dual_var_manager.dual_value(x)
        )

        fig = px.scatter(
            df,
            x="row",
            y="col",
            color="dual_value",
            symbol="constraint",
            symbol_map={"inactive": "x-open", "active": "circle"},
            custom_data="constraint_name",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_traces(marker=dict(size=15))
        fig.update_layout(
            coloraxis_colorbar=dict(yanchor="top", y=1, x=1.3, ticks="outside")
        )
        fig.update_xaxes(
            tickmode="array", tickvals=list(range(len(order))), ticktext=order
        )
        fig.update_yaxes(
            tickmode="array", tickvals=list(range(len(order))), ticktext=order
        )
        fig.update_layout(showlegend=False)
        return fig, df

    def get_primal_fig_and_df_from_result(
        self,
        ctx: pc.PEPContext,
        result: pep.PEPResult | pep.DualPEPResult,
        builder: pep.PEPBuilder,
    ) -> tuple[go.Figure, pd.DataFrame]:
        """The dataframe `df` has the columns "constraint_name",
        "col_point", "row_point", "constraint", and "dual_value".
        """

        fig, df = self.get_dual_fig_and_df_from_result(ctx, result, builder)
        fig.update_layout(showlegend=True)

        return fig, df

    def get_primal_fig_from_df_and_order(
        self,
        df: pd.DataFrame,
        order: list[str],
    ) -> go.Figure:
        """The dataframe `df` has the columns "constraint_name",
        "col_point", "row_point", "constraint", and "dual_value".
        Order is a list of the order of the points.
        """
        fig = px.scatter(
            df,
            x="row",
            y="col",
            color="dual_value",
            symbol="constraint",
            symbol_map={"inactive": "x-open", "active": "circle"},
            custom_data="constraint_name",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_traces(marker=dict(size=15))
        fig.update_layout(
            coloraxis_colorbar=dict(yanchor="top", y=1, x=1.3, ticks="outside")
        )
        fig.update_xaxes(
            tickmode="array", tickvals=list(range(len(order))), ticktext=order
        )
        fig.update_yaxes(
            tickmode="array", tickvals=list(range(len(order))), ticktext=order
        )
        return fig

    def __call__(self, point: vt.Vector) -> sc.Scalar:
        return self.func_val(point)

    def __add__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return Function(
            is_basis=False,
            composition=AddedFunc(self, other),
            tags=[f"{self.tag}+{other.tag}"],
        )

    def __sub__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        tag_other = other.tag
        if isinstance(other.composition, AddedFunc):
            tag_other = f"({other.tag})"
        return Function(
            is_basis=False,
            composition=AddedFunc(self, -other),
            tags=[f"{self.tag}-{tag_other}"],
        )

    def __mul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        tag_self = self.tag
        if isinstance(self.composition, AddedFunc):
            tag_self = f"({self.tag})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[f"{other:.4g}*{tag_self}"],
        )

    def __rmul__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        tag_self = self.tag
        if isinstance(self.composition, AddedFunc):
            tag_self = f"({self.tag})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=other, base_func=self),
            tags=[f"{other:.4g}*{tag_self}"],
        )

    def __neg__(self):
        tag_self = self.tag
        if isinstance(self.composition, AddedFunc):
            tag_self = f"({self.tag})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=-1, base_func=self),
            tags=[f"-{tag_self}"],
        )

    def __truediv__(self, other):
        if not utils.is_numerical(other):
            return NotImplemented
        tag_self = self.tag
        if isinstance(self.composition, AddedFunc):
            tag_self = f"({self.tag})"
        return Function(
            is_basis=False,
            composition=ScaledFunc(scale=1 / other, base_func=self),
            tags=[f"1/{other:.4g}*{tag_self}"],
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Function):
            return NotImplemented
        return self.uid == other.uid


class ConvexFunction(Function):
    """
    The :class:`ConvexFunction` class is a child of :class:`Function.`
    The :class:`ConvexFunction` class represents a closed, convex, and.

    proper (CCP) function, i.e., a convex function whose epigraph is a
    non-empty closed set.

    A CCP function typically has no parameters. We can instantiate a
    :class:`ConvexFunction` object as follows:

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("example").set_as_current()
        >>> pep_builder = pf.PEPBuilder()
        >>> g = pep_builder.declare_func(pf.ConvexFunction, "g")
    """

    def __init__(
        self,
        is_basis=True,
        composition=None,
    ):
        super().__init__(
            is_basis=is_basis,
            composition=composition,
        )

    def convex_interpolability_constraints(
        self, triplet_i: Triplet, triplet_j: Triplet
    ) -> Constraint:
        point_i = triplet_i.point
        func_val_i = triplet_i.func_val

        point_j = triplet_j.point
        func_val_j = triplet_j.func_val
        grad_j = triplet_j.grad

        func_diff = func_val_j - func_val_i
        cross_term = grad_j * (point_i - point_j)

        return (func_diff + cross_term).le(
            0, name=f"{self.tag}:{point_i.tag},{point_j.tag}"
        )

    def get_interpolation_constraints(
        self, pep_context: pc.PEPContext | None = None
    ) -> list[Constraint]:
        interpolation_constraints = []
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        for i in pep_context.triplets[self]:
            for j in pep_context.triplets[self]:
                if i == j:
                    continue
                interpolation_constraints.append(
                    self.convex_interpolability_constraints(i, j)
                )
        return interpolation_constraints

    def interpolate_ineq(
        self, p1_tag: str, p2_tag: str, pep_context: pc.PEPContext | None = None
    ) -> sc.Scalar:
        """Generate the interpolation inequality :class:`Scalar` by tags.

        The interpolation inequality between two points :math:`p_1, p_2` for a
        CCP function :math:`f` is

        .. math:: f(p_2) - f(p_1) + \\langle \\nabla f(p_2), p_1 - p_2 \\rangle.

        Args:
            p1_tag (str): A tag of the :class:`Vector` :math:`p_1`.
            p2_tag (str): A tag of the :class:`Vector` :math:`p_2`.
        """
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to specify a context?")
        # TODO: we definitely need a more robust tag system
        x1 = pep_context.get_by_tag(p1_tag)
        x2 = pep_context.get_by_tag(p2_tag)
        f1 = pep_context.get_by_tag(f"{self.tag}({p1_tag})")
        f2 = pep_context.get_by_tag(f"{self.tag}({p2_tag})")
        g2 = pep_context.get_by_tag(utils.grad_tag(f"{self.tag}({p2_tag})"))
        return f2 - f1 + g2 * (x1 - x2)

    def proximal_step(self, x_0: vt.Vector, stepsize: numbers.Number) -> vt.Vector:
        """Define the proximal operator as.

        .. math:: \\text{prox}_{\\gamma f}(x_0) := \\arg\\min_x \\left\\{ \\gamma f(x) + \\frac{1}{2} \\|x - x_0\\|^2 \\right\\}.

        This function performs a proximal step with respect to some
        :class:`Function` :math:`f` on the :class:`Vector` :math:`x_0`
        with stepsize :math:`\\gamma`:

        .. math::
            :nowrap:

            \\begin{eqnarray}
                x := \\text{prox}_{\\gamma f}(x_0) & := & \\arg\\min_x \\left\\{ \\gamma f(x) + \\frac{1}{2} \\|x - x_0\\|^2 \\right\\}, \\\\
                & \\Updownarrow & \\\\
                0 & = & \\gamma \\partial f(x) + x - x_0,\\\\
                & \\Updownarrow & \\\\
                x & = & x_0 - \\gamma \\widetilde{\\nabla} f(x) \\text{ where } \\widetilde{\\nabla} f(x)\\in\\partial f(x).
            \\end{eqnarray}

        Args:
            x_0 (:class:`Vector`): The initial point.
            stepsize (int | float): The stepsize.
        """
        grad = vt.Vector(is_basis=True)
        grad.add_tag(
            utils.grad_tag(f"{self.tag}(prox_{{{stepsize}*{self.tag}}}({x_0.tag}))")
        )
        func_val = sc.Scalar(is_basis=True)
        func_val.add_tag(f"{self.tag}(prox_{{{stepsize}*{self.tag}}}({x_0.tag}))")
        x = x_0 - stepsize * grad
        x.add_tag(f"prox_{{{stepsize}*{self.tag}}}({x_0.tag})")
        new_triplet = Triplet(
            x,
            func_val,
            grad,
            name=f"{x.tag}_{func_val.tag}_{grad.tag}",
        )
        self.add_triplet_to_func(new_triplet)
        return x


class SmoothConvexFunction(Function):
    """
    The :class:`SmoothConvexFunction` class is a child of :class:`Function.`
    The :class:`SmoothConvexFunction` class represents a smooth,.

    convex function.

    A smooth, convex function has a smoothness parameter :math:`L`.
    We can instantiate a :class:`SmoothConvexFunction` object as follows:

    Example:
        >>> import pepflow as pf
        >>> ctx = pf.PEPContext("example").set_as_current()
        >>> pep_builder = pf.PEPBuilder()
        >>> f = pep_builder.declare_func(pf.SmoothConvexFunction, "f", L=1)
    """

    def __init__(
        self,
        L,
        is_basis=True,
        composition=None,
    ):
        super().__init__(
            is_basis=is_basis,
            composition=composition,
        )
        self.L = L

    def smooth_convex_interpolability_constraints(self, triplet_i, triplet_j):
        point_i = triplet_i.point
        func_val_i = triplet_i.func_val
        grad_i = triplet_i.grad

        point_j = triplet_j.point
        func_val_j = triplet_j.func_val
        grad_j = triplet_j.grad

        func_diff = func_val_j - func_val_i
        cross_term = grad_j * (point_i - point_j)
        quad_term = 1 / (2 * self.L) * (grad_i - grad_j) ** 2

        return (func_diff + cross_term + quad_term).le(
            0, name=f"{self.tag}:{point_i.tag},{point_j.tag}"
        )

    def get_interpolation_constraints(self, pep_context: pc.PEPContext | None = None):
        interpolation_constraints = []
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to create a context?")
        for i in pep_context.triplets[self]:
            for j in pep_context.triplets[self]:
                if i == j:
                    continue
                interpolation_constraints.append(
                    self.smooth_convex_interpolability_constraints(i, j)
                )
        return interpolation_constraints

    def interpolate_ineq(
        self, p1_tag: str, p2_tag: str, pep_context: pc.PEPContext | None = None
    ) -> sc.Scalar:
        """Generate the interpolation inequality :class:`Scalar` by tags.

        The interpolation inequality between two points :math:`p_1, p_2` for a
        smooth, convex function :math:`f` is

        .. math:: f(p_2) - f(p_1) + \\langle \\nabla f(p_2), p_1 - p_2 \\rangle + \\tfrac{1}{2} \\lVert \\nabla f(p_1) - \\nabla f(p_2) \\rVert^2.

        Args:
            p1_tag (str): A tag of the :class:`Vector` :math:`p_1`.
            p2_tag (str): A tag of the :class:`Vector` :math:`p_2`.
        """
        if pep_context is None:
            pep_context = pc.get_current_context()
        if pep_context is None:
            raise RuntimeError("Did you forget to specify a context?")
        # TODO: we definitely need a more robust tag system
        x1 = pep_context.get_by_tag(p1_tag)
        x2 = pep_context.get_by_tag(p2_tag)
        f1 = pep_context.get_by_tag(f"{self.tag}({p1_tag})")
        f2 = pep_context.get_by_tag(f"{self.tag}({p2_tag})")
        g1 = pep_context.get_by_tag(utils.grad_tag(f"{self.tag}({p1_tag})"))
        g2 = pep_context.get_by_tag(utils.grad_tag(f"{self.tag}({p2_tag})"))
        return f2 - f1 + g2 * (x1 - x2) + 1 / 2 * (g1 - g2) ** 2
