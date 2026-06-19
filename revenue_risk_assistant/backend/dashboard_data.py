from revenue_risk_assistant.backend.queries import (
    cancellation_by_segment_query,
    kpi_query,
    property_opportunity_query,
    property_type_value_query,
    years_query,
)
from revenue_risk_assistant.backend.sql_client import run_sql


def fetch_years() -> list[int]:
    df = run_sql(years_query())
    return [int(year) for year in df["order_year"].dropna().tolist()]


def fetch_dashboard_data(year: int) -> dict:
    return {
        "kpi": run_sql(kpi_query(year)).iloc[0],
        "property_type": run_sql(property_type_value_query(year)),
        "cancellation": run_sql(cancellation_by_segment_query(year)),
        "opportunities": run_sql(property_opportunity_query(year)),
    }
