from revenue_risk_assistant.backend.queries import (
    customer_risk_query,
    kpi_query,
    monthly_revenue_query,
    product_revenue_query,
    support_summary_query,
    years_query,
)
from revenue_risk_assistant.backend.sql_client import run_sql


def fetch_years() -> list[int]:
    df = run_sql(years_query())
    return [int(year) for year in df["order_year"].dropna().tolist()]


def fetch_dashboard_data(year: int) -> dict:
    return {
        "kpi": run_sql(kpi_query(year)).iloc[0],
        "support": run_sql(support_summary_query(year)).iloc[0],
        "monthly": run_sql(monthly_revenue_query(year)),
        "product": run_sql(product_revenue_query(year)),
        "risk": run_sql(customer_risk_query()),
    }
