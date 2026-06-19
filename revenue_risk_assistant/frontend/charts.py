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


def property_type_value_figure(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="property_type",
        y="booked_revenue",
        template=PLOT_TEMPLATE,
        color="booked_revenue",
        color_continuous_scale=["#fee2e2", CHART_COLORS["primary"]],
    )
    fig.update_traces(
        customdata=df[["booking_count", "avg_booking_value", "avg_rating"]].to_numpy(),
        hovertemplate=(
            "<b>%{x}</b><br>Revenue: %{y:,.0f}<br>"
            "Bookings: %{customdata[0]:,}<br>"
            "Avg booking: %{customdata[1]:,.0f}<br>"
            "Avg rating: %{customdata[2]:.2f}<extra></extra>"
        )
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False,
        showlegend=False,
    )
    return _apply_chart_style(fig)


def monthly_revenue_bookings_figure(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["order_month"],
            y=df["booked_revenue"],
            name="Revenue",
            marker_color=CHART_COLORS["primary"],
            customdata=df[["booking_count"]].to_numpy(),
            hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<br>Bookings: %{customdata[0]:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["order_month"],
            y=df["booking_count"],
            name="Bookings",
            mode="lines+markers",
            marker=dict(size=7, color=CHART_COLORS["secondary"], line=dict(width=1.5, color="#ffffff")),
            line=dict(width=2.5, color=CHART_COLORS["secondary"]),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Bookings: %{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            title=None,
            tickfont=dict(color=CHART_COLORS["text"]),
            zeroline=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        showlegend=True,
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
