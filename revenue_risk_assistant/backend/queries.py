from revenue_risk_assistant.settings import HEALTH_VIEW, ORDERS_VIEW, PROPERTY_VALUE_VIEW, TICKETS_VIEW


def years_query() -> str:
    return f"""
    SELECT DISTINCT order_year
    FROM {ORDERS_VIEW}
    ORDER BY order_year
    """


def kpi_query(year: int) -> str:
    return f"""
    WITH bookings AS (
        SELECT
            ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
            SUM(CASE WHEN order_status = 'Booked' THEN 1 ELSE 0 END) AS booking_count,
            SUM(CASE WHEN order_status = 'Booked' THEN stay_nights ELSE 0 END) AS booked_nights,
            ROUND(
                100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
                2
            ) AS cancellation_rate_pct
        FROM {ORDERS_VIEW}
        WHERE order_year = {year}
    ),
    quality AS (
        SELECT
            ROUND(AVG(csat_score), 2) AS avg_rating
        FROM {TICKETS_VIEW}
        WHERE ticket_year = {year}
    ),
    weak_review_properties AS (
        SELECT
            COUNT(DISTINCT o.property_id) AS high_value_weak_review_properties
        FROM {ORDERS_VIEW} o
        JOIN {PROPERTY_VALUE_VIEW} p
          ON o.property_id = p.property_id
        WHERE
            o.order_year = {year}
            AND p.booked_revenue >= 10000
            AND p.avg_rating < 4
    )
    SELECT
        COALESCE(b.booked_revenue, 0) AS booked_revenue,
        COALESCE(b.booking_count, 0) AS booking_count,
        COALESCE(b.booked_nights, 0) AS booked_nights,
        COALESCE(b.cancellation_rate_pct, 0) AS cancellation_rate_pct,
        COALESCE(q.avg_rating, 0) AS avg_rating,
        COALESCE(w.high_value_weak_review_properties, 0) AS high_value_weak_review_properties
    FROM bookings b
    CROSS JOIN quality q
    CROSS JOIN weak_review_properties w
    """


def property_type_value_query(year: int) -> str:
    return f"""
    SELECT
        o.product_family AS property_type,
        ROUND(SUM(CASE WHEN o.order_status = 'Booked' THEN o.revenue_amount ELSE 0 END), 2) AS booked_revenue,
        SUM(CASE WHEN o.order_status = 'Booked' THEN 1 ELSE 0 END) AS booking_count,
        ROUND(
            SUM(CASE WHEN o.order_status = 'Booked' THEN o.revenue_amount ELSE 0 END) /
            NULLIF(SUM(CASE WHEN o.order_status = 'Booked' THEN 1 ELSE 0 END), 0),
            2
        ) AS avg_booking_value,
        ROUND(AVG(p.avg_rating), 2) AS avg_rating
    FROM {ORDERS_VIEW} o
    LEFT JOIN {PROPERTY_VALUE_VIEW} p
      ON o.property_id = p.property_id
    WHERE o.order_year = {year}
    GROUP BY o.product_family
    ORDER BY booked_revenue DESC
    """


def cancellation_by_segment_query(year: int) -> str:
    return f"""
    SELECT
        segment,
        COUNT(*) AS bookings,
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
        ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
        ROUND(
            100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
            2
        ) AS cancellation_rate_pct
    FROM {ORDERS_VIEW}
    WHERE order_year = {year}
    GROUP BY segment
    ORDER BY cancellation_rate_pct DESC, booked_revenue DESC
    """


def property_opportunity_query(year: int) -> str:
    return f"""
    WITH year_property_value AS (
        SELECT
            property_id,
            property_title,
            product_family AS property_type,
            destination_name,
            ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
            SUM(CASE WHEN order_status = 'Booked' THEN 1 ELSE 0 END) AS booking_count,
            ROUND(
                SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END) /
                NULLIF(SUM(CASE WHEN order_status = 'Booked' THEN 1 ELSE 0 END), 0),
                2
            ) AS avg_booking_value
        FROM {ORDERS_VIEW}
        WHERE order_year = {year}
        GROUP BY property_id, property_title, product_family, destination_name
    )
    SELECT
        y.property_title,
        y.property_type,
        y.destination_name,
        y.booked_revenue,
        y.booking_count,
        y.avg_booking_value,
        p.avg_rating,
        p.weak_review_count,
        p.cancellation_rate_pct,
        p.value_quality_segment
    FROM year_property_value y
    LEFT JOIN {PROPERTY_VALUE_VIEW} p
      ON y.property_id = p.property_id
    ORDER BY
        CASE p.value_quality_segment
            WHEN 'High value / weak reviews' THEN 1
            WHEN 'High value' THEN 2
            WHEN 'Weak reviews' THEN 3
            ELSE 4
        END,
        y.booked_revenue DESC
    LIMIT 50
    """


def customer_risk_query() -> str:
    return f"""
    SELECT
        customer_name,
        country,
        segment,
        booked_revenue,
        margin_pct,
        open_tickets,
        high_priority_open_tickets,
        avg_csat,
        risk_bucket
    FROM {HEALTH_VIEW}
    ORDER BY
        CASE risk_bucket WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
        booked_revenue DESC
    LIMIT 40
    """
