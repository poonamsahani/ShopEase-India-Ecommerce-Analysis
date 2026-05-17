USE ShopEase_India_New;

-- Product Analysis
-- Business Questions

-- Q1 Which product category contributes most to total revenue — and how has that share shifted from 2024 to 2025?
-- Q2 What are the top 5 and bottom 5 products by revenue in 2025 — ranked within their category?
-- Q3 How did the new Clothing line launched in March 2025 perform month by month after launch?
-- Q4 What is the average discount percentage given per category — and is heavy discounting hurting net revenue?

-----------------------------------------------------------------------------------------------------------------------
-- SQL Query
-- 1.
SELECT
*,
revenue_2024-revenue_2025 AS Diff,
CAST(revenue_2024 * 100.0 / SUM(revenue_2024) OVER() AS DECIMAL(5,2)) AS share_2024_pct,
CAST(revenue_2025 * 100.0 / SUM(revenue_2025) OVER() AS DECIMAL(5,2)) AS share_2025_pct
FROM
(
	SELECT
		p.category,
		CAST(SUM(CASE 
					WHEN YEAR(o.order_date) = '2024' 
					THEN (oi.unit_price*oi.quantity)* (1-oi.discount_pct/100.0) ELSE 0 END) AS DECIMAL(10,2)) AS revenue_2024,
		CAST(SUM(CASE 
					WHEN YEAR(o.order_date) = '2025' 
					THEN (oi.unit_price*oi.quantity)* (1-oi.discount_pct/100.0) ELSE 0 END) AS DECIMAL(10,2)) AS revenue_2025
	FROM Orders o
	LEFT JOIN Order_Items oi
		ON o.order_id = oi.order_id
	LEFT JOIN Products p
		ON oi.product_id = p.product_id
	WHERE o.order_status = 'Delivered'
	GROUP BY p.category
)t;

-----------------------------------------------------------------------------------------------------------------------
-- 2.
WITH Product_Revenue AS
(
	SELECT
		p.category,
		p.product_name,
		CAST(SUM(oi.quantity*oi.unit_price * (1- oi.discount_pct / 100.0)) AS DECIMAL(10,2)) Revenue,
		DENSE_RANK() OVER(PARTITION BY p.category ORDER BY SUM(oi.quantity*oi.unit_price * (1- oi.discount_pct / 100.0)) DESC) AS top_5,
		DENSE_RANK() OVER(PARTITION BY p.category ORDER BY SUM(oi.quantity*oi.unit_price * (1- oi.discount_pct / 100.0)) ASC) AS Bottom_5
	FROM Orders o 
	LEFT JOIN Order_Items oi
		ON o.order_id = oi.order_id
	LEFT JOIN Products p
		ON oi.product_id = p.product_id
	WHERE YEAR(o.order_date) = '2025'
	GROUP BY p.category, p.product_name
)
SELECT 
	* 
FROM Product_Revenue pr
WHERE top_5 <= 5 OR Bottom_5 <= 5
ORDER BY pr.category, pr.top_5;

-----------------------------------------------------------------------------------------------------------------------
-- 3.
SELECT
	order_month,
	Order_year,
	Total_revenue,
	LAG(Total_revenue) OVER(ORDER BY order_year ,order_month) AS Prv_month_revn,
	Total_revenue - LAG(Total_revenue) OVER(ORDER BY order_year, order_month) Rvn_diff
FROM
(
	SELECT 
		MONTH(o.order_date) order_month,
		YEAR(o.order_date) Order_year,
		CAST(SUM(oi.unit_price*oi.quantity* (1-oi.discount_pct/100.0))AS DECIMAL(10,2)) AS Total_revenue
	FROM Orders o
	LEFT JOIN Order_Items oi
		ON o.order_id = oi.order_id
	LEFT JOIN Products p
		ON oi.product_id = p.product_id
	WHERE YEAR(launch_date) = '2025' AND MONTH(launch_date) = '3'
			AND p.category = 'Clothing'
	GROUP BY YEAR(o.order_date), MONTH(Order_date)
)t 
WHERE Order_year = '2025' AND order_month >= '3';

-----------------------------------------------------------------------------------------------------------------------
-- 4.
SELECT
	p.category,
	AVG(oi.discount_pct) Avg_Discount_Pct,
	CAST(SUM(oi.unit_price*oi.quantity*(1- oi.discount_pct/100.0)) AS DECIMAL(10,2)) as Net_revenue,
	CAST(SUM(oi.quantity*oi.unit_price) AS DECIMAL(10,2)) AS gross_revenue, 
	CAST(SUM(oi.quantity*oi.unit_price) AS DECIMAL(10,2))  - CAST(SUM(oi.unit_price*oi.quantity*(1- oi.discount_pct/100.0)) AS DECIMAL(10,2)) AS diff
FROM Orders o
LEFT JOIN Order_Items oi
	ON o.order_id = oi.order_id
LEFT JOIN Products p
	ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY Avg_Discount_Pct DESC;

-----------------------------------------------------------------------------------------------------------------------

-- Key Findings :

-- Category Shift: 
-- Electronics revenue dropped by a massive $26M in 2025. During this same time, Clothing revenue doubled, 
-- but it was not enough to make up for the Electronics loss.

-- The Discount Factor: 
-- Clothing has the highest average discount rate at 8.5%, while Electronics is slightly lower at 8.2%.

-- New Launch Performance: 
-- The clothing line launched in March 2025 shows inconsistent growth, often dropping in revenue as soon as promotional periods end.

-----------------------------------------------------------------------------------------------------------------------

-- Business Interpretation :

-- Our business model is shifting from high-value Electronics to high-volume Clothing. 
-- However, the Clothing growth seems "forced" by high discounts. We are essentially trading high-margin 
-- electronic sales for low-margin clothing sales, which is hurting our overall bottom line.

-----------------------------------------------------------------------------------------------------------------------
