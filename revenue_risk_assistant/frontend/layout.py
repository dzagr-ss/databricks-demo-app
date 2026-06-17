from dash import dcc, html

from revenue_risk_assistant.frontend.components import status_badge
from revenue_risk_assistant.frontend.questions import DEFAULT_QUESTION, PRESET_QUESTIONS
from revenue_risk_assistant.settings import DEMO_SCHEMA, GENIE_SPACE_ID, WAREHOUSE_ID


def build_layout() -> html.Div:
    return html.Div(
        [
            dcc.Store(id="conversation-id"),
            dcc.Store(id="chat-history", data=[]),
            build_header(),
            build_controls(),
            html.Section(id="kpi-cards", className="metric-grid"),
            build_chart_section(),
            build_risk_section(),
            build_genie_section(),
        ],
        className="app-shell",
    )


def build_header() -> html.Header:
    return html.Header(
        [
            html.Div(
                [
                    html.P("Databricks Apps + Dash + Genie", className="eyebrow"),
                    html.H1("Revenue Risk Assistant"),
                    html.P(
                        "Customer revenue, support health, and natural-language follow-up analysis in one governed app.",
                        className="lede",
                    ),
                ],
                className="title-block",
            ),
            html.Button("Refresh", id="refresh-button", n_clicks=0, className="secondary-button"),
        ],
        className="app-header",
    )


def build_controls() -> html.Section:
    return html.Section(
        [
            html.Div(
                [
                    html.Label("Order year", htmlFor="year-filter"),
                    dcc.Dropdown(id="year-filter", clearable=False, className="year-filter"),
                ],
                className="filter-group",
            ),
            html.Div(
                [
                    html.Div("Configured resources", className="panel-label"),
                    html.Div(
                        [
                            status_badge("Genie Space", bool(GENIE_SPACE_ID)),
                            status_badge("SQL Warehouse", bool(WAREHOUSE_ID)),
                        ],
                        className="resource-row",
                    ),
                    html.Code(f"Schema: {DEMO_SCHEMA}", className="schema-code"),
                ],
                className="resource-panel",
            ),
        ],
        className="control-strip",
    )


def build_chart_section() -> html.Section:
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Monthly booked revenue"),
                            html.P("Booked orders grouped by order month."),
                        ],
                        className="section-heading",
                    ),
                    dcc.Graph(id="monthly-revenue-chart", config={"displayModeBar": False}),
                ],
                className="surface",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Revenue by product family"),
                            html.P("Booked revenue with margin percentage in hover details."),
                        ],
                        className="section-heading",
                    ),
                    dcc.Graph(id="product-revenue-chart", config={"displayModeBar": False}),
                ],
                className="surface",
            ),
        ],
        className="chart-grid",
    )


def build_risk_section() -> html.Section:
    return html.Section(
        [
            html.Div(
                [
                    html.H2("Customer health risk"),
                    html.P("Ranked by calculated risk bucket and booked revenue."),
                ],
                className="section-heading",
            ),
            html.Div(id="risk-grid-container"),
        ],
        className="surface",
    )


def build_genie_section() -> html.Section:
    return html.Section(
        [
            html.Div(
                [
                    html.H2("Ask Genie"),
                    html.P("Ask follow-up questions over the curated Unity Catalog views."),
                ],
                className="section-heading",
            ),
            dcc.Dropdown(
                id="preset-question",
                options=PRESET_QUESTIONS,
                value=DEFAULT_QUESTION,
                clearable=False,
                className="question-select",
            ),
            dcc.Textarea(
                id="custom-question",
                placeholder="Or type your own question...",
                className="question-textarea",
            ),
            html.Button("Ask Genie", id="ask-button", n_clicks=0, className="primary-button"),
            html.Div(id="chat-window", className="chat-window"),
            build_genie_outputs(),
            html.Details(
                [
                    html.Summary("Raw Genie response"),
                    html.Pre(id="raw-response", className="raw-response"),
                ],
                className="raw-details",
            ),
        ],
        className="surface genie-panel",
    )


def build_genie_outputs() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H3("Generated SQL"),
                    html.Pre(id="sql-code", className="sql-block"),
                ],
                className="genie-column",
            ),
            html.Div(
                [
                    html.H3("Query result"),
                    html.Div(id="genie-result-grid"),
                    dcc.Graph(id="genie-result-chart", config={"displayModeBar": False}),
                ],
                className="genie-column",
            ),
        ],
        className="genie-output-grid",
    )
