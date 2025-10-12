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
from dash import ALL, MATCH, Dash, Input, Output, State, dcc, html

from pepflow import utils
from pepflow.constants import PSD_CONSTRAINT

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.pep import PEPBuilder, PEPResult
    from pepflow.pep_context import PEPContext


plotly.io.renderers.default = "colab+vscode"
plotly.io.templates.default = "plotly_white"


@attrs.frozen
class PlotData:
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


def solve_primal_prob_and_get_fig(
    pep_builder: PEPBuilder, context: PEPContext
) -> tuple[list[PlotData], PEPResult]:
    plot_data_list: list[PlotData] = []

    result = pep_builder.solve_primal(context=context)

    for f in context.triplets.keys():
        fig, df = f.get_primal_fig_and_df_from_result(context, result, pep_builder)

        plot_data_list.append(PlotData(dataframe=df, fig=fig, func=f))

    return plot_data_list, result


def launch_primal_interactive(
    pep_builder: PEPBuilder, context: PEPContext, port: int = 8050
):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    plot_data_list, result = solve_primal_prob_and_get_fig(pep_builder, context)

    display_row = dbc.Row(
        [
            # Column 1: The scatter plots of dual variables and buttons to relax or restore constraints.
            dbc.Col(
                [
                    dbc.Button(
                        "Relax All Constraints",
                        id="relax-all-constraints-button",
                        style={"margin-bottom": "5px", "margin-right": "5px"},
                    ),
                    dbc.Button(
                        "Restore All Constraints",
                        id="restore-all-constraints-button",
                        style={"margin-bottom": "5px"},
                        color="success",
                    ),
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
                    dbc.Button(
                        "Solve PEP Problem",
                        id="solve-button",
                        color="primary",
                        className="me-1",
                        style={"margin-bottom": "5px"},
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
        ]
    )

    @dash.callback(
        Output("result-card", "children"),
        Output({"type": "dual-value-display", "index": ALL}, "children"),
        Output({"type": "interactive-scatter", "index": ALL}, "figure"),
        Output({"type": "dataframe-store", "index": ALL}, "data"),
        Input("solve-button", "n_clicks"),
    )
    def solve(_):
        plot_data_list, result = solve_primal_prob_and_get_fig(pep_builder, context)
        with np.printoptions(precision=3, linewidth=100, suppress=True):
            psd_dual_value = np.array(
                result.dual_var_manager.dual_value(PSD_CONSTRAINT)
            )
            result_card = dbc.CardBody(
                [
                    html.H3(f"Optimal Value: {result.primal_opt_value:.4g}"),
                    html.H3(f"Solver Status: {result.solver_status}"),
                    html.P("PSD Dual Variable:"),
                    html.Pre(str(psd_dual_value)),
                    html.P("Relaxed Constraints:"),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "flexDirection": "row",
                        },
                        children=[
                            html.Pre(
                                json.dumps(pep_builder.relaxed_constraints, indent=2),
                                id="relaxed-constraints",
                            ),
                            dcc.Clipboard(
                                id="relaxed-constraint-copy",
                                target_id="relaxed-constraints",
                                style={
                                    "fontSize": 20,
                                },
                            ),
                        ],
                    ),
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
        Output(
            {"type": "interactive-scatter", "index": ALL},
            "figure",
            allow_duplicate=True,
        ),
        Output({"type": "dataframe-store", "index": ALL}, "data", allow_duplicate=True),
        Input("restore-all-constraints-button", "n_clicks"),
        State({"type": "dataframe-store", "index": ALL}, "data"),
        prevent_initial_call=True,
    )
    def restore_all_constraints(_, list_previous_df_tuples):
        nonlocal pep_builder
        pep_builder.relaxed_constraints = []
        updated_figs = []
        df_data = []
        for previous_df_tuple in list_previous_df_tuples:
            tag, previous_df = previous_df_tuple
            df_updated = pd.DataFrame(previous_df)
            df_updated["constraint"] = "active"
            func = pep_builder.get_func_by_tag(tag)
            order = context.order_of_point(func)
            updated_figs.append(
                func.get_primal_fig_from_df_and_order(df_updated, order)
            )
            df_data.append((tag, df_updated.to_dict("records")))
        return updated_figs, df_data

    @dash.callback(
        Output(
            {"type": "interactive-scatter", "index": ALL},
            "figure",
            allow_duplicate=True,
        ),
        Output({"type": "dataframe-store", "index": ALL}, "data", allow_duplicate=True),
        Input("relax-all-constraints-button", "n_clicks"),
        State({"type": "dataframe-store", "index": ALL}, "data"),
        prevent_initial_call=True,
    )
    def relax_all_constraints(_, list_previous_df_tuples):
        nonlocal pep_builder
        pep_builder.relaxed_constraints = []
        updated_figs = []
        df_data = []
        for previous_df_tuple in list_previous_df_tuples:
            tag, previous_df = previous_df_tuple
            df_updated = pd.DataFrame(previous_df)
            pep_builder.relaxed_constraints.extend(
                df_updated["constraint_name"].to_list()
            )
            df_updated["constraint"] = "inactive"
            func = pep_builder.get_func_by_tag(tag)
            order = context.order_of_point(func)
            updated_figs.append(
                func.get_primal_fig_from_df_and_order(df_updated, order)
            )
            df_data.append((tag, df_updated.to_dict("records")))
        return updated_figs, df_data

    @dash.callback(
        Output(
            {"type": "interactive-scatter", "index": MATCH},
            "figure",
            allow_duplicate=True,
        ),
        Output(
            {"type": "dataframe-store", "index": MATCH}, "data", allow_duplicate=True
        ),
        Input({"type": "interactive-scatter", "index": MATCH}, "clickData"),
        State({"type": "dataframe-store", "index": MATCH}, "data"),
        prevent_initial_call=True,
    )
    def update_df_and_redraw(clickData, previous_df_tuple):
        nonlocal pep_builder
        if not clickData["points"][0]["customdata"]:
            return dash.no_update, dash.no_update

        clicked_name = clickData["points"][0]["customdata"][0]
        if clicked_name not in pep_builder.relaxed_constraints:
            pep_builder.relaxed_constraints.append(clicked_name)
        else:
            pep_builder.relaxed_constraints.remove(clicked_name)

        tag, previous_df = previous_df_tuple
        df_updated = pd.DataFrame(previous_df)
        df_updated["constraint"] = df_updated.constraint_name.map(
            lambda x: "inactive" if x in pep_builder.relaxed_constraints else "active"
        )
        func = pep_builder.get_func_by_tag(tag)
        order = context.order_of_point(func)
        return func.get_primal_fig_from_df_and_order(df_updated, order), (
            tag,
            df_updated.to_dict("records"),
        )

    app.run(debug=True, port=port)
