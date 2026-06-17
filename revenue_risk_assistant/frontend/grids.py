import dash_ag_grid as dag
import pandas as pd


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    safe_df = df.copy()
    for col in safe_df.columns:
        if pd.api.types.is_datetime64_any_dtype(safe_df[col]):
            safe_df[col] = safe_df[col].dt.strftime("%Y-%m-%d")
    return safe_df


def df_to_grid(df: pd.DataFrame, page_size: int = 10, height: int = 360) -> dag.AgGrid:
    if df is None or df.empty:
        return dag.AgGrid(
            rowData=[],
            columnDefs=[],
            className="ag-theme-quartz",
            style={"height": 120, "width": "100%"},
        )

    safe_df = format_dataframe(df).head(500)
    return dag.AgGrid(
        rowData=safe_df.to_dict("records"),
        columnDefs=[{"field": col, "filter": True, "sortable": True, "resizable": True} for col in safe_df.columns],
        defaultColDef={"filter": True, "sortable": True, "resizable": True},
        dashGridOptions={"pagination": True, "paginationPageSize": page_size},
        className="ag-theme-quartz",
        style={"height": height, "width": "100%"},
    )
