USE ShopEase_India_New;

-- Customer Analysis
-- Business Questions

-- Q1 Segment all customers into New, Returning, and Loyal based on their total number of orders. (New = 1 order, Returning = 2–4 orders, Loyal = 5+ orders)
-- Q2 Who are the top 10 customers by total lifetime revenue — and what segment do they belong to?
-- Q3 What percentage of customers who signed up in 2025 placed only one order and never returned?
-- Q4 Which region has the highest customer lifetime value?

-----------------------------------------------------------------------------------------------------------------------
-- SQL Query
-- 1.
SELECT 
	segment_count,
	COUNT(customer_id) AS total_customer,
	CAST(COUNT(customer_id)* 100.0 /SUM(COUNT(customer_id)) OVER() AS DECIMAl(5,2))pct_of_total_base
FROM
(
	SELECT 
		customer_id,
		CASE 
			WHEN COUNT(order_id) = 1 THEN 'New'
			WHEN COUNT(order_id) BETWEEN 2 AND 4 THEN 'Returning'
			WHEN COUNT(order_id) >= 5 THEN 'Loyal'
			ELSE 'other'
		END AS segment_count
	FROM Orders
	WHERE order_status = 'Delivered'
	GROUP BY customer_id
)t
GROUP BY segment_count;

-----------------------------------------------------------------------------------------------------------------------
-- 2.
SELECT TOP 10
	*,
	spend_2024 - spend_2025 AS diff
FROM
(
	SELECT 
		customer_id,
		SUM(total_amount) AS LTV,
		SUM(CASE WHEN year(order_date) = '2024' THEN total_amount ELSE 0 END) AS spend_2024,
		SUM(CASE WHEN year(order_date) = '2025' THEN total_amount ELSE 0 END) AS spend_2025,
		CASE 
			WHEN COUNT(*) = 1 THEN 'New' 
			WHEN COUNT(*) BETWEEN 2 AND 4 THEN 'Returning'
			WHEN COUNT(*) >= 5 THEN 'Loyal'
			ELSE 'other'
		END AS Segemnt
	FROM Orders
	WHERE order_status = 'Delivered'
	GROUP BY customer_id
)t
ORDER BY LTV DESC;

-----------------------------------------------------------------------------------------------------------------------
-- 3. 
SELECT 
	COUNT(CASE WHEN num_ofOrder = 1 THEN 1 END) * 100.0 / COUNT(*) AS Churn_percent
FROM 
(
	SELECT 
		 o.customer_id,
		 COUNT(*) AS num_ofOrder
	FROM Orders o
	LEFT JOIN customers c
		ON o.customer_id = c.customer_id
	WHERE c.signup_date >= '2025-01-01' AND c.signup_date <= '2025-12-31'
		AND o.order_status = 'Delivered'
	GROUP BY o.customer_id 
)t;

-----------------------------------------------------------------------------------------------------------------------
-- 4.
SELECT 
	c.region,
	SUM(total_amount) AS customer_lifetime_value,
	COUNT(DISTINCT c.customer_id) AS customer_count,
	CAST(SUM(total_amount) / COUNT(DISTINCT c.customer_id) AS DECIMAL(10,2)) Avg_LTV_Per_Customer
FROM Orders o
LEFT JOIN Customers c
	ON o.customer_id = c.customer_id
WHERE order_status = 'Delivered'
GROUP BY  c.region
ORDER BY customer_lifetime_value DESC;

-----------------------------------------------------------------------------------------------------------------------

-- Key Findings :

-- High Loyalty Base: 
-- Nearly 80% of our customers are in the "Loyal" segment (5+ orders), meaning we have a very solid group of repeat buyers.

-- Loss of Top Spenders: 
-- Our highest-value loyal customers significantly reduced their spending in 2025. For example, our top 1st customer spent 
-- nearly $700k less than they did the previous year.

-- Regional Differences: 
-- The North region is our most valuable area because it has the highest average spend per customer, even though the 
-- East has the highest total revenue.

-----------------------------------------------------------------------------------------------------------------------

-- Business Interpretation :

-- Our most loyal customers the "backbone" of our revenue are pulling back. We aren't losing customers,
-- but we are losing their "wallet share". We need to focus on why our North, region high spenders are suddenly spending less.

