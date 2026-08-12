-- ============================================================
-- 02_load_schema_dw.sql
-- Load cleaned CSV into the staging layer
-- ============================================================

CREATE OR REPLACE TABLE staging.transactions AS
SELECT *
FROM read_csv_auto(
    'F:/DATA_ENG_PROJECTS/Data_Eng_warehouse_insurance/data/insurance_operations_transactions_clean.csv',
    header = true
);