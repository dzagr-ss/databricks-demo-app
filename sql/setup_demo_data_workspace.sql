-- Use this version if your workspace uses the `workspace` catalog.
-- If you prefer a different catalog, replace `workspace.demo_dash_genie`
-- with `<your_catalog>.demo_dash_genie` throughout this file and set DEMO_SCHEMA
-- to the same value in .env and app.yaml.

CREATE SCHEMA IF NOT EXISTS workspace.demo_dash_genie;

CREATE OR REPLACE TABLE workspace.demo_dash_genie.customers AS
SELECT
  CAST(id + 1 AS INT) AS customer_id,
  CONCAT('Customer ', LPAD(CAST(id + 1 AS STRING), 3, '0')) AS customer_name,
  CASE id % 5
    WHEN 0 THEN 'Germany'
    WHEN 1 THEN 'Spain'
    WHEN 2 THEN 'Italy'
    WHEN 3 THEN 'Poland'
    ELSE 'United Kingdom'
  END AS country,
  CASE id % 4
    WHEN 0 THEN 'Enterprise'
    WHEN 1 THEN 'Mid-Market'
    WHEN 2 THEN 'SMB'
    ELSE 'Strategic'
  END AS segment,
  CASE id % 5
    WHEN 0 THEN 'Pharma'
    WHEN 1 THEN 'Retail'
    WHEN 2 THEN 'Manufacturing'
    WHEN 3 THEN 'Financial Services'
    ELSE 'Technology'
  END AS industry
FROM range(40);

CREATE OR REPLACE TABLE workspace.demo_dash_genie.orders AS
SELECT
  CAST(id + 1 AS INT) AS order_id,
  CAST((id % 40) + 1 AS INT) AS customer_id,
  DATE_ADD(DATE '2025-01-01', CAST((id * 3) % 520 AS INT)) AS order_date,
  CASE id % 5
    WHEN 0 THEN 'Platform License'
    WHEN 1 THEN 'Data Engineering'
    WHEN 2 THEN 'BI Analytics'
    WHEN 3 THEN 'AI Enablement'
    ELSE 'Support Package'
  END AS product_family,
  CASE
    WHEN id % 17 = 0 THEN 'Cancelled'
    WHEN id % 13 = 0 THEN 'Returned'
    ELSE 'Booked'
  END AS order_status,
  ROUND(500 + (id % 19) * 125 + ((id * 37) % 100), 2) AS revenue_amount,
  ROUND((500 + (id % 19) * 125 + ((id * 37) % 100)) * (0.25 + (id % 7) * 0.035), 2) AS gross_margin_amount
FROM range(260);

CREATE OR REPLACE TABLE workspace.demo_dash_genie.support_tickets AS
SELECT
  CAST(id + 1 AS INT) AS ticket_id,
  CAST((id % 40) + 1 AS INT) AS customer_id,
  DATE_ADD(DATE '2025-01-05', CAST((id * 5) % 520 AS INT)) AS ticket_date,
  CASE
    WHEN id % 10 IN (0, 1) THEN 'High'
    WHEN id % 10 IN (2, 3, 4) THEN 'Medium'
    ELSE 'Low'
  END AS priority,
  CASE
    WHEN id % 11 = 0 THEN 'Open'
    WHEN id % 7 = 0 THEN 'In Progress'
    ELSE 'Resolved'
  END AS ticket_status,
  CASE id % 5
    WHEN 0 THEN 'Billing'
    WHEN 1 THEN 'Performance'
    WHEN 2 THEN 'Data Quality'
    WHEN 3 THEN 'Access'
    ELSE 'Feature Request'
  END AS issue_type,
  CASE
    WHEN id % 11 = 0 THEN NULL
    ELSE CAST(4 + (id % 48) AS INT)
  END AS hours_to_resolution,
  CASE
    WHEN id % 11 = 0 THEN NULL
    ELSE ROUND(2.5 + (id % 6) * 0.45, 2)
  END AS csat_score
FROM range(120);

CREATE OR REPLACE VIEW workspace.demo_dash_genie.orders_enriched AS
SELECT
  o.order_id,
  o.customer_id,
  c.customer_name,
  c.country,
  c.segment,
  c.industry,
  o.order_date,
  YEAR(o.order_date) AS order_year,
  DATE_TRUNC('month', o.order_date) AS order_month,
  o.product_family,
  o.order_status,
  o.revenue_amount,
  o.gross_margin_amount
FROM workspace.demo_dash_genie.orders o
JOIN workspace.demo_dash_genie.customers c
  ON o.customer_id = c.customer_id;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.support_tickets_enriched AS
SELECT
  t.ticket_id,
  t.customer_id,
  c.customer_name,
  c.country,
  c.segment,
  c.industry,
  t.ticket_date,
  YEAR(t.ticket_date) AS ticket_year,
  DATE_TRUNC('month', t.ticket_date) AS ticket_month,
  t.priority,
  t.ticket_status,
  t.issue_type,
  t.hours_to_resolution,
  t.csat_score
FROM workspace.demo_dash_genie.support_tickets t
JOIN workspace.demo_dash_genie.customers c
  ON t.customer_id = c.customer_id;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.customer_health_360 AS
WITH revenue AS (
  SELECT
    customer_id,
    ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
    ROUND(SUM(CASE WHEN order_status = 'Booked' THEN gross_margin_amount ELSE 0 END), 2) AS gross_margin,
    ROUND(
      100.0 * SUM(CASE WHEN order_status = 'Booked' THEN gross_margin_amount ELSE 0 END) /
      NULLIF(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 0),
      2
    ) AS margin_pct,
    COUNT(*) AS order_count,
    SUM(CASE WHEN order_status IN ('Cancelled', 'Returned') THEN 1 ELSE 0 END) AS exception_orders,
    MAX(order_date) AS latest_order_date
  FROM workspace.demo_dash_genie.orders_enriched
  GROUP BY customer_id
),
support AS (
  SELECT
    customer_id,
    COUNT(*) AS ticket_count,
    SUM(CASE WHEN ticket_status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN ticket_status IN ('Open', 'In Progress') AND priority = 'High' THEN 1 ELSE 0 END) AS high_priority_open_tickets,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    ROUND(AVG(hours_to_resolution), 2) AS avg_hours_to_resolution
  FROM workspace.demo_dash_genie.support_tickets_enriched
  GROUP BY customer_id
)
SELECT
  c.customer_id,
  c.customer_name,
  c.country,
  c.segment,
  c.industry,
  COALESCE(r.booked_revenue, 0) AS booked_revenue,
  COALESCE(r.gross_margin, 0) AS gross_margin,
  r.margin_pct,
  COALESCE(r.order_count, 0) AS order_count,
  COALESCE(r.exception_orders, 0) AS exception_orders,
  r.latest_order_date,
  COALESCE(s.ticket_count, 0) AS ticket_count,
  COALESCE(s.open_tickets, 0) AS open_tickets,
  COALESCE(s.high_priority_open_tickets, 0) AS high_priority_open_tickets,
  s.avg_csat,
  s.avg_hours_to_resolution,
  CASE
    WHEN COALESCE(s.high_priority_open_tickets, 0) >= 2 AND COALESCE(r.booked_revenue, 0) > 6000 THEN 'High'
    WHEN COALESCE(s.open_tickets, 0) >= 2 OR COALESCE(s.avg_csat, 5) < 3.2 THEN 'Medium'
    ELSE 'Low'
  END AS risk_bucket
FROM workspace.demo_dash_genie.customers c
LEFT JOIN revenue r ON c.customer_id = r.customer_id
LEFT JOIN support s ON c.customer_id = s.customer_id;

SELECT *
FROM workspace.demo_dash_genie.customer_health_360
ORDER BY booked_revenue DESC
LIMIT 10;
