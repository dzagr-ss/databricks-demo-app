import pandas as pd
import plotly.express as px

from revenue_risk_assistant.settings import PLOT_TEMPLATE


def monthly_revenue_figure(df: pd.DataFrame):
    fig = px.line(df, x="order_month", y="booked_revenue", markers=True, template=PLOT_TEMPLATE)
    fig.update_layout(margin={"l": 12, "r": 12, "t": 12, "b": 12}, xaxis_title=None, yaxis_title=None)
    return fig


def product_revenue_figure(df: pd.DataFrame):
    fig = px.bar(
        df,
        x="product_family",
        y="booked_revenue",
        hover_data=["margin_pct"],
        template=PLOT_TEMPLATE,
    )
    fig.update_layout(margin={"l": 12, "r": 12, "t": 12, "b": 12}, xaxis_title=None, yaxis_title=None)
    return fig


def auto_figure(df: pd.DataFrame):
    if df is None or df.empty:
        return {}
    numeric_cols = list(df.select_dtypes(include="number").columns)
    if not numeric_cols:
        return {}

    date_cols = [col for col in df.columns if any(term in col.lower() for term in ["date", "month", "year"])]
    category_cols = [col for col in df.columns if col not in numeric_cols]
    if date_cols:
        fig = px.line(df, x=date_cols[0], y=numeric_cols[0], markers=True, template=PLOT_TEMPLATE)
    elif category_cols:
        fig = px.bar(df.head(20), x=category_cols[0], y=numeric_cols[0], template=PLOT_TEMPLATE)
    else:
        return {}
    fig.update_layout(margin={"l": 12, "r": 12, "t": 22, "b": 12})
    return fig
