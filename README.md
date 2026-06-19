# Databricks Dash + Genie POC

This project is a sample Databricks App called Wanderbricks Revenue Assistant. It uses Dash, Plotly, AG Grid, Databricks SQL, Unity Catalog views, and an AI/BI Genie Space.

The app follows the PDF runbook's security model: no PATs or hardcoded workspace values, a SQL warehouse and Genie Space injected as Databricks App resources, and Databricks unified authentication for local development.

## Files

- `app.py` - Thin Databricks App entrypoint that creates and runs the Dash app.
- `revenue_risk_assistant/backend/` - Databricks auth, SQL connector, Genie client, SQL guard, and dashboard queries.
- `revenue_risk_assistant/frontend/` - Dash layout, callbacks, reusable UI components, charts, grids, and preset questions.
- `app.yaml` - Databricks App runtime command and resource environment variables.
- `requirements.txt` - Python dependencies.
- `sql/setup_wanderbricks_workspace.sql` - Curated Wanderbricks semantic views using `samples.wanderbricks` as the source and `workspace.demo_dash_genie` as the app schema.
- `sql/setup_demo_data.sql` - Synthetic Unity Catalog tables and curated views using the PDF default `main.demo_dash_genie`.
- `sql/setup_demo_data_workspace.sql` - Synthetic demo objects using `workspace.demo_dash_genie`.
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

- Run [sql/setup_wanderbricks_workspace.sql](sql/setup_wanderbricks_workspace.sql) and set `DEMO_SCHEMA=workspace.demo_dash_genie`.
- Use another catalog from `SHOW CATALOGS`; replace `workspace.demo_dash_genie` in the SQL file and set `DEMO_SCHEMA=<your_catalog>.demo_dash_genie`.

The app defaults to `workspace.demo_dash_genie`. With the Wanderbricks setup, the SQL creates curated views over `samples.wanderbricks`:

- `workspace.demo_dash_genie.bookings_enriched`
- `workspace.demo_dash_genie.orders_enriched`
- `workspace.demo_dash_genie.reviews_enriched`
- `workspace.demo_dash_genie.support_tickets_enriched`
- `workspace.demo_dash_genie.property_value_360`
- `workspace.demo_dash_genie.destination_quality_360`
- `workspace.demo_dash_genie.customer_health_360`
- `workspace.demo_dash_genie.repeat_value_360`

## Genie Space setup

Create a Genie Space named `Wanderbricks Revenue Genie` and add these curated views:

- `workspace.demo_dash_genie.bookings_enriched`
- `workspace.demo_dash_genie.orders_enriched`
- `workspace.demo_dash_genie.reviews_enriched`
- `workspace.demo_dash_genie.support_tickets_enriched`
- `workspace.demo_dash_genie.property_value_360`
- `workspace.demo_dash_genie.destination_quality_360`
- `workspace.demo_dash_genie.customer_health_360`
- `workspace.demo_dash_genie.repeat_value_360`

Suggested instructions:

```text
This Genie Space supports travel marketplace revenue, property value, review quality, cancellation, and repeat value analysis using the Wanderbricks dataset.

Business definitions:
- Booked revenue means SUM(revenue_amount) where order_status = 'Booked' in orders_enriched, or SUM(booked_revenue) in aggregate 360 views.
- Estimated gross margin is modeled as 18% of booked revenue in the curated views.
- Property type value questions should usually use property_value_360.
- High-value bookings with weak reviews should use destination_quality_360 or property_value_360. Weak reviews are ratings of 3 or lower.
- Cancellation rate means cancelled bookings divided by all bookings. For guest segment questions, use customer_health_360.segment and cancellation_rate_pct.
- Repeat value questions should use repeat_value_360. It includes both guests and properties as entity_type values.
- Customer risk is calculated in customer_health_360.risk_bucket from revenue, cancellation, and review-derived support signals.
- Revenue trend questions should use orders_enriched and order_month.
- Support and quality trend questions can use support_tickets_enriched and ticket_month.
- When ranking business impact, rank by booked_revenue unless the user asks for margin, repeat bookings, cancellations, reviews, or CSAT.
- Always show the time period used when answering trend questions.
```

Test these questions in Genie before using the app:

- Which property types generate the most value?
- Where do high-value bookings have weak reviews?
- What is the cancellation rate by segment?
- Which guests or properties drive repeat value?

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
GRANT USE CATALOG ON CATALOG samples TO `<app-service-principal>`;
GRANT USE SCHEMA ON SCHEMA samples.wanderbricks TO `<app-service-principal>`;
GRANT SELECT ON SCHEMA samples.wanderbricks TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.bookings_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.orders_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.reviews_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.support_tickets_enriched TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.property_value_360 TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.destination_quality_360 TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.customer_health_360 TO `<app-service-principal>`;
GRANT SELECT ON VIEW <your_catalog>.demo_dash_genie.repeat_value_360 TO `<app-service-principal>`;
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

If deploy fails with:

```text
The user is not authorized to make the request, please assign the user: <principal-id> CAN_MANAGE permission for the app: dash-genie-revenue-risk.
```

grant `CAN MANAGE` on the Databricks App to the service principal used by GitHub Actions. In Databricks, open the app, click **Share**, add the service principal from `DATABRICKS_CLIENT_ID`, choose **CAN MANAGE**, and save.

This is the deployer identity. It is different from the app runtime service principal shown in the app Authorization tab.

## Troubleshooting

- `NO_SUCH_CATALOG_EXCEPTION`: run `SHOW CATALOGS`, pick an existing catalog, rerun the setup SQL in that catalog, and set `DEMO_SCHEMA=<catalog>.demo_dash_genie` in `.env` and `app.yaml`.
- App deploy fails with missing `CAN_MANAGE`: grant `CAN MANAGE` on the Databricks App to the service principal used by GitHub Actions.
- Dashboard query fails: verify `DATABRICKS_WAREHOUSE_ID`, app resource keys, `DEMO_SCHEMA`, and table/view grants.
- Genie call fails: verify `GENIE_SPACE_ID`, `CAN RUN`, and access to the underlying views.
- Generated SQL does not run: the app only executes SQL that starts with `SELECT` or `WITH` and does not contain write or DDL keywords.
- Local auth fails: run `databricks auth login` and check `.env` values.
