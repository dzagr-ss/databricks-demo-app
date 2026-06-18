from dash import html

from revenue_risk_assistant.frontend.components import metric_card


def build_metric_cards(kpi, support, year: int) -> list[html.Div]:
    return [
        metric_card("Booked revenue", f"{float(kpi['booked_revenue'] or 0):,.0f}", "Booked orders", "revenue"),
        metric_card("Gross margin", f"{float(kpi['gross_margin'] or 0):,.0f}", "Booked orders", "margin"),
        metric_card("Active customers", f"{int(kpi['active_customers'] or 0):,}", f"Year {year}", "customers"),
        metric_card(
            "Order exception rate",
            f"{float(kpi['exception_rate_pct'] or 0):.1f}%",
            "Cancelled or returned",
            "risk",
        ),
        metric_card(
            "Open tickets",
            f"{int(support['open_tickets'] or 0):,}",
            f"Avg CSAT {float(support['avg_csat'] or 0):.2f}",
            "support",
        ),
    ]


def render_chat_history(chat_history: list[dict]) -> list[html.Div]:
    return [
        html.Div(
            [
                html.Div(item["role"], className="chat-role"),
                html.Div(item["content"], className="chat-message-text"),
            ],
            className=f"chat-message {item['role'].lower()}",
        )
        for item in chat_history[-8:]
    ]
