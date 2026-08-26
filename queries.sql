-- Questions answered by the project.

-- 1. Which category generates the most revenue?
SELECT category,
       ROUND(SUM(revenue), 2) AS total_revenue,
       SUM(quantity) AS units_sold
FROM orders
GROUP BY category
ORDER BY total_revenue DESC;

-- 2. Which region generates the most revenue?
SELECT region,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM orders
GROUP BY region
ORDER BY total_revenue DESC;

-- 3. What is the average order value?
SELECT ROUND(AVG(revenue), 2) AS average_order_value
FROM orders;
