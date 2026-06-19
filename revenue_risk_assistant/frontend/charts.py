import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from revenue_risk_assistant.settings import PLOT_TEMPLATE

CHART_COLORS = {
    "primary": "#ef4444",
    "primary_light": "#fecaca",
    "secondary": "#0891b2",
    "grid": "#e5e7eb",
    "text": "#6b7280",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, ui-sans-serif, system-ui, sans-serif", color="#374151", size=12),
    hoverlabel=dict(bgcolor="#111827", font_color="#f9fafb", font_size=12),
    margin=dict(l=8, r=8, t=10, b=8),
)


def _apply_chart_style(fig: go.Figure) -> go.Figure:
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(
        showgrid=False,
        linecolor=CHART_COLORS["grid"],
        tickfont=dict(color=CHART_COLORS["text"]),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=CHART_COLORS["grid"],
        gridwidth=1,
        zeroline=False,
        linecolor=CHART_COLORS["grid"],
        tickfont=dict(color=CHART_COLORS["text"]),
    )
    return fig


def monthly_revenue_figure(df: pd.DataFrame):
    fig = px.line(
        df,
        x="order_month",
        y="booked_revenue",
        markers=True,
        template=PLOT_TEMPLATE,
        color_discrete_sequence=[CHART_COLORS["primary"]],
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=7, line=dict(width=1.5, color="#ffffff")),
        hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return _apply_chart_style(fig)


def product_revenue_figure(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="product_family",
        y="booked_revenue",
        hover_data={"margin_pct": ":.1f", "booked_revenue": ":,.0f"},
        template=PLOT_TEMPLATE,
        color="booked_revenue",
        color_continuous_scale=["#fee2e2", CHART_COLORS["primary"]],
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<br>Margin: %{customdata[0]:.1f}%<extra></extra>")
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False,
        showlegend=False,
    )
    return _apply_chart_style(fig)


def auto_figure(df: pd.DataFrame):
    if df is None or df.empty:
        return {}
    numeric_cols = list(df.select_dtypes(include="number").columns)
    if not numeric_cols:
        return {}

    date_cols = [col for col in df.columns if any(term in col.lower() for term in ["date", "month", "year"])]
    category_cols = [col for col in df.columns if col not in numeric_cols]
    if date_cols:
        fig = px.line(
            df,
            x=date_cols[0],
            y=numeric_cols[0],
            markers=True,
            template=PLOT_TEMPLATE,
            color_discrete_sequence=[CHART_COLORS["secondary"]],
        )
    elif category_cols:
        fig = px.bar(
            df.head(20),
            x=category_cols[0],
            y=numeric_cols[0],
            template=PLOT_TEMPLATE,
            color_discrete_sequence=[CHART_COLORS["primary"]],
        )
    else:
        return {}
    fig.update_layout(margin=dict(l=8, r=8, t=16, b=8))
    return _apply_chart_style(fig)
