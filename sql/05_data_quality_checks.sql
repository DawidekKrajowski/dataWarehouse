-- ============================================================
-- 05_data_quality_checks.sql
-- Automated Data Quality & Referential Integrity Validation
-- ============================================================

-- ------------------------------------------------------------
-- 1. PRIMARY KEY & UNIQUENESS CHECKS
-- (Each check should return 0 rows)
-- ------------------------------------------------------------

-- Duplicate Customer IDs in dim_customer
SELECT customer_id, COUNT(*) AS dup_count
FROM dw.dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Duplicate Policy IDs in dim_policy
SELECT policy_id, COUNT(*) AS dup_count
FROM dw.dim_policy
GROUP BY policy_id
HAVING COUNT(*) > 1;

-- Duplicate Transaction IDs in fact_transaction
SELECT transaction_id, COUNT(*) AS dup_count
FROM dw.fact_transaction
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- ------------------------------------------------------------
-- 2. NULL & MISSING VALUE CHECKS
-- (Counts should all equal 0)
-- ------------------------------------------------------------

SELECT
    SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) AS missing_transaction_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN policy_id IS NULL THEN 1 ELSE 0 END) AS missing_policy_id,
    SUM(CASE WHEN date_key IS NULL THEN 1 ELSE 0 END) AS missing_date_key,
    SUM(CASE WHEN premium_amount IS NULL THEN 1 ELSE 0 END) AS missing_premium_amount,
    SUM(CASE WHEN payment_status IS NULL THEN 1 ELSE 0 END) AS missing_payment_status
FROM dw.fact_transaction;


-- ------------------------------------------------------------
-- 3. REFERENTIAL INTEGRITY (ORPHAN CHECKS)
-- (Checks for foreign keys in fact with no match in dim; should return 0 rows)
-- ------------------------------------------------------------

-- Orphan Customers
SELECT f.transaction_id, f.customer_id
FROM dw.fact_transaction f
LEFT JOIN dw.dim_customer c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Orphan Policies
SELECT f.transaction_id, f.policy_id
FROM dw.fact_transaction f
LEFT JOIN dw.dim_policy p ON f.policy_id = p.policy_id
WHERE p.policy_id IS NULL;

-- Orphan Dates
SELECT f.transaction_id, f.date_key
FROM dw.fact_transaction f
LEFT JOIN dw.dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;


-- ------------------------------------------------------------
-- 4. BUSINESS RULE & DOMAIN VALIDATION
-- ------------------------------------------------------------

-- Invalid negative or zero premium amounts
SELECT *
FROM dw.fact_transaction
WHERE premium_amount <= 0;

-- Unexpected payment statuses
SELECT DISTINCT payment_status
FROM dw.fact_transaction
WHERE payment_status NOT IN ('Paid', 'Pending', 'Overdue');


-- ------------------------------------------------------------
-- 5. PIPELINE RECONCILIATION
-- (Verify row counts match across Staging, Fact, and Mart)
-- ------------------------------------------------------------

SELECT
    (SELECT COUNT(*) FROM staging.transactions) AS staging_rows,
    (SELECT COUNT(*) FROM dw.fact_transaction) AS fact_rows,
    (SELECT COUNT(*) FROM mart.operations_payment_mart) AS mart_rows,
    (SELECT COUNT(*) FROM staging.transactions) - (SELECT COUNT(*) FROM dw.fact_transaction) AS staging_vs_fact_diff;
