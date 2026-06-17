import pandas as pd
from databricks import sql

from revenue_risk_assistant.backend.databricks_auth import get_config, server_hostname
from revenue_risk_assistant.settings import WAREHOUSE_ID


def warehouse_http_path() -> str:
    if not WAREHOUSE_ID:
        raise ValueError("DATABRICKS_WAREHOUSE_ID is not set. Add a SQL warehouse resource or set it in .env.")
    if WAREHOUSE_ID.startswith("/sql/"):
        return WAREHOUSE_ID
    return f"/sql/1.0/warehouses/{WAREHOUSE_ID}"


def run_sql(query: str) -> pd.DataFrame:
    cfg = get_config()
    connection = sql.connect(
        server_hostname=server_hostname(),
        http_path=warehouse_http_path(),
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()
    finally:
        connection.close()
