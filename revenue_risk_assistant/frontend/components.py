from dash import html


def metric_card(title: str, value: str, subtitle: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(title, className="metric-title"),
            html.Div(value, className="metric-value"),
            html.Div(subtitle, className="metric-subtitle"),
        ],
        className="metric-card",
    )


def status_badge(label: str, configured: bool) -> html.Span:
    return html.Span(
        [
            html.Span(className="status-dot ok" if configured else "status-dot missing"),
            label,
        ],
        className="status-badge",
    )


def error_panel(title: str, detail: str) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="error-title"),
            html.Div(detail, className="error-detail"),
        ],
        className="error-panel",
    )


def empty_result(message: str) -> html.Div:
    return html.Div(message, className="empty-result")
