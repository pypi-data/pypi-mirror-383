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

import contextlib
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterator

import attrs
import numpy as np

from pepflow import pep_context as pc
from pepflow import scalar as sc
from pepflow import solver as ps
from pepflow import utils
from pepflow import vector as vt
from pepflow.constants import PSD_CONSTRAINT

if TYPE_CHECKING:
    from pepflow.constraint import Constraint
    from pepflow.function import Function
    from pepflow.solver import DualPEPDualVarManager, PrimalPEPDualVarManager


@attrs.frozen
class PEPResult:
    """
    A data class object that contains the results of solving the Primal
    PEP.

    Attributes:
        primal_opt_value (float): The objective value of the solved Primal PEP.
        dual_var_manager (:class:`PrimalPEPDualVarManager`): A manager object
            which provides access to the dual variables associated with the
            constraints of the Primal PEP.
        solver_status (Any): States whether the solver managed to solve the
            Primal PEP successfully.
        context (:class:`PEPContext`): The :class:`PEPContext` object used to
            solve the Primal PEP.
    """

    primal_opt_value: float
    dual_var_manager: PrimalPEPDualVarManager
    solver_status: Any
    context: pc.PEPContext

    def get_func_dual_vars(self) -> dict[Function, np.ndarray]:
        """
        Return a dictionary which contains the associated dual variables of the
        interpolation constraints for Primal PEP.

        Returns:
            dict[:class:`Function`, np.ndarray]: A dictionary where the keys
            are :class:`Function` objects, and the values are the dual
            variables associated with the interpolation constraints of the
            :class:`Function` key.
        """
        df_dict, _ = self.context.triplets_to_df_and_order()
        df_dict_matrix = {}
        for f in df_dict.keys():
            df = df_dict[f]
            df["dual_value"] = df.constraint_name.map(
                lambda x: self.dual_var_manager.dual_value(x)
            )
            df_dict_matrix[f] = utils.get_matrix_of_dual_value(df)

        return df_dict_matrix

    def get_psd_dual_matrix(self) -> np.ndarray:
        """
        Return the PSD dual variable matrix associated with the constraint
        that the Primal PEP decision variable :math:`G` is PSD.

        Returns:
            np.ndarray: The PSD dual variable matrix associated with the
            constraint that the Primal PEP decision variable :math:`G` is PSD.
        """
        return np.array(self.dual_var_manager.dual_value(PSD_CONSTRAINT))


@attrs.frozen
class DualPEPResult:
    """
    A data class object that contains the results of solving the Dual
    PEP.

    Attributes:
        dual_opt_value (float): The objective value of the solved Dual PEP.
        dual_var_manager (:class:`DualPEPDualVarManager`): A manager object
            which provides access to the dual variables associated with the
            constraints of the Primal PEP after solving the Dual PEP.
        solver_status (Any): States whether the solver managed to solve the
            Dual PEP successfully.
        context (:class:`PEPContext`): The :class:`PEPContext` object used to
            solve the Dual PEP.
    """

    dual_opt_value: float
    dual_var_manager: DualPEPDualVarManager
    solver_status: Any
    context: pc.PEPContext


class PEPBuilder:
    """The main class for Primal and Dual PEP formulation.

    Attributes:
        init_conditions (list[:class:`Constraint`]): A list of all the initial
            conditions associated with this PEP.
        functions (list[:class:`Function`]): A list of all the functions
            associated with this PEP.
        performance_metric (:class:`Scalar`): The performance metric for this
            PEP.
        relaxed_constraints (list[str]): A list of names of the constraints
            that will be ignored when the Primal or Dual PEP is constructed.
        dual_val_constraint (dict[str, list[tuple[str, float]]]): A dictionary
            of the form `{constraint_name: [(op, val)]}`. The `constraint_name`
            is the name of the constraint the dual variable is associated with.
            The `op` is a string for the type of relation, i.e., `le`, `ge`,
            `eq`, `<=`, `>=`, or `==`. The `val` is the value for the
            other side of the constraint. For example, consider
            `{"f:x_1,x_0", [("eq", 0)]}`. Denote the associated dual variable
            as :math:`\\lambda_{1,0}`. Then, this means to add a constraint
            of the form :math:`\\lambda_{1,0} = 0` to the Dual PEP.
            Because it is hard to judge if the constraint associated
            with `constraint_name` is active, we suggest to not add dual
            variable constraints manually but instead use the interactive
            dashboard.
    """

    def __init__(self):
        self.pep_context_dict: dict[str, pc.PEPContext] = {}

        self.init_conditions: list[Constraint] = []
        self.functions: list[Function] = []
        self.performance_metric: sc.Scalar | None = None

        # Contain the name for the constraints that should be removed.
        # We should think about a better choice like manager.
        self.relaxed_constraints: list[str] = []

        # `dual_val_constraint` has the data structure: {constraint_name: [op, val]}.
        # Because it is hard to judge if the dual_val_constraint is applied or not,
        # we recommend to not use this object directly but through the interactive dashboard.
        self.dual_val_constraint: dict[str, list[tuple[str, float]]] = defaultdict(list)

    def clear_setup(self):
        """Resets the :class:`PEPBuilder` object."""
        self.init_conditions.clear()
        self.functions.clear()
        self.performance_metric = None
        self.relaxed_constraints.clear()
        self.dual_val_constraint.clear()

    @contextlib.contextmanager
    def make_context(
        self, name: str, override: bool = False
    ) -> Iterator[pc.PEPContext]:
        if not override and name in self.pep_context_dict:
            raise KeyError(f"There is already a context {name} in the builder")
        try:
            self.clear_setup()
            ctx = pc.PEPContext(name)
            self.pep_context_dict[name] = ctx
            pc.set_current_context(ctx)
            yield ctx
        finally:
            pc.set_current_context(None)

    def get_context(self, name: str) -> pc.PEPContext:
        if name not in self.pep_context_dict:
            raise KeyError(f"Cannot find a context named {name} in the builder.")
        ctx = self.pep_context_dict[name]
        pc.set_current_context(ctx)
        return ctx

    def clear_context(self, name: str) -> None:
        if name not in self.pep_context_dict:
            raise KeyError(f"Cannot find a context named {name} in the builder.")
        del self.pep_context_dict[name]

    def clear_all_context(self) -> None:
        self.pep_context_dict.clear()

    def add_init_point(self, tag: str) -> vt.Vector:
        point = vt.Vector(is_basis=True)
        point.add_tag(tag)
        return point

    def add_initial_constraint(self, constraint):
        """
        Add an initial condition.

        Args:
            constraint (:class:`Constraint`): A :class:`Constraint` object that
                represents the desired initial condition.
        """
        for init_constr in self.init_conditions:
            if init_constr.name == constraint.name:
                raise ValueError(
                    f"An initial constraint with the same name as {constraint.name} already exists."
                )
        self.init_conditions.append(constraint)

    def set_performance_metric(self, metric: sc.Scalar):
        """
        Set the performance metric.

        Args:
            metric (:class:`Scalar`): A :class:`Scalar` object that
                represents the desired performance metric.
        """
        self.performance_metric = metric

    def set_relaxed_constraints(self, relaxed_constraints: list[str]):
        """
        Set the constraints that will be ignored.

        Args:
            relaxed_constraints (list[str]): A list of names of constraints
                that will be ignored.
        """
        self.relaxed_constraints.extend(relaxed_constraints)

    def add_dual_val_constraint(
        self, constraint_name: str, op: str, val: float
    ) -> None:
        if op not in ["le", "ge", "lt", "gt", "eq", "<=", ">=", "<", ">", "=="]:
            raise ValueError(
                f"op must be one of `le`, `ge`, `lt`, `gt`, `eq`, `<=`, `>=`, `<`, `>`, or `==` but got {op}."
            )
        if not utils.is_numerical(val):
            raise ValueError("Value must be some numerical value.")

        self.dual_val_constraint[constraint_name].append((op, val))

    def declare_func(self, func_class: type[Function], tag: str, **kwargs):
        """
        Declare a function.

        Args:
            func_class (type[:class:`Function`]): The type of function we want to
                declare. Examples include :class:`ConvexFunction` or
                :class:`SmoothConvexFunction`.
            tag (str): A tag that will be added to the :class:`Function`'s
                `tags` list. It can be used to identify the :class:`Function`
                object.
            **kwargs: The other parameters needed to declare the function. For
                example, :class:`SmoothConvexFunction` will require a
                smoothness parameter `L`.
        """
        func = func_class(is_basis=True, composition=None, **kwargs)
        func.add_tag(tag)
        self.functions.append(func)
        return func

    def get_func_by_tag(self, tag: str):
        """
        Return the :class:`Function` object associated with the provided `tag`.

        Args:
            tag (str): The `tag` of the :class:`Function` object we want to
                retrieve.

        Returns:
            :class:`Function`: The :class:`Function` object associated with
            the `tag`.

        Note:
            Currently, only basis :class:`Function` objects can be retrieved.
            This will be updated eventually.
        """
        # TODO: Add support to return composite functions as well. Right now we can only return base functions
        for f in self.functions:
            if tag in f.tags:
                return f
        raise ValueError("Cannot find the function of given tag.")

    def solve(
        self,
        context: pc.PEPContext | None = None,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ):
        return self.solve_primal(context, resolve_parameters=resolve_parameters)

    def solve_primal(
        self,
        context: pc.PEPContext | None = None,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ):
        """
        Solve the Primal PEP associated with this :class:`PEPBuilder` object
        using the given :class:`PEPContext` object.

        Args:
            context (:class:`PEPContext`): The :class:`PEPContext` object used
                to solve the Primal PEP associated with this
                :class:`PEPBuilder` object. `None` if we consider the current
                global :class:`PEPContext` object.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
                maps the name of parameters to the numerical values.

        Returns:
            :class:`PEPResult`: A :class:`PEPResult` object that contains the
            information obtained after solving the Primal PEP associated with
            this :class:`PEPBuilder` object.
        """
        if context is None:
            context = pc.get_current_context()
        if context is None:
            raise RuntimeError("Did you forget to create a context?")

        all_constraints: list[Constraint] = [*self.init_conditions]
        for f in self.functions:
            all_constraints.extend(f.get_interpolation_constraints(context))

        # For now, we heavily rely on CVX. We can make a wrapper class to avoid
        # direct dependencies in the future.
        solver = ps.CVXPrimalSolver(
            perf_metric=self.performance_metric,
            constraints=[
                c for c in all_constraints if c.name not in self.relaxed_constraints
            ],
            context=context,
        )
        problem = solver.build_problem(resolve_parameters=resolve_parameters)
        result = problem.solve()
        return PEPResult(
            primal_opt_value=result,
            dual_var_manager=solver.dual_var_manager,
            solver_status=problem.status,
            context=context,
        )

    def solve_dual(
        self,
        context: pc.PEPContext | None = None,
        resolve_parameters: dict[str, utils.NUMERICAL_TYPE] | None = None,
    ):
        """
        Solve the Dual PEP associated with this :class:`PEPBuilder` object
        using the given :class:`PEPContext` object.

        Args:
            context (:class:`PEPContext`): The :class:`PEPContext` object used
                to solve the Dual PEP associated with this :class:`PEPBuilder`
                object. `None` if we consider the current global
                :class:`PEPContext` object.
            resolve_parameters (dict[str, :class:`NUMERICAL_TYPE`]): A dictionary that
                maps the name of parameters to the numerical values.

        Returns:
            :class:`DualPEPResult`: A :class:`DualPEPResult` object that
            contains the information obtained after solving the Dual PEP
            associated with this :class:`PEPBuilder` object.
        """
        if context is None:
            context = pc.get_current_context()
        if context is None:
            raise RuntimeError("Did you forget to create a context?")

        all_constraints: list[Constraint] = [*self.init_conditions]
        for f in self.functions:
            all_constraints.extend(f.get_interpolation_constraints(context))

        # TODO: Consider a better API and interface to adding constraint for dual
        # variable in dual problem. We can add `extra_dual_val_constraints` to add
        # more constraints on dual var in dual PEP.
        constraints = []
        for c in all_constraints:
            if c.name in self.relaxed_constraints:
                continue
            for op, val in self.dual_val_constraint[c.name]:
                if op in ["le", "lt", "<=", "<"]:
                    c.dual_le(val)
                elif op in ["ge", "gt", ">=", ">"]:
                    c.dual_ge(val)
                elif op == "eq" or op == "==":
                    c.dual_eq(val)
                else:
                    raise ValueError(f"Unknown op when construct the {c}")
            constraints.append(c)

        dual_solver = ps.CVXDualSolver(
            perf_metric=self.performance_metric,
            constraints=constraints,
            context=context,
        )
        problem = dual_solver.build_problem(resolve_parameters=resolve_parameters)
        result = problem.solve()

        return DualPEPResult(
            dual_opt_value=result,
            dual_var_manager=dual_solver.dual_var_manager,
            solver_status=problem.status,
            context=context,
        )
