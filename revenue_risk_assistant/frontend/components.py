from dash import html

METRIC_VARIANTS = ("revenue", "margin", "customers", "risk", "support")


def metric_card(title: str, value: str, subtitle: str = "", variant: str = "revenue") -> html.Div:
    safe_variant = variant if variant in METRIC_VARIANTS else "revenue"
    return html.Div(
        [
            html.Div(
                [
                    html.Span(className=f"metric-icon metric-icon-{safe_variant}"),
                    html.Span(title, className="metric-title"),
                ],
                className="metric-header",
            ),
            html.Div(value, className="metric-value"),
            html.Div(subtitle, className="metric-subtitle"),
        ],
        className=f"metric-card metric-card-{safe_variant}",
    )


def status_badge(label: str, configured: bool) -> html.Span:
    return html.Span(
        [
            html.Span(className="status-dot ok" if configured else "status-dot missing"),
            label,
        ],
        className="status-badge",
    )


def section_header(title: str, description: str = "", badge: str = "", badge_id=None) -> html.Div:
    badge_el = None
    if badge or badge_id:
        badge_el = html.Span(badge, id=badge_id, className="section-badge")
    children = [
        html.Div(
            [html.H2(title), badge_el],
            className="section-title-row",
        ),
    ]
    if description:
        children.append(html.P(description, className="section-description"))
    return html.Div(children, className="section-heading")


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
