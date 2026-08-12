-- ============================================================
-- 06_total_analysis.sql
-- Useful business and data-quality statistics for the
-- Insurance Operations Payment Mart
-- ============================================================

-- 1. OVERALL PORTFOLIO SUMMARY
SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium,
    ROUND(MIN(premium_amount), 1) AS minimum_premium,
    ROUND(MAX(premium_amount), 1) AS maximum_premium
FROM mart.operations_payment_mart;


-- 2. PAYMENT STATUS SUMMARY
SELECT
    payment_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage_of_transactions
FROM mart.operations_payment_mart
GROUP BY payment_status
ORDER BY total_premium DESC;


-- 3. TOTAL PREMIUM BY PROVINCE
SELECT
    province,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY province
ORDER BY total_premium DESC;


-- 4. OVERDUE PAYMENTS BY PROVINCE
SELECT
    province,
    COUNT(*) AS overdue_transactions,
    ROUND(SUM(premium_amount), 1) AS overdue_amount,
    ROUND(100.0 * SUM(premium_amount) /
          SUM(SUM(premium_amount)) OVER (), 1) AS percent_of_overdue_amount
FROM mart.operations_payment_mart
WHERE payment_status = 'Overdue'
GROUP BY province
ORDER BY overdue_amount DESC;


-- 5. PERFORMANCE BY PRODUCT
SELECT
    product_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium,
    ROUND(MIN(premium_amount), 1) AS minimum_premium,
    ROUND(MAX(premium_amount), 1) AS maximum_premium
FROM mart.operations_payment_mart
GROUP BY product_type
ORDER BY total_premium DESC;


-- 6. PAYMENT STATUS BY PRODUCT
SELECT
    product_type,
    payment_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium
FROM mart.operations_payment_mart
GROUP BY product_type, payment_status
ORDER BY product_type, total_premium DESC;


-- 7. POLICY STATUS SUMMARY
SELECT
    policy_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY policy_status
ORDER BY transaction_count DESC;


-- 8. PAYMENT PRIORITY SUMMARY
SELECT
    payment_priority,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY payment_priority
ORDER BY
    CASE payment_priority
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END;


-- 9. HIGH-PRIORITY TRANSACTIONS
SELECT
    transaction_id,
    customer_id,
    policy_id,
    province,
    product_type,
    policy_status,
    payment_status,
    ROUND(premium_amount, 1) AS premium_amount,
    payment_priority
FROM mart.operations_payment_mart
WHERE payment_priority = 'HIGH'
ORDER BY premium_amount DESC;


-- 10. PREMIUM BY MONTH
SELECT
    year,
    month,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY year, month
ORDER BY year, month;


-- 11. PAYMENT STATUS BY MONTH
SELECT
    year,
    month,
    payment_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium
FROM mart.operations_payment_mart
GROUP BY year, month, payment_status
ORDER BY year, month, payment_status;


-- 12. PROVINCE + PRODUCT PERFORMANCE
SELECT
    province,
    product_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY province, product_type
ORDER BY total_premium DESC;


-- 13. PAYMENT FREQUENCY SUMMARY
SELECT
    payment_frequency,
    COUNT(*) AS transaction_count,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium
FROM mart.operations_payment_mart
GROUP BY payment_frequency
ORDER BY total_premium DESC;


-- 14. OVERDUE RATE BY PROVINCE
SELECT
    province,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN payment_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_transactions,
    ROUND(
        100.0 * SUM(CASE WHEN payment_status = 'Overdue' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS overdue_rate_percent
FROM mart.operations_payment_mart
GROUP BY province
ORDER BY overdue_rate_percent DESC;


-- 15. OVERDUE RATE BY PRODUCT
SELECT
    product_type,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN payment_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_transactions,
    ROUND(
        100.0 * SUM(CASE WHEN payment_status = 'Overdue' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS overdue_rate_percent
FROM mart.operations_payment_mart
GROUP BY product_type
ORDER BY overdue_rate_percent DESC;


-- 16. DATA QUALITY: DUPLICATE TRANSACTIONS
-- Should return zero rows.
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count
FROM mart.operations_payment_mart
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 17. DATA QUALITY: MISSING VALUES
SELECT
    SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) AS missing_transaction_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN policy_id IS NULL THEN 1 ELSE 0 END) AS missing_policy_id,
    SUM(CASE WHEN transaction_date IS NULL THEN 1 ELSE 0 END) AS missing_transaction_date,
    SUM(CASE WHEN province IS NULL THEN 1 ELSE 0 END) AS missing_province,
    SUM(CASE WHEN premium_amount IS NULL THEN 1 ELSE 0 END) AS missing_premium,
    SUM(CASE WHEN payment_status IS NULL THEN 1 ELSE 0 END) AS missing_payment_status
FROM mart.operations_payment_mart;


-- 18. DATA QUALITY: INVALID PREMIUMS
-- Should return zero rows.
SELECT *
FROM mart.operations_payment_mart
WHERE premium_amount < 0;


-- 19. SOURCE-TO-WAREHOUSE RECONCILIATION
SELECT
    (SELECT COUNT(*) FROM staging.transactions) AS staging_count,
    (SELECT COUNT(*) FROM dw.fact_transaction) AS fact_count,
    (SELECT COUNT(*) FROM staging.transactions)
        - (SELECT COUNT(*) FROM dw.fact_transaction) AS difference;


-- 20. EXECUTIVE KPI SUMMARY
SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(premium_amount), 1) AS total_premium,
    ROUND(AVG(premium_amount), 1) AS average_premium,
    ROUND(SUM(CASE WHEN payment_status = 'Paid' THEN premium_amount ELSE 0 END), 1) AS paid_premium,
    ROUND(SUM(CASE WHEN payment_status = 'Overdue' THEN premium_amount ELSE 0 END), 1) AS overdue_premium,
    ROUND(SUM(CASE WHEN payment_status = 'Pending' THEN premium_amount ELSE 0 END), 1) AS pending_premium,
    SUM(CASE WHEN payment_priority = 'HIGH' THEN 1 ELSE 0 END) AS high_priority_transactions,
    ROUND(
        100.0 * SUM(CASE WHEN payment_status = 'Paid' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS paid_transaction_rate_percent
FROM mart.operations_payment_mart;