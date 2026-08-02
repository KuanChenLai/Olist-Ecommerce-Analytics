-- Olist business analysis queries (SQLite)
-- fact_orders contains delivered orders only.

-- 1. Executive KPIs
SELECT
    ROUND(SUM(price), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT seller_id) AS active_sellers,
    COUNT(DISTINCT product_category_name) AS product_categories,
    ROUND(SUM(price) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(AVG(price), 2) AS average_product_price
FROM fact_orders;

-- 2. Monthly revenue trend
SELECT
    year_month,
    ROUND(price, 2) AS revenue
FROM monthly_revenue
ORDER BY year_month;

-- 3. Top product categories and revenue share
WITH category_revenue AS (
    SELECT
        product_category_name,
        SUM(price) AS revenue
    FROM fact_orders
    GROUP BY product_category_name
),
platform_total AS (
    SELECT SUM(revenue) AS total_revenue
    FROM category_revenue
)
SELECT
    product_category_name,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / total_revenue * 100, 2) AS revenue_percentage
FROM category_revenue
CROSS JOIN platform_total
ORDER BY revenue DESC
LIMIT 10;

-- 4. Top sellers and platform revenue share
WITH seller_revenue AS (
    SELECT seller_id, SUM(price) AS revenue
    FROM fact_orders
    GROUP BY seller_id
),
platform_total AS (
    SELECT SUM(revenue) AS total_revenue
    FROM seller_revenue
)
SELECT
    seller_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / total_revenue * 100, 2) AS revenue_percentage
FROM seller_revenue
CROSS JOIN platform_total
ORDER BY revenue DESC
LIMIT 10;

-- 5. Repeat purchase KPIs
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS repeat_purchase_rate,
    ROUND(AVG(total_spent), 2) AS average_customer_spend
FROM customer_summary;

-- 6. One-time vs repeat customer value
SELECT
    CASE WHEN order_count > 1 THEN 'Repeat' ELSE 'One-time' END AS customer_type,
    COUNT(*) AS customers,
    ROUND(AVG(total_spent), 2) AS average_spend,
    ROUND(AVG(order_count), 2) AS average_orders
FROM customer_summary
GROUP BY customer_type
ORDER BY average_spend DESC;

-- 7. RFM segment contribution
SELECT
    Segment,
    customers,
    ROUND(customer_percentage * 100, 2) AS customer_percentage,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(revenue_percentage * 100, 2) AS revenue_percentage,
    ROUND(avg_recency, 1) AS average_recency_days,
    ROUND(avg_frequency, 2) AS average_frequency,
    ROUND(avg_monetary, 2) AS average_monetary
FROM rfm_summary
ORDER BY Segment_Order;

-- 8. Raw order status quality check
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS order_percentage
FROM orders
GROUP BY order_status
ORDER BY orders DESC;
