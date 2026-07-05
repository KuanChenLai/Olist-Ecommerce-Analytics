-- 1. Total Revenue
SELECT 
    ROUND(SUM(price), 2) AS total_revenue
FROM fact_orders;

-- 2. Total Orders
SELECT 
    COUNT(DISTINCT order_id) AS total_orders
FROM fact_orders;

-- 3. Total Customers
SELECT 
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM customer_summary;

-- 4. Total Sellers
SELECT 
    COUNT(DISTINCT seller_id) AS total_sellers
FROM fact_orders;

-- 5. Top 10 Product Categories by Revenue
SELECT 
    product_category_name,
    ROUND(SUM(price), 2) AS revenue
FROM fact_orders
GROUP BY product_category_name
ORDER BY revenue DESC
LIMIT 10;

-- 6. Monthly Revenue Trend
SELECT 
    year_month,
    ROUND(SUM(price), 2) AS monthly_revenue
FROM monthly_revenue
GROUP BY year_month
ORDER BY year_month;

-- 7. Top 10 Sellers by Revenue
SELECT 
    seller_id,
    ROUND(SUM(price), 2) AS revenue
FROM fact_orders
GROUP BY seller_id
ORDER BY revenue DESC
LIMIT 10;

-- 8. RFM Segment Revenue Contribution
SELECT
    Segment,
    customers,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(customer_percentage * 100, 2) AS customer_percentage,
    ROUND(revenue_percentage * 100, 2) AS revenue_percentage
FROM rfm_summary
ORDER BY total_revenue DESC;