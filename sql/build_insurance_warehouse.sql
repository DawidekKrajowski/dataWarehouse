-- ============================================================
-- MASTER BUILD SCRIPT
-- Insurance Operations Data Warehouse
--
-- Builds the complete pipeline:
--   1. Create schemas
--   2. Load cleaned data
--   3. Build dimensional warehouse
--   4. Build operations/payment mart
--   5. Run data quality checks
--
-- Local:
--   duckdb insurance.duckdb -c ".read build_insurance_warehouse.sql"
--
-- MotherDuck:
--   duckdb "md:insurance_warehouse" -c ".read build_insurance_warehouse.sql"
-- ============================================================


-- ============================================================
-- STEP 1: CREATE DATABASE SCHEMAS
-- ============================================================

.read 01_create_tables_dw.sql


-- ============================================================
-- STEP 2: LOAD CLEANED DATA INTO STAGING
-- ============================================================

.read 02_load_schema_dw.sql


-- ============================================================
-- STEP 3: BUILD DIMENSIONAL DATA WAREHOUSE
-- ============================================================

.read 03_create_warehouse.sql


-- ============================================================
-- STEP 4: BUILD OPERATIONS / PAYMENT DATA MART
-- ============================================================

.read 04_create_operations_mart.sql


-- ============================================================
-- STEP 5: RUN DATA QUALITY AND RECONCILIATION CHECKS
-- ============================================================

.read 05_data_quality_checks.sql


-- ============================================================
-- PIPELINE VERIFICATION
-- ============================================================

SELECT '=== INSURANCE DATA PIPELINE BUILD COMPLETE ===' AS status;

SELECT
    'staging.transactions' AS table_name,
    COUNT(*) AS row_count
FROM staging.transactions

UNION ALL

SELECT
    'dw.fact_transaction' AS table_name,
    COUNT(*) AS row_count
FROM dw.fact_transaction

UNION ALL

SELECT
    'mart.operations_payment_mart' AS table_name,
    COUNT(*) AS row_count
FROM mart.operations_payment_mart;


SELECT '=== BUILD SUCCESSFUL ===' AS status;