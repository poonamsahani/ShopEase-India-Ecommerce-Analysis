USE ShopEase_India_New;

-- Time Series Analysis
-- Business Questions

-- Q1 What is the monthly revenue trend across 2024 and 2025 — and which months were strongest?
-- Q2 What is the month over month revenue growth rate — where did it accelerate and where did it drop?
-- Q3 How does revenue compare quarter by quarter — 2024 vs 2025 — broken down by category?
-- Q4 What is the average basket size — number of items and order value — by month across both years?

-----------------------------------------------------------------------------------------------------------------------
-- SQL Query
-- 1. 
SELECT
	MONTH(order_date) AS order_month,
	YEAR(order_date)AS order_year,
	SUM(CASE WHEN order_status = 'Delivered' THEN total_amount ELSE 0 END) as monthly_revenue
FROM Orders
GROUP BY 
	YEAR(order_date),
	MONTH(order_date)
ORDER BY order_year, order_month;

-----------------------------------------------------------------------------------------------------------------------
-- 2.
-- Note: January 2024 shows NULL for MoM growth as there is no prior month in dataset.
WITH MonthlyRevenue AS
(
	SELECT 
		YEAR(order_date) order_year,
		month(order_date) order_month,
		SUM(CASE WHEN order_status = 'Delivered' THEN total_amount ELSE 0 END) AS revenue 
	FROM Orders
	GROUP BY YEAR(order_date), month(order_date)
) 
SELECT 
	order_year,
	order_month,
	revenue AS current_month_revenue,
	LAG(revenue) OVER(ORDER BY order_year, order_month) previous_month_revenue,
	CAST((revenue - LAG(revenue) OVER(ORDER BY order_year,order_month))
	/LAG(revenue) OVER(ORDER BY order_year, order_month) * 100 AS decimal(10,2)) AS Mom_growth_rate
FROM MonthlyRevenue
ORDER BY order_year, order_month;

-----------------------------------------------------------------------------------------------------------------------
-- 3.
WITH Quarterly_Revenue AS
(
	SELECT 
		p.category AS Category,
		YEAR(o.order_date) AS Order_year,
		DATEPART(QUARTER , order_date) Order_quarter,
		CAST (SUM(
			CASE 
				WHEN o.order_status = 'Delivered' 
				THEN oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0) 
				ELSE 0
			END) AS DECIMAL(10,2))AS Revenue
	FROM orders o
	JOIN Order_Items oi
		ON o.order_id = oi.order_id
	JOIN products p
		ON oi.product_id = p.product_id 
	GROUP BY p.category, YEAR(o.order_date), DATEPART(QUARTER , order_date)
) 
SELECT 
	category,
	order_year,
	order_quarter,
	revenue,
	LAG(revenue) OVER(PARTITION BY category, order_quarter ORDER BY order_year) AS previous_year_revenue,
	Revenue - LAG(revenue) OVER(PARTITION BY category, order_quarter ORDER BY order_year) AS revenue_diff
FROM Quarterly_Revenue
ORDER BY 
	Category,
	Order_quarter,
	Order_year;

-----------------------------------------------------------------------------------------------------------------------
-- 4. 
WITH  CTE_Summary AS
(
	SELECT 
		o.order_id,
		MONTH(o.order_date) AS order_month,
		year(o.order_date) AS order_year,
		SUM(oi.quantity) AS total_item,
		CAST (SUM(
			CASE 
				WHEN o.order_status = 'Delivered' 
				THEN oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0) 
				ELSE 0
			 END) AS DECIMAL(10,2))AS order_value
	FROM Orders o
	JOIN Order_Items oi
		ON o.order_id = oi.order_id
	GROUP BY o.order_id, year(o.order_date), MONTH(o.order_date)
)
SELECT 
	order_year,
	order_month,
	AVG(total_item) AS Basket_size,
	CAST(AVG(order_value)AS decimal(10,2)) AS Aov
FROM CTE_Summary
GROUP BY 
	order_year,
	order_month
ORDER BY 
	order_year,
	order_month;

-----------------------------------------------------------------------------------------------------------------------

-- Key Findings :

-- Strong 2024 Performance: 
-- Revenue grew steadily throughout 2024, with a significant festive peak in November.

-- The 2025 Slump: 
-- 2025 started with a much lower revenue base than 2024. While there was steady growth until April,
-- a major drop occurred in May 2025, losing nearly $770k in a single month.

-- Shrinking Order Value: 
-- Even though customers kept buying roughly the same number of items per order as Basket Size 
-- remained consistent over 2 years, 
-- the Average Order Value (AOV) in 2025 dropped to less than half of what it was in 2024.

-----------------------------------------------------------------------------------------------------------------------

-- Business Interpretation :

-- The business is struggling to Sustain its 2024 momentum. The data shows that while we are still processing orders, 
-- the "value" of those orders has collapsed. This indicates that customers are either moving toward much cheaper 
-- products or we are failing to sell our high-ticket items in 2025.

-----------------------------------------------------------------------------------------------------------------------