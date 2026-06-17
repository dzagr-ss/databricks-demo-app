from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config


def get_config() -> Config:
    return Config()


def get_workspace_client() -> WorkspaceClient:
    return WorkspaceClient()


def server_hostname() -> str:
    host = get_config().host
    if not host:
        raise ValueError("Databricks host is not configured. Run `databricks auth login` or set DATABRICKS_HOST.")
    return host.replace("https://", "").replace("http://", "")
