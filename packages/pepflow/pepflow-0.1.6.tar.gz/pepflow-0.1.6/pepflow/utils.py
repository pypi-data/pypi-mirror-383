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

import enum
import math
import numbers
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import sympy as sp

from pepflow import constants as const

if TYPE_CHECKING:
    from pepflow.parameter import Parameter
    from pepflow.scalar import Scalar
    from pepflow.vector import Vector


NUMERICAL_TYPE = numbers.Number | sp.Rational


def SOP(v, w, sympy_mode: bool = False) -> np.ndarray:
    """Symmetric Outer Product."""
    coef = sp.S(1) / 2 if sympy_mode else 1 / 2
    return coef * (np.outer(v, w) + np.outer(w, v))


def SOP_self(v, sympy_mode: bool = False) -> np.ndarray:
    return SOP(v, v, sympy_mode=sympy_mode)


class Op(enum.Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"


class Comparator(enum.Enum):
    GE = "GE"
    LE = "LE"
    EQ = "EQ"

    def from_str(op: str) -> Comparator:
        if op not in ["le", "ge", "lt", "gt", "eq", "<=", ">=", "<", ">", "=="]:
            raise ValueError(
                f"op must be one of `le`, `ge`, `lt`, `gt`, `eq`, `<=`, `>=`, `<`, `>`, or `==` but got {op}"
            )
        if op in ["le", "lt", "<=", "<"]:
            cmp = Comparator.LE
        elif op in ["ge", "gt", ">=", ">"]:
            cmp = Comparator.GE
        elif op == "eq" or op == "==":
            cmp = Comparator.EQ
        return cmp


def is_numerical(val: Any) -> bool:
    return isinstance(val, numbers.Number) or isinstance(val, sp.Rational)


def is_numerical_or_parameter(val: Any) -> bool:
    from pepflow import parameter as param

    return is_numerical(val) or isinstance(val, param.Parameter)


def numerical_str(val: Any) -> str:
    from pepflow import parameter as param

    if not is_numerical_or_parameter(val):
        raise ValueError(
            "Cannot call numerical_str for {val} since it is not numerical."
        )
    if isinstance(val, param.Parameter):
        return str(val)
    return str(val) if isinstance(val, sp.Rational) else f"{val:.4g}"


def tag_and_coef_to_str(tag: str, val: NUMERICAL_TYPE | Parameter) -> str:
    """Returns a string representation with values and tag."""
    from pepflow import parameter as param

    if isinstance(val, param.Parameter):
        return f"{numerical_str(val)}*{tag}"

    coef = numerical_str(abs(val))
    sign = "+" if val >= 0 else "-"
    if math.isclose(abs(val), 1):
        return f"{sign} {tag} "
    elif math.isclose(val, 0, abs_tol=1e-5):
        return ""
    else:
        return f"{sign} {coef}*{tag} "


def parenthesize_tag(val: Vector | Scalar) -> str:
    tmp_tag = val.tag
    if not val.is_basis:
        if op := getattr(val.eval_expression, "op", None):
            if op in (Op.ADD, Op.SUB):
                tmp_tag = f"({val.tag})"
    return tmp_tag


def grad_tag(base_tag: str) -> str:
    """Make a gradient tag for the base_tag (the func value typically)."""
    return f"{const.GRADIENT}_{base_tag}"


def str_to_latex(s: str) -> str:
    """Convert string into latex style."""
    s = s.replace("star", r"\star")
    s = s.replace(f"{const.GRADIENT}_", r"\nabla ")
    s = s.replace("|", r"\|")
    return rf"$\displaystyle {s}$"


def get_matrix_of_dual_value(df: pd.DataFrame) -> np.ndarray:
    """The dataframe `df` has the columns "constraint_name",
    "col_point", "row_point", "constraint", and "dual_value".
    """
    # Check if we need to update the order.
    return (
        pd.pivot_table(
            df, values="dual_value", index="row", columns="col", dropna=False
        )
        .fillna(0.0)
        .to_numpy()
        .T
    )


def name_to_vector_tuple(c_name: str) -> list[str]:
    """Take a constraint name and return the tag of the two corresponding points."""
    _, vectors = c_name.split(":")
    return vectors.split(",")
