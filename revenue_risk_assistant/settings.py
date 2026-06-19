import os

from dotenv import load_dotenv

load_dotenv()

GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
DEMO_SCHEMA = os.getenv("DEMO_SCHEMA", "workspace.demo_dash_genie")

ORDERS_VIEW = f"{DEMO_SCHEMA}.orders_enriched"
TICKETS_VIEW = f"{DEMO_SCHEMA}.support_tickets_enriched"
HEALTH_VIEW = f"{DEMO_SCHEMA}.customer_health_360"
PROPERTY_VALUE_VIEW = f"{DEMO_SCHEMA}.property_value_360"

PLOT_TEMPLATE = "plotly_white"


def runtime_port() -> int:
    return int(os.getenv("DATABRICKS_APP_PORT", os.getenv("PORT", "8050")))
