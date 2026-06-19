from dash import dcc, html

from revenue_risk_assistant.frontend.components import metric_card


def build_metric_cards(kpi, year: int) -> list[html.Div]:
    return [
        metric_card("Booked revenue", f"{float(kpi['booked_revenue'] or 0):,.0f}", "Confirmed stays", "revenue"),
        metric_card("Booked nights", f"{int(kpi['booked_nights'] or 0):,}", f"Year {year}", "margin"),
        metric_card("Bookings", f"{int(kpi['booking_count'] or 0):,}", "Confirmed", "customers"),
        metric_card(
            "Cancellation rate",
            f"{float(kpi['cancellation_rate_pct'] or 0):.1f}%",
            "Cancelled bookings",
            "risk",
        ),
        metric_card(
            "Weak-review value",
            f"{float(kpi['weak_review_booked_revenue'] or 0):,.0f}",
            f"{int(kpi['weak_review_properties'] or 0):,} properties · Avg rating {float(kpi['avg_rating'] or 0):.2f}",
            "support",
        ),
    ]


def render_chat_history(chat_history: list[dict]) -> list[html.Div]:
    return [
        html.Div(
            [
                html.Div(item["role"], className="chat-role"),
                render_chat_content(item),
            ],
            className=f"chat-message {item['role'].lower()}",
        )
        for item in chat_history[-8:]
    ]


def render_chat_content(item: dict):
    if item["role"].lower() == "genie":
        return dcc.Markdown(item["content"], className="chat-message-text markdown-body")
    return html.Div(item["content"], className="chat-message-text")
