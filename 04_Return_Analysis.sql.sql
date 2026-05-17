USE ShopEase_India_New;

-- Return Analysis
-- Business Questions

-- Q1 What is the return rate by category — and which category is causing the most revenue loss through returns?
-- Q2 What are the most common return reasons — and how do they differ across categories?
-- Q3 Which specific products have the highest return rate — and should they be reviewed or delisted?
-- Q4 How much total revenue was lost to refunds month by month in 2025 — and is it getting worse?

-----------------------------------------------------------------------------------------------------------------------
-- SQL Query
-- 1.
SELECT 
	p.category,
	COUNT(oi.product_id) AS total_item_sold,
	COUNT(r.order_id) AS returned_item_count,
	CAST(COUNT(r.order_id) * 100 / NULLIF(COUNT(oi.product_id),0) AS DECIMAL(10,2)) AS return_rate_pct,
	CAST(SUM(CASE 
				WHEN r.order_id IS NOT NULL THEN (oi.unit_price * oi.quantity) * (1 - oi.discount_pct / 100.0)
				ELSE 0 END) AS DECIMAL (10,2)) AS revenue_lost_to_returns
FROM Order_Items oi
JOIN Products p
	ON oi.product_id = p.product_id
LEFT JOIN Returns r
	ON r.order_id = oi.order_id
		AND r.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;

-----------------------------------------------------------------------------------------------------------------------
-- 2.
SELECT 
	COUNT(r.return_reason) AS reason_count,
	p.category,
	r.return_reason
FROM Returns r
LEFT JOIN Products p
	ON r.product_id = p.product_id
GROUP BY
	p.category, 
	r.return_reason
ORDER BY 
	p.category, 
	reason_count DESC;

-----------------------------------------------------------------------------------------------------------------------
-- 3.
WITH  HighReturnProducts AS 
(
	SELECT 
		p.product_id,
		p.product_name,
		COUNT(oi.product_id) AS Item_sold_count,
		COUNT(r.order_id) AS return_item_count,
		CAST(COUNT(r.order_id) * 100.0 / NULLIF(COUNT(oi.product_id),0) AS decimal (10,1) ) return_rate_pct
	FROM Order_Items oi
	JOIN Products p
		ON oi.product_id = p.product_id
	LEFT JOIN Returns r
		ON oi.order_id = r.order_id
			AND r.product_id = p.product_id
	GROUP BY p.product_id, p.product_name
	HAVING CAST(COUNT(r.order_id) * 100.0 / NULLIF(COUNT(oi.product_id),0) AS decimal (10,1) )  > 10.0
)
SELECT 
	hrp.product_id,
	hrp.product_name,
	r.return_reason,
	hrp.return_rate_pct,
	COUNT(*) AS reason_occurence
FROM Returns r
JOIN HighReturnProducts hrp
	ON r.product_id = hrp.product_id
GROUP BY hrp.product_id,
		hrp.product_name,
		r.return_reason,
		hrp.return_rate_pct
ORDER BY hrp.return_rate_pct DESC;

-----------------------------------------------------------------------------------------------------------------------
-- 4.
SELECT
	return_month,
	monthly_refund_amount,
	LAG(monthly_refund_amount) OVER (ORDER BY return_month) AS pre_month_refund,
	monthly_refund_amount - LAG(monthly_refund_amount) OVER (ORDER BY return_month) AS diff
FROM
(
	SELECT 
		MONTH(r.return_date) return_month,
		SUM(r.refund_amount) monthly_refund_amount
	FROM Returns r
	WHERE YEAR(r.return_date) = 2025
	GROUP BY 
		MONTH(r.return_date)
)t;
-----------------------------------------------------------------------------------------------------------------------

-- Key Findings :

-- Revenue Leakage: 
-- The Electronics category has a 9% return rate, causing an $8M loss in revenue. 
-- The most common reasons are "Damaged" items and products being "Not as Described".

-- Clothing Returns: 
-- Clothing has a high return rate driven primarily by "Changed Mind" which accounts for a huge portion of its returns.

-- Worsening Refund Trend:
-- Refund amounts in 2025 are highly unstable, with massive spikes in June and August where losses increased by 
-- over $350k and $490k respectively.

-- High-Risk Products: 
-- Specific items like the Samsung 43 inch Smart TV, boAt Airdopes 141, and Women Kurti Floral Print all
-- show a high return rate of 12%.

-----------------------------------------------------------------------------------------------------------------------

-- Business Interpretation :

-- Fix vs. Delist Strategy - Based on the return reasons, we should take two different paths for our top returned items:

-- The Fix List :
-- Products like the "Samsung Smart TV" and "boAt Airdopes" are being returned mostly because they are "Damaged". 
-- These are high-demand products, so we should keep them but fix our logistics and packaging to prevent shipping damage.

-- The Delist List : 
-- Clothing items like the "Women Kurti Floral Print" and "ShopEase Joggers" are being returned because customers "Changed their Mind".
-- This suggests the product quality or sizing doesn't meet expectations once the item arrives.
-- We should discontinue these items because these returns may negatively impact profitability and customer satisfaction.

-- Operational vs. Quality Issues - We have two distinct problems: 
-- Electronics returns are a logistics and description issue (items arriving broken or not as expected). 
-- Clothing returns are a customer intent issue (people buying on impulse due to discounts and then changing their minds).
-- Both are draining our cash flow month-over-month.

-----------------------------------------------------------------------------------------------------------------------