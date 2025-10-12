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

import json
from typing import TYPE_CHECKING

import attrs
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, State, dcc, html

from pepflow import utils
from pepflow.constants import PSD_CONSTRAINT

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.pep import DualPEPResult, PEPBuilder
    from pepflow.pep_context import PEPContext


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


@attrs.frozen
class DualPlotData:
    dataframe: pd.DataFrame
    fig: go.Figure
    func: Function

    def dual_matrix_to_tab(self) -> html.Pre:
        with np.printoptions(precision=3, linewidth=100, suppress=True):
            dual_value_tab = html.Pre(
                str(utils.get_matrix_of_dual_value(self.dataframe)),
                id={"type": "dual-value-display", "index": self.func.tag},
                style={
                    "border": "1px solid lightgrey",
                    "padding": "10px",
                    "height": "60vh",
                    "overflowY": "auto",
                },
            )
        return dual_value_tab

    def plot_data_to_tab(self) -> dbc.Tab:
        tab = dbc.Tab(
            html.Div(
                [
                    html.P("Interactive Heat Map:"),
                    dcc.Graph(
                        id={
                            "type": "interactive-scatter",
                            "index": self.func.tag,
                        },
                        figure=self.fig,
                    ),
                    html.P("Dual Value Matrix:"),
                    self.dual_matrix_to_tab(),
                ]
            ),
            label=f"{self.func.tag}-Interpolation Conditions",
            tab_id=f"{self.func.tag}-interactive-scatter-tab",
        )
        return tab


def solve_dual_prob_and_get_fig(
    pep_builder: PEPBuilder, context: PEPContext
) -> tuple[list[DualPlotData], DualPEPResult]:
    plot_data_list: list[DualPlotData] = []

    result = pep_builder.solve_dual(context=context)

    for f in context.triplets.keys():
        fig, df = f.get_dual_fig_and_df_from_result(context, result, pep_builder)

        plot_data_list.append(DualPlotData(dataframe=df, fig=fig, func=f))

    return plot_data_list, result


def generate_dual_constraint_list_cardbody(data: list[str]) -> dbc.CardBody:
    def generate_dual_constraint_html_div(
        constraint_dict: dict[str, str | float],
    ) -> html.Div:
        constraint_name = constraint_dict["constraint_name"]
        op = constraint_dict["relation"]
        value = constraint_dict["value"]
        return html.Div(
            f"Constraint Name: {constraint_name}, Relation: {op}, Value: {value}",
            style={
                "border": "2px solid black",
                "padding": "2px",
                "margin": "2px",
                "text-align": "center",
                "width": "400px",
            },
        )

    def generate_remove_constraint_html_div(index: int) -> html.Div:
        return html.Div(
            dbc.Button(
                "Remove Constraint",
                id={
                    "type": "remove-specific-dual-constraint-button",
                    "index": index,
                },
                color="primary",
                className="me-1",
                style={"margin-bottom": "5px"},
            )
        )

    return dbc.CardBody(
        [
            html.Div(
                style={
                    "display": "flex",
                    "gap": "10px",
                    "flexDirection": "row",
                    "alignItems": "center",
                },
                children=[
                    generate_dual_constraint_html_div(json.loads(constraint_dict)),
                    generate_remove_constraint_html_div(index),
                ],
            )
            for index, constraint_dict in enumerate(data)
        ]
    )


def launch_dual_interactive(
    pep_builder: PEPBuilder, context: PEPContext, port: int = 9050
):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    plot_data_list, result = solve_dual_prob_and_get_fig(pep_builder, context)

    solve_dual_button = dbc.Button(
        "Solve Dual PEP Problem",
        id="solve-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    associated_constraint_div = html.Div(
        children="Associated Constraint",
        id="constraint-name-output-div",
        style={
            "border": "2px solid black",
            "padding": "2px",
            "margin": "2px",
            "text-align": "center",
            "width": "200px",
        },
    )
    relation_dropdown = html.Div(
        dcc.Dropdown(
            id="relation-dropdown",
            options=[
                {"label": "le", "value": "le"},
                {"label": "ge", "value": "ge"},
                {"label": "eq", "value": "eq"},
                {"label": "lt", "value": "lt"},
                {"label": "gt", "value": "gt"},
            ],
            value=None,
            placeholder="Relation",
            style={"width": "100px"},
        )
    )
    float_input = dcc.Input(
        id="float-input",
        type="number",
        placeholder="Enter a float",
        debounce=True,
        value=None,
        style={"width": "125px"},
    )
    add_constraint_button = dbc.Button(
        "Add Constraint",
        id="add-dual-constraint-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    remove_all_constraint_button = dbc.Button(
        "Remove All Constraints",
        id="remove-dual-constraint-button",
        color="primary",
        className="me-1",
        style={"margin-bottom": "5px"},
    )
    display_row = dbc.Row(
        [
            # Column 1: The scatter plots of dual variables.
            dbc.Col(
                [
                    dbc.Tabs(
                        [plot_data.plot_data_to_tab() for plot_data in plot_data_list],
                        active_tab=f"{plot_data_list[0].func.tag}-interactive-scatter-tab",
                    ),
                ],
                width=5,
            ),
            # Column 2: The data display and area to add constraints to dual variables.
            dbc.Col(
                [
                    solve_dual_button,
                    dbc.Row(html.H3("Add Constraint to Dual Variable:")),
                    dbc.Row(
                        html.Div(
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "flexDirection": "row",
                                "alignItems": "center",
                            },
                            children=[
                                associated_constraint_div,
                                relation_dropdown,
                                float_input,
                                add_constraint_button,
                                remove_all_constraint_button,
                            ],
                        )
                    ),
                    dbc.Row(html.H3("Constraints on Dual Variables:")),
                    dcc.Loading(
                        dbc.Card(
                            id="dual-constraint-card",
                            style={"overflow-x": "auto", "overflow-y": "auto"},
                        )
                    ),
                    dcc.Loading(
                        dbc.Card(
                            id="result-card",
                            style={"height": "60vh", "overflow-y": "auto"},
                        )
                    ),
                ],
                width=7,
            ),
        ],
    )

    # 3. Define the app layout.
    app.layout = html.Div(
        [
            html.H2("PEPFlow"),
            display_row,
            # For each function, store the corresponding DataFrame as a dictionary in dcc.Store.
            *[
                dcc.Store(
                    id={
                        "type": "dataframe-store",
                        "index": plot_data.func.tag,
                    },
                    data=(
                        plot_data.func.tag,
                        plot_data.dataframe.to_dict("records"),
                    ),
                )
                for plot_data in plot_data_list
            ],
            dcc.Store(id="list-of-constraints-on-dual", data=[]),
            dcc.Store(id="old-clickData", data=[]),
        ]
    )

    @dash.callback(
        Output("result-card", "children"),
        Output({"type": "dual-value-display", "index": ALL}, "children"),
        Output({"type": "interactive-scatter", "index": ALL}, "figure"),
        Output({"type": "dataframe-store", "index": ALL}, "data"),
        Input("solve-button", "n_clicks"),
    )
    def solve_dual(_):
        plot_data_list, result = solve_dual_prob_and_get_fig(pep_builder, context)
        with np.printoptions(precision=3, linewidth=100, suppress=True):
            psd_dual_value = np.array(
                result.dual_var_manager.dual_value(PSD_CONSTRAINT)
            )
            result_card = dbc.CardBody(
                [
                    html.H3(f"Optimal Value: {result.dual_opt_value:.4g}"),
                    html.H3(f"Solver Status: {result.solver_status}"),
                    html.P("PSD Dual Variable:"),
                    html.Pre(str(psd_dual_value)),
                ]
            )
            dual_value_displays = [
                str(utils.get_matrix_of_dual_value(plot_data.dataframe))
                for plot_data in plot_data_list
            ]
        figs = [plot_data.fig for plot_data in plot_data_list]

        df_data = [
            (plot_data.func.tag, plot_data.dataframe.to_dict("records"))
            for plot_data in plot_data_list
        ]

        return result_card, dual_value_displays, figs, df_data

    @dash.callback(
        Output("constraint-name-output-div", "children"),
        Output("old-clickData", "data"),
        Input({"type": "interactive-scatter", "index": ALL}, "clickData"),
        Input("constraint-name-output-div", "children"),
        State("old-clickData", "data"),
        prevent_initial_call=True,
    )
    def update_constraint_name_output_div(clickData, prev_constraint, prev_clickData):
        for index in clickData:
            if index is not None and index not in prev_clickData:
                return index["points"][0]["customdata"][0], clickData
        return dash.no_update, dash.no_update

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input("add-dual-constraint-button", "n_clicks"),
        State("constraint-name-output-div", "children"),
        State("relation-dropdown", "value"),
        State("float-input", "value"),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def add_constraints_dual_vars(n_clicks, constraint_name, op, val, data):
        if op is None:
            return dash.no_update
        if val is None:
            return dash.no_update
        if constraint_name == "Associated Constraint":
            return dash.no_update
        pep_builder.add_dual_val_constraint(constraint_name, op, float(val))
        data.append(
            json.dumps(
                {
                    "constraint_name": constraint_name,
                    "relation": op,
                    "value": float(val),
                }
            )
        )
        dual_constraint_card = generate_dual_constraint_list_cardbody(data)

        return dual_constraint_card, data

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input("remove-dual-constraint-button", "n_clicks"),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def remove_all_constraints_dual_vars(n_clicks, data):
        pep_builder.dual_val_constraint.clear()
        data = []
        dual_constraint_card = generate_dual_constraint_list_cardbody(data)

        return dual_constraint_card, data

    @dash.callback(
        Output("dual-constraint-card", "children", allow_duplicate=True),
        Output("list-of-constraints-on-dual", "data", allow_duplicate=True),
        Input(
            {"type": "remove-specific-dual-constraint-button", "index": ALL}, "n_clicks"
        ),
        State("list-of-constraints-on-dual", "data"),
        prevent_initial_call=True,
    )
    def remove_one_constraint_dual_vars(n_clicks_list, data):
        for index, n_clicks in enumerate(n_clicks_list):
            if n_clicks is not None:
                constraint_dict = json.loads(data[index])
                constraint_name = constraint_dict["constraint_name"]
                op = constraint_dict["relation"]
                value = constraint_dict["value"]
                pep_builder.dual_val_constraint[constraint_name].remove((op, value))
                data.remove(data[index])
                dual_constraint_card = generate_dual_constraint_list_cardbody(data)
                return dual_constraint_card, data

        return dash.no_update, dash.no_update

    app.run(debug=True, port=port)
