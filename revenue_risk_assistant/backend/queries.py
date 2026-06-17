from revenue_risk_assistant.settings import HEALTH_VIEW, ORDERS_VIEW, TICKETS_VIEW


def years_query() -> str:
    return f"""
    SELECT DISTINCT order_year
    FROM {ORDERS_VIEW}
    ORDER BY order_year
    """


def kpi_query(year: int) -> str:
    return f"""
    SELECT
        ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
        ROUND(SUM(CASE WHEN order_status = 'Booked' THEN gross_margin_amount ELSE 0 END), 2) AS gross_margin,
        COUNT(DISTINCT customer_id) AS active_customers,
        ROUND(
            100.0 * SUM(CASE WHEN order_status IN ('Cancelled', 'Returned') THEN 1 ELSE 0 END) / COUNT(*),
            2
        ) AS exception_rate_pct
    FROM {ORDERS_VIEW}
    WHERE order_year = {year}
    """


def support_summary_query(year: int) -> str:
    return f"""
    SELECT
        SUM(CASE WHEN ticket_status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS open_tickets,
        ROUND(AVG(csat_score), 2) AS avg_csat
    FROM {TICKETS_VIEW}
    WHERE ticket_year = {year}
    """


def monthly_revenue_query(year: int) -> str:
    return f"""
    SELECT
        order_month,
        ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
        COUNT(*) AS orders
    FROM {ORDERS_VIEW}
    WHERE order_year = {year}
    GROUP BY order_month
    ORDER BY order_month
    """


def product_revenue_query(year: int) -> str:
    return f"""
    SELECT
        product_family,
        ROUND(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 2) AS booked_revenue,
        ROUND(
            100.0 * SUM(CASE WHEN order_status = 'Booked' THEN gross_margin_amount ELSE 0 END) /
            NULLIF(SUM(CASE WHEN order_status = 'Booked' THEN revenue_amount ELSE 0 END), 0),
            2
        ) AS margin_pct
    FROM {ORDERS_VIEW}
    WHERE order_year = {year}
    GROUP BY product_family
    ORDER BY booked_revenue DESC
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
