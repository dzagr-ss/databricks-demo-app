from dash import dcc, html

from revenue_risk_assistant.frontend.components import section_header, status_badge
from revenue_risk_assistant.frontend.questions import DEFAULT_QUESTION, PRESET_QUESTIONS
from revenue_risk_assistant.settings import DEMO_SCHEMA, GENIE_SPACE_ID, WAREHOUSE_ID


def build_layout() -> html.Div:
    return html.Div(
        [
            dcc.Store(id="conversation-id"),
            dcc.Store(id="chat-history", data=[]),
            html.Div(
                [
                    build_header(),
                    build_toolbar(),
                    html.Main(
                        [
                            html.Section(
                                [
                                    section_header(
                                        "Key metrics",
                                        "Snapshot for the selected order year.",
                                        badge_id="metrics-year-badge",
                                    ),
                                    html.Div(id="kpi-cards", className="metric-grid"),
                                ],
                                className="dashboard-section",
                                id="overview",
                            ),
                            html.Section(
                                [
                                    section_header(
                                        "Revenue trends",
                                        "Monthly performance and product mix for the selected year.",
                                    ),
                                    build_chart_section(),
                                ],
                                className="dashboard-section",
                            ),
                            html.Section(
                                [
                                    section_header(
                                        "Customer health risk",
                                        "Ranked by risk bucket and booked revenue. Sort and filter columns to drill in.",
                                    ),
                                    html.Div(id="risk-grid-container", className="grid-container"),
                                ],
                                className="dashboard-section surface",
                            ),
                            html.Section(
                                [
                                    section_header(
                                        "Ask Genie",
                                        "Natural-language follow-up over curated Unity Catalog views.",
                                    ),
                                    build_genie_section(),
                                ],
                                className="dashboard-section surface genie-panel",
                            ),
                        ],
                        className="app-main",
                    ),
                    build_footer(),
                ],
                className="app-frame",
            ),
        ],
        className="app-shell",
    )


def build_header() -> html.Header:
    return html.Header(
        [
            html.Div(
                [
                    html.P("Databricks Apps · Dash · Genie", className="eyebrow"),
                    html.H1("Revenue Risk Assistant"),
                    html.P(
                        "Monitor revenue, margin, and support health — then ask follow-up questions in plain language.",
                        className="lede",
                    ),
                ],
                className="title-block",
            ),
        ],
        className="app-header",
    )


def build_toolbar() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Order year", htmlFor="year-filter", className="toolbar-label"),
                    dcc.Dropdown(
                        id="year-filter",
                        clearable=False,
                        className="year-filter",
                        placeholder="Select year…",
                    ),
                ],
                className="toolbar-group",
            ),
            html.Div(
                [
                    html.Button(
                        [
                            html.Span(className="btn-icon refresh-icon"),
                            "Refresh data",
                        ],
                        id="refresh-button",
                        n_clicks=0,
                        className="secondary-button",
                    ),
                ],
                className="toolbar-actions",
            ),
        ],
        className="analytics-toolbar",
    )


def build_chart_section() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H3("Monthly booked revenue"),
                    html.P("Booked orders grouped by order month."),
                    dcc.Graph(id="monthly-revenue-chart", config={"displayModeBar": False}),
                ],
                className="chart-card",
            ),
            html.Div(
                [
                    html.H3("Revenue by product family"),
                    html.P("Hover for margin percentage."),
                    dcc.Graph(id="product-revenue-chart", config={"displayModeBar": False}),
                ],
                className="chart-card",
            ),
        ],
        className="chart-grid",
    )


def build_genie_section() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Suggested questions", htmlFor="preset-question", className="field-label"),
                    dcc.Dropdown(
                        id="preset-question",
                        options=PRESET_QUESTIONS,
                        value=DEFAULT_QUESTION,
                        clearable=False,
                        className="question-select",
                    ),
                ],
                className="genie-field",
            ),
            html.Div(
                [
                    html.Label("Your question", htmlFor="custom-question", className="field-label"),
                    dcc.Textarea(
                        id="custom-question",
                        placeholder="e.g. Which high-risk customers have the most open tickets?",
                        className="question-textarea",
                    ),
                ],
                className="genie-field",
            ),
            html.Button(
                [
                    html.Span(className="btn-icon spark-icon"),
                    "Ask Genie",
                ],
                id="ask-button",
                n_clicks=0,
                className="primary-button",
            ),
            html.Div(id="chat-window", className="chat-window"),
            build_genie_outputs(),
            html.Details(
                [
                    html.Summary("Developer: raw Genie response"),
                    html.Pre(id="raw-response", className="raw-response"),
                ],
                className="raw-details",
            ),
        ],
        className="genie-body",
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
                    html.Div(id="genie-result-grid", className="grid-container"),
                    dcc.Graph(id="genie-result-chart", config={"displayModeBar": False}),
                ],
                className="genie-column",
            ),
        ],
        className="genie-output-grid",
    )


def build_footer() -> html.Footer:
    return html.Footer(
        [
            html.Div(
                [
                    status_badge("Genie Space", bool(GENIE_SPACE_ID)),
                    status_badge("SQL Warehouse", bool(WAREHOUSE_ID)),
                ],
                className="resource-row",
            ),
            html.Code(DEMO_SCHEMA, className="schema-code"),
        ],
        className="app-footer",
    )
