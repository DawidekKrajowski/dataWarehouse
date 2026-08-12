from pathlib import Path
import pandas as pd

# Automatically target the project root (one level up from python/)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Target the data folder inside the project root
INPUT_FILE = PROJECT_ROOT / "data" / "insurance_operations_transactions_raw.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "insurance_operations_transactions_clean.csv"

# Load raw data
df = pd.read_csv(INPUT_FILE)

print("=== RAW DATA QUALITY REPORT ===")
print(f"Rows received: {len(df)}")
print(f"Duplicate transaction IDs: {df['transaction_id'].duplicated().sum()}")
print(f"Missing values by column:\n{df.isna().sum()}")

# Remove duplicate transaction IDs, keeping the first occurrence
df = df.drop_duplicates(subset=["transaction_id"], keep="first")

# Standardize text fields
df["province"] = df["province"].astype("string").str.strip().str.title()
df["product_type"] = df["product_type"].astype("string").str.strip().str.title()
df["policy_status"] = df["policy_status"].astype("string").str.strip().str.title()
df["payment_frequency"] = df["payment_frequency"].astype("string").str.strip().str.title()
df["payment_status"] = df["payment_status"].astype("string").str.strip().str.title()

# Convert dates; invalid dates become missing
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)

# Convert premium to numeric
df["premium_amount"] = pd.to_numeric(
    df["premium_amount"],
    errors="coerce"
)

# Treat invalid negative premiums as missing
df.loc[df["premium_amount"] < 0, "premium_amount"] = pd.NA

# Remove records missing fields required by the warehouse
required_columns = [
    "transaction_id",
    "customer_id",
    "policy_id",
    "transaction_date",
    "product_type",
    "policy_status",
    "premium_amount",
    "province",
    "payment_frequency",
    "payment_status"
]

before_drop = len(df)
df = df.dropna(subset=required_columns)
rows_removed = before_drop - len(df)

# Convert date back to YYYY-MM-DD for the output CSV
df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")

# Save cleaned dataset
df.to_csv(OUTPUT_FILE, index=False)

print("\n=== CLEAN DATA QUALITY REPORT ===")
print(f"Rows written: {len(df)}")
print(f"Rows removed during cleaning: {rows_removed}")
print(f"Remaining duplicate transaction IDs: {df['transaction_id'].duplicated().sum()}")
print(f"Remaining missing values: {df.isna().sum().sum()}")
print(f"Output file: {OUTPUT_FILE}")