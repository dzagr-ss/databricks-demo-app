from typing import Optional

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
                                        "Marketplace value snapshot for the selected booking year.",
                                        badge_id="metrics-year-badge",
                                    ),
                                    loading_region(
                                        html.Div(
                                            [
                                                html.Div(id="kpi-cards", className="metric-grid loading-content"),
                                                build_metric_placeholders(),
                                            ],
                                            className="loading-stack",
                                        ),
                                        "Loading metrics",
                                        target_components={"kpi-cards": "children"},
                                    ),
                                ],
                                className="dashboard-section",
                                id="overview",
                            ),
                            html.Section(
                                [
                                    section_header(
                                        "Value and cancellation mix",
                                        "Property type revenue and cancellation rate by guest segment.",
                                    ),
                                    loading_region(
                                        html.Div(
                                            [
                                                build_chart_section(),
                                                build_chart_placeholders(),
                                            ],
                                            className="loading-stack",
                                        ),
                                        "Loading charts",
                                        target_components={
                                            "monthly-revenue-chart": "figure",
                                            "product-revenue-chart": "figure",
                                        },
                                    ),
                                ],
                                className="dashboard-section",
                            ),
                            html.Section(
                                [
                                    section_header(
                                        "Property value opportunities",
                                        "Properties ranked by revenue, review quality, and cancellation pressure.",
                                    ),
                                    loading_region(
                                        html.Div(
                                            [
                                                html.Div(id="risk-grid-container", className="grid-container loading-content"),
                                                build_table_placeholder(),
                                            ],
                                            className="loading-stack",
                                        ),
                                        "Loading property opportunities",
                                        target_components={"risk-grid-container": "children"},
                                    ),
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


def loading_region(children, message: str, target_components: Optional[dict] = None) -> dcc.Loading:
    return dcc.Loading(
        children=children,
        className="loading-region",
        custom_spinner=html.Div(
            [
                html.Span(className="loading-dot"),
                html.Span(message, className="loading-text"),
            ],
            className="loading-indicator",
        ),
        delay_hide=200,
        delay_show=250,
        overlay_style={"visibility": "visible"},
        parent_className="loading-parent",
        show_initially=True,
        target_components=target_components,
    )


def build_header() -> html.Header:
    return html.Header(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("RA", className="brand-mark"),
                            html.Div(
                                [
                                    html.P("Databricks Apps", className="brand-label"),
                                    html.P("Dash + Genie workspace", className="brand-subtitle"),
                                ],
                                className="brand-copy",
                            ),
                        ],
                        className="brand-lockup",
                    ),
                    html.Div(
                        [
                            status_badge("Genie Space", bool(GENIE_SPACE_ID)),
                            status_badge("SQL Warehouse", bool(WAREHOUSE_ID)),
                        ],
                        className="header-status",
                    ),
                ],
                className="header-top",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Travel marketplace analytics", className="eyebrow"),
                            html.H1("Wanderbricks Revenue Assistant"),
                            html.P(
                                "Monitor bookings, property value, cancellations, and review quality, then ask follow-up questions in plain language.",
                                className="lede",
                            ),
                        ],
                        className="title-block",
                    ),
                    html.Div(
                        [
                            html.Span("Demo schema", className="meta-label"),
                            html.Code(DEMO_SCHEMA, className="meta-code"),
                        ],
                        className="header-meta",
                    ),
                ],
                className="header-content",
            ),
        ],
        className="app-header",
    )


def build_toolbar() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Filters", className="toolbar-title"),
                    html.Div(
                        [
                            html.Label("Order year", htmlFor="year-filter", className="toolbar-label"),
                            loading_region(
                                dcc.Dropdown(
                                    id="year-filter",
                                    clearable=False,
                                    className="year-filter",
                                    placeholder="Select year...",
                                ),
                                "Loading years",
                                target_components={"year-filter": ["options", "value"]},
                            ),
                        ],
                        className="toolbar-field",
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
                    html.H3("Revenue by property type"),
                    html.P("Booked revenue, booking count, and review quality."),
                    dcc.Graph(id="monthly-revenue-chart", config={"displayModeBar": False}),
                ],
                className="chart-card",
            ),
            html.Div(
                [
                    html.H3("Cancellation rate by segment"),
                    html.P("Guest segment cancellation rate and revenue context."),
                    dcc.Graph(id="product-revenue-chart", config={"displayModeBar": False}),
                ],
                className="chart-card",
            ),
        ],
        className="chart-grid loading-content",
    )


def build_metric_placeholders() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Div(className="skeleton-line skeleton-line-short"),
                    html.Div(className="skeleton-line skeleton-line-value"),
                    html.Div(className="skeleton-line skeleton-line-small"),
                ],
                className="metric-card skeleton-card",
            )
            for _ in range(5)
        ],
        className="metric-grid loading-placeholder",
    )


def build_chart_placeholders() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Div(className="skeleton-line skeleton-line-title"),
                    html.Div(className="chart-skeleton-bars"),
                ],
                className="chart-card skeleton-card",
            ),
            html.Div(
                [
                    html.Div(className="skeleton-line skeleton-line-title"),
                    html.Div(className="chart-skeleton-bars"),
                ],
                className="chart-card skeleton-card",
            ),
        ],
        className="chart-grid loading-placeholder",
    )


def build_table_placeholder() -> html.Div:
    return html.Div(
        [
            html.Div(className="table-skeleton-header"),
            *[html.Div(className="table-skeleton-row") for _ in range(8)],
        ],
        className="table-skeleton loading-placeholder",
    )


def build_genie_section() -> html.Div:
    return html.Div(
        [
            html.Div(
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
                                placeholder="e.g. Where do high-value bookings have weak reviews?",
                                value=DEFAULT_QUESTION,
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
                ],
                className="genie-controls",
            ),
            loading_region(
                html.Div(id="chat-window", className="chat-window"),
                "Waiting for Genie",
                target_components={"chat-window": "children"},
            ),
            loading_region(
                html.Div(
                    [
                        build_genie_outputs(),
                        html.Details(
                            [
                                html.Summary("Developer: raw Genie response"),
                                html.Pre(id="raw-response", className="raw-response"),
                            ],
                            className="raw-details",
                        ),
                    ],
                    id="genie-results-panel",
                    className="genie-results-panel is-hidden",
                ),
                "Running generated query",
                target_components={
                    "genie-results-panel": "className",
                    "sql-code": "children",
                    "genie-result-grid": "children",
                    "genie-result-chart": "figure",
                    "raw-response": "children",
                },
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
