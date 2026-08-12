-- ============================================================
-- 04_create_operations_mart.sql
-- Create an analytical mart for insurance operations
-- and payment performance
-- ============================================================
--operations_payment_mart
CREATE OR REPLACE TABLE mart.operations_payment_mart AS

SELECT
    f.transaction_id,

    -- Customer information
    c.customer_id,
    c.province,

    -- Policy information
    p.policy_id,
    p.product_type,
    p.policy_status,
    p.payment_frequency,

    -- Date information
    d.date_key AS transaction_date,
    d.year,
    d.month,
    d.quarter,

    -- Transaction information
    f.premium_amount,
    f.payment_status,

    -- Business priority
    CASE
        WHEN f.payment_status = 'Overdue'
             AND p.policy_status = 'Lapsed'
            THEN 'HIGH'

        WHEN f.payment_status = 'Overdue'
            THEN 'MEDIUM'

        WHEN f.payment_status = 'Pending'
            THEN 'MEDIUM'

        ELSE 'LOW'
    END AS payment_priority

FROM dw.fact_transaction f

LEFT JOIN dw.dim_customer c
    ON f.customer_id = c.customer_id

LEFT JOIN dw.dim_policy p
    ON f.policy_id = p.policy_id

LEFT JOIN dw.dim_date d
    ON f.date_key = d.date_key;


  --Total premium by province
  SELECT
    province,
    SUM(premium_amount) AS total_premium
FROM mart.operations_payment_mart
GROUP BY province
ORDER BY total_premium DESC;

--Overdue payments by province
SELECT
    province,
    COUNT(*) AS overdue_transactions,
    SUM(premium_amount) AS overdue_amount
FROM mart.operations_payment_mart
WHERE payment_status = 'Overdue'
GROUP BY province
ORDER BY overdue_amount DESC;
--Performance by product
SELECT
    product_type,
    COUNT(*) AS transaction_count,
    SUM(premium_amount) AS total_premium,
    AVG(premium_amount) AS average_premium
FROM mart.operations_payment_mart
GROUP BY product_type
ORDER BY total_premium DESC;
--Priority cases
SELECT
    payment_priority,
    COUNT(*) AS transaction_count,
    SUM(premium_amount) AS total_premium
FROM mart.operations_payment_mart
GROUP BY payment_priority
ORDER BY
    CASE payment_priority
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END;