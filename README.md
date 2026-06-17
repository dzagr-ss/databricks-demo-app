# Databricks Dash + Genie POC

This project is a sample Databricks App called Revenue Risk Assistant. It uses Dash, Plotly, AG Grid, Databricks SQL, Unity Catalog views, and an AI/BI Genie Space.

The app follows the PDF runbook's security model: no PATs or hardcoded workspace values, a SQL warehouse and Genie Space injected as Databricks App resources, and Databricks unified authentication for local development.

## Files

- `app.py` - Thin Databricks App entrypoint that creates and runs the Dash app.
- `revenue_risk_assistant/backend/` - Databricks auth, SQL connector, Genie client, SQL guard, and dashboard queries.
- `revenue_risk_assistant/frontend/` - Dash layout, callbacks, reusable UI components, charts, grids, and preset questions.
- `app.yaml` - Databricks App runtime command and resource environment variables.
- `requirements.txt` - Python dependencies.
- `sql/setup_demo_data.sql` - Synthetic Unity Catalog tables and curated views using the PDF default `main.demo_dash_genie`.
- `sql/setup_demo_data_workspace.sql` - Same demo objects using `workspace.demo_dash_genie`, matching this workspace.
- `sql/setup_demo_data_hive_metastore.sql` - Same demo objects using `hive_metastore.demo_dash_genie` for workspaces without a `main` catalog.
- `.env.example` - Local development environment template.

## Required Databricks resources

- SQL warehouse app resource
  - Resource key: `sql-warehouse`
  - Permission: `CAN USE`
- Genie Space app resource
  - Resource key: `genie-space`
  - Permission: `CAN RUN`

## Required Unity Catalog objects

First choose a catalog that exists in your workspace:

```sql
SHOW CATALOGS;
```

The PDF uses `main.demo_dash_genie`, but this workspace has `workspace` instead of `main`. Use one of these options:

- Run [sql/setup_demo_data_workspace.sql](sql/setup_demo_data_workspace.sql) and set `DEMO_SCHEMA=workspace.demo_dash_genie`.
- Use another catalog from `SHOW CATALOGS`; replace `workspace.demo_dash_genie` in the SQL file and set `DEMO_SCHEMA=<your_catalog>.demo_dash_genie`.

The app defaults to `workspace.demo_dash_genie`. With that default, the setup SQL creates:

- `workspace.demo_dash_genie.customers`
- `workspace.demo_dash_genie.orders`
- `workspace.demo_dash_genie.support_tickets`
- `workspace.demo_dash_genie.orders_enriched`
- `workspace.demo_dash_genie.support_tickets_enriched`
- `workspace.demo_dash_genie.customer_health_360`

## Genie Space setup

Create a Genie Space named `Revenue Risk Genie` and add these curated views:

- `workspace.demo_dash_genie.orders_enriched`
- `workspace.demo_dash_genie.support_tickets_enriched`
- `workspace.demo_dash_genie.customer_health_360`

Suggested instructions:

```text
This Genie Space supports revenue risk and customer health analysis.

Business definitions:
- Booked revenue means SUM(revenue_amount) where order_status = 'Booked'.
- Gross margin amount means SUM(gross_margin_amount) where order_status = 'Booked'.
- Gross margin percentage means gross margin amount divided by booked revenue.
- Order exceptions mean orders where order_status is 'Cancelled' or 'Returned'.
- Open tickets mean support tickets where ticket_status is 'Open' or 'In Progress'.
- High-priority open tickets mean open tickets where priority = 'High'.
- Customer risk is already calculated in customer_health_360.risk_bucket.
- Customer health questions should usually use customer_health_360.
- Revenue trend questions should use orders_enriched and order_month.
- Support trend questions should use support_tickets_enriched and ticket_month.
- When ranking customers by business impact, rank by booked_revenue unless the user asks for margin, tickets, or CSAT.
- Always show the time period used when answering trend questions.
```

Test these questions in Genie before using the app:

- Which customers are high risk and have the most booked revenue?
- Show booked revenue and gross margin percentage by product family.
- Which countries have the most open high-priority support tickets?
- Show monthly booked revenue and order count.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
databricks auth login --host https://<your-workspace-url>
cp .env.example .env
python -m py_compile app.py
python app.py
```

Update `.env` with your local `GENIE_SPACE_ID`, `DATABRICKS_WAREHOUSE_ID`, and `DEMO_SCHEMA`.

For your specific error, make sure `.env` does not still contain `DEMO_SCHEMA=main.demo_dash_genie` unless `SHOW CATALOGS` includes `main`.

## Deploy as a Databricks App

1. Create a Databricks App, for example `dash-genie-revenue-risk`.
2. Add a SQL warehouse resource using key `sql-warehouse` with `CAN USE`.
3. Add a Genie Space resource using key `genie-space` with `CAN RUN`.
4. Copy the app service principal from the app Authorization tab.
5. Grant Unity Catalog access:

```sql
GRANT USE CATALOG ON CATALOG <your_catalog> TO `<app-service-principal>`;
GRANT USE SCHEMA ON SCHEMA <your_catalog>.demo_dash_genie TO `<app-service-principal>`;
GRANT SELECT ON TABLE <your_catalog>.demo_dash_genie.customers TO `<app-service-principal>`;
GRANT SELECT ON TABLE <your_catalog>.demo_dash_genie.orders TO `<app-service-principal>`;
GRANT SELECT ON TABLE <your_catalog>.demo_dash_genie.support_tickets TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.orders_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.support_tickets_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.customer_health_360 TO `<app-service-principal>`;
```

Sync and deploy:

```bash
databricks sync --watch . /Workspace/Users/<your-email>/databricks-dash-genie-poc
databricks apps deploy dash-genie-revenue-risk \
  --source-code-path /Workspace/Users/<your-email>/databricks-dash-genie-poc
```

## GitHub Actions deploy

The repository includes [deploy-databricks-app.yml](.github/workflows/deploy-databricks-app.yml). It validates Python imports, installs the Databricks CLI, syncs the app source into a Databricks Workspace folder, and deploys an existing Databricks App.

Configure these GitHub repository secrets:

- `DATABRICKS_HOST` - workspace URL, for example `https://dbc-...cloud.databricks.com`
- `DATABRICKS_CLIENT_ID` - Databricks service principal client ID
- `DATABRICKS_CLIENT_SECRET` - Databricks service principal OAuth secret

Optional GitHub repository variables:

- `DATABRICKS_APP_NAME` - defaults to `dash-genie-revenue-risk`
- `DATABRICKS_WORKSPACE_PATH` - defaults to `/Workspace/Shared/databricks-demo-app`

The Databricks App must already exist and have its `sql-warehouse` and `genie-space` resources configured. The service principal used by GitHub Actions needs permission to write to `DATABRICKS_WORKSPACE_PATH` and deploy the app.

## Troubleshooting

- `NO_SUCH_CATALOG_EXCEPTION`: run `SHOW CATALOGS`, pick an existing catalog, rerun the setup SQL in that catalog, and set `DEMO_SCHEMA=<catalog>.demo_dash_genie` in `.env` and `app.yaml`.
- Dashboard query fails: verify `DATABRICKS_WAREHOUSE_ID`, app resource keys, `DEMO_SCHEMA`, and table/view grants.
- Genie call fails: verify `GENIE_SPACE_ID`, `CAN RUN`, and access to the underlying views.
- Generated SQL does not run: the app only executes SQL that starts with `SELECT` or `WITH` and does not contain write or DDL keywords.
- Local auth fails: run `databricks auth login` and check `.env` values.
