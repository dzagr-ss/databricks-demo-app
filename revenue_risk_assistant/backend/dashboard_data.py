from revenue_risk_assistant.backend.queries import (
    kpi_query,
    monthly_revenue_bookings_query,
    property_opportunity_query,
    property_type_value_query,
)
from revenue_risk_assistant.backend.sql_client import run_sql


def fetch_dashboard_data(year: int) -> dict:
    return {
        "kpi": run_sql(kpi_query(year)).iloc[0],
        "property_type": run_sql(property_type_value_query(year)),
        "monthly": run_sql(monthly_revenue_bookings_query(year)),
        "opportunities": run_sql(property_opportunity_query(year)),
    }
