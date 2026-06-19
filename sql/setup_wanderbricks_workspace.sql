-- Wanderbricks setup for the default Databricks App schema.
-- Source dataset: samples.wanderbricks
-- Target semantic layer: workspace.demo_dash_genie
--
-- Run this in a Databricks SQL editor before configuring the Genie Space.

CREATE SCHEMA IF NOT EXISTS workspace.demo_dash_genie;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.bookings_enriched AS
SELECT
  b.booking_id,
  b.user_id,
  u.name AS guest_name,
  u.country AS guest_country,
  u.user_type AS guest_segment,
  b.property_id,
  p.title AS property_title,
  p.property_type,
  p.host_id,
  d.destination_id,
  d.name AS destination_name,
  b.check_in,
  b.check_out,
  DATEDIFF(b.check_out, b.check_in) AS stay_nights,
  b.total_amount,
  b.status AS booking_status,
  CASE
    WHEN LOWER(b.status) IN ('cancelled', 'canceled') THEN 'Cancelled'
    WHEN LOWER(b.status) IN ('returned', 'refunded') THEN 'Returned'
    ELSE 'Booked'
  END AS normalized_status
FROM samples.wanderbricks.bookings b
JOIN samples.wanderbricks.users u
  ON b.user_id = u.user_id
JOIN samples.wanderbricks.properties p
  ON b.property_id = p.property_id
LEFT JOIN samples.wanderbricks.destinations d
  ON p.destination_id = d.destination_id;

-- Compatibility view used by the current dashboard code.
CREATE OR REPLACE VIEW workspace.demo_dash_genie.orders_enriched AS
SELECT
  booking_id AS order_id,
  user_id AS customer_id,
  guest_name AS customer_name,
  guest_country AS country,
  guest_segment AS segment,
  'Travel' AS industry,
  check_in AS order_date,
  YEAR(check_in) AS order_year,
  DATE_TRUNC('month', check_in) AS order_month,
  property_type AS product_family,
  normalized_status AS order_status,
  ROUND(total_amount, 2) AS revenue_amount,
  ROUND(CASE WHEN normalized_status = 'Booked' THEN total_amount * 0.18 ELSE 0 END, 2) AS gross_margin_amount,
  booking_id,
  property_id,
  property_title,
  destination_id,
  destination_name,
  stay_nights
FROM workspace.demo_dash_genie.bookings_enriched;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.reviews_enriched AS
SELECT
  r.property_id,
  r.user_id,
  u.name AS guest_name,
  u.country AS guest_country,
  u.user_type AS guest_segment,
  p.title AS property_title,
  p.property_type,
  d.destination_id,
  d.name AS destination_name,
  r.rating,
  r.is_deleted
FROM samples.wanderbricks.reviews r
JOIN samples.wanderbricks.properties p
  ON r.property_id = p.property_id
LEFT JOIN samples.wanderbricks.users u
  ON r.user_id = u.user_id
LEFT JOIN samples.wanderbricks.destinations d
  ON p.destination_id = d.destination_id
WHERE r.is_deleted = false;

-- Compatibility support-style view, derived from review quality signals.
CREATE OR REPLACE VIEW workspace.demo_dash_genie.support_tickets_enriched AS
WITH review_context AS (
  SELECT
    r.*,
    b.booking_id,
    b.check_out,
    ROW_NUMBER() OVER (
      PARTITION BY r.property_id, r.user_id, r.rating
      ORDER BY b.check_out DESC NULLS LAST
    ) AS booking_rank
  FROM workspace.demo_dash_genie.reviews_enriched r
  LEFT JOIN workspace.demo_dash_genie.bookings_enriched b
    ON r.user_id = b.user_id
    AND r.property_id = b.property_id
)
SELECT
  ROW_NUMBER() OVER (ORDER BY r.property_id, r.user_id, r.rating, r.booking_id) AS ticket_id,
  r.user_id AS customer_id,
  r.guest_name AS customer_name,
  r.guest_country AS country,
  r.guest_segment AS segment,
  'Travel' AS industry,
  COALESCE(r.check_out, CURRENT_DATE()) AS ticket_date,
  YEAR(COALESCE(r.check_out, CURRENT_DATE())) AS ticket_year,
  DATE_TRUNC('month', COALESCE(r.check_out, CURRENT_DATE())) AS ticket_month,
  CASE
    WHEN r.rating <= 2 THEN 'High'
    WHEN r.rating = 3 THEN 'Medium'
    ELSE 'Low'
  END AS priority,
  CASE
    WHEN r.rating <= 2 THEN 'Open'
    WHEN r.rating = 3 THEN 'In Progress'
    ELSE 'Resolved'
  END AS ticket_status,
  'Review quality' AS issue_type,
  CASE WHEN r.rating <= 3 THEN NULL ELSE 24 END AS hours_to_resolution,
  CAST(r.rating AS DOUBLE) AS csat_score,
  r.property_id,
  r.property_title,
  r.property_type,
  r.destination_name
FROM review_context r
WHERE r.booking_rank = 1;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.property_value_360 AS
WITH booking_value AS (
  SELECT
    property_id,
    property_title,
    property_type,
    destination_name,
    COUNT(*) AS booking_count,
    COUNT(DISTINCT user_id) AS unique_guests,
    SUM(CASE WHEN normalized_status = 'Booked' THEN 1 ELSE 0 END) AS booked_count,
    SUM(CASE WHEN normalized_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
    ROUND(SUM(CASE WHEN normalized_status = 'Booked' THEN total_amount ELSE 0 END), 2) AS booked_revenue,
    ROUND(SUM(CASE WHEN normalized_status = 'Booked' THEN total_amount * 0.18 ELSE 0 END), 2) AS estimated_margin,
    SUM(CASE WHEN normalized_status = 'Booked' THEN stay_nights ELSE 0 END) AS booked_nights
  FROM workspace.demo_dash_genie.bookings_enriched
  GROUP BY property_id, property_title, property_type, destination_name
),
review_quality AS (
  SELECT
    property_id,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS review_count,
    SUM(CASE WHEN rating <= 3 THEN 1 ELSE 0 END) AS weak_review_count
  FROM workspace.demo_dash_genie.reviews_enriched
  GROUP BY property_id
)
SELECT
  b.*,
  r.avg_rating,
  COALESCE(r.review_count, 0) AS review_count,
  COALESCE(r.weak_review_count, 0) AS weak_review_count,
  ROUND(100.0 * b.cancelled_count / NULLIF(b.booking_count, 0), 2) AS cancellation_rate_pct,
  ROUND(b.booked_revenue / NULLIF(b.booked_count, 0), 2) AS avg_booking_value,
  CASE
    WHEN b.booked_revenue >= 10000 AND COALESCE(r.avg_rating, 5) < 4 THEN 'High value / weak reviews'
    WHEN b.booked_revenue >= 10000 THEN 'High value'
    WHEN COALESCE(r.avg_rating, 5) < 4 THEN 'Weak reviews'
    ELSE 'Healthy'
  END AS value_quality_segment
FROM booking_value b
LEFT JOIN review_quality r
  ON b.property_id = r.property_id;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.destination_quality_360 AS
SELECT
  destination_name,
  property_type,
  COUNT(DISTINCT property_id) AS properties,
  SUM(booked_count) AS booked_count,
  ROUND(SUM(booked_revenue), 2) AS booked_revenue,
  ROUND(AVG(avg_rating), 2) AS avg_rating,
  SUM(weak_review_count) AS weak_review_count,
  ROUND(AVG(cancellation_rate_pct), 2) AS avg_cancellation_rate_pct,
  SUM(CASE WHEN value_quality_segment = 'High value / weak reviews' THEN 1 ELSE 0 END) AS high_value_weak_review_properties
FROM workspace.demo_dash_genie.property_value_360
GROUP BY destination_name, property_type;

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
    COUNT(DISTINCT property_id) AS properties_booked,
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
  u.user_id AS customer_id,
  u.name AS customer_name,
  u.country,
  u.user_type AS segment,
  'Travel' AS industry,
  COALESCE(r.booked_revenue, 0) AS booked_revenue,
  COALESCE(r.gross_margin, 0) AS gross_margin,
  r.margin_pct,
  COALESCE(r.order_count, 0) AS order_count,
  COALESCE(r.properties_booked, 0) AS properties_booked,
  COALESCE(r.exception_orders, 0) AS exception_orders,
  ROUND(100.0 * COALESCE(r.exception_orders, 0) / NULLIF(r.order_count, 0), 2) AS cancellation_rate_pct,
  r.latest_order_date,
  COALESCE(s.ticket_count, 0) AS ticket_count,
  COALESCE(s.open_tickets, 0) AS open_tickets,
  COALESCE(s.high_priority_open_tickets, 0) AS high_priority_open_tickets,
  s.avg_csat,
  s.avg_hours_to_resolution,
  CASE
    WHEN COALESCE(s.high_priority_open_tickets, 0) >= 2 AND COALESCE(r.booked_revenue, 0) > 10000 THEN 'High'
    WHEN COALESCE(r.exception_orders, 0) >= 2 OR COALESCE(s.avg_csat, 5) < 3.5 THEN 'Medium'
    ELSE 'Low'
  END AS risk_bucket
FROM samples.wanderbricks.users u
LEFT JOIN revenue r ON u.user_id = r.customer_id
LEFT JOIN support s ON u.user_id = s.customer_id;

CREATE OR REPLACE VIEW workspace.demo_dash_genie.repeat_value_360 AS
SELECT
  'Guest' AS entity_type,
  customer_id AS entity_id,
  customer_name AS entity_name,
  country,
  segment,
  order_count AS booking_count,
  properties_booked,
  booked_revenue,
  gross_margin,
  ROUND(booked_revenue / NULLIF(order_count, 0), 2) AS avg_booking_value,
  CASE WHEN order_count >= 2 THEN true ELSE false END AS is_repeat_value_driver
FROM workspace.demo_dash_genie.customer_health_360
WHERE order_count > 0
UNION ALL
SELECT
  'Property' AS entity_type,
  property_id AS entity_id,
  property_title AS entity_name,
  destination_name AS country,
  property_type AS segment,
  booking_count,
  unique_guests AS properties_booked,
  booked_revenue,
  estimated_margin AS gross_margin,
  avg_booking_value,
  CASE WHEN unique_guests >= 2 AND booked_count >= 2 THEN true ELSE false END AS is_repeat_value_driver
FROM workspace.demo_dash_genie.property_value_360
WHERE booking_count > 0;

SELECT *
FROM workspace.demo_dash_genie.property_value_360
ORDER BY booked_revenue DESC
LIMIT 10;
