-- ============================================================
-- 03_create_warehouse.sql
-- Create dimensional warehouse tables
-- ============================================================


-- ============================================================
-- CUSTOMER DIMENSION
-- ============================================================

CREATE OR REPLACE TABLE dw.dim_customer AS
SELECT DISTINCT
    customer_id,
    province
FROM staging.transactions;


-- ============================================================
-- POLICY DIMENSION
-- ============================================================

CREATE OR REPLACE TABLE dw.dim_policy AS
SELECT DISTINCT
    policy_id,
    customer_id,
    product_type,
    policy_status,
    payment_frequency
FROM staging.transactions;


-- ============================================================
-- DATE DIMENSION
-- ============================================================

CREATE OR REPLACE TABLE dw.dim_date AS
SELECT DISTINCT
    CAST(transaction_date AS DATE) AS date_key,
    EXTRACT(YEAR FROM CAST(transaction_date AS DATE)) AS year,
    EXTRACT(MONTH FROM CAST(transaction_date AS DATE)) AS month,
    EXTRACT(QUARTER FROM CAST(transaction_date AS DATE)) AS quarter,
    EXTRACT(DAY FROM CAST(transaction_date AS DATE)) AS day
FROM staging.transactions;


-- ============================================================
-- TRANSACTION FACT
-- ============================================================

CREATE OR REPLACE TABLE dw.fact_transaction AS
SELECT
    t.transaction_id,
    t.customer_id,
    t.policy_id,
    CAST(t.transaction_date AS DATE) AS date_key,
    t.premium_amount,
    t.payment_status
FROM staging.transactions t;
