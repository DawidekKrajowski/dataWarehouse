# Insurance Operations Data Warehouse

A end-to-end local data engineering pipeline built with **DuckDB** and **Python**. This project ingests, cleans, and transforms raw insurance transaction data into a dimensional warehouse and an operational payment data mart.

---

## 🛠️ Tech Stack & Architecture

* **Database Engine:** DuckDB
* **Data Processing:** Python, SQL
* **Data Modeling:** Star Schema (Staging $\rightarrow$ Dimensional Warehouse $\rightarrow$ Data Marts)
---------------------------------
# Insurance Operations & Payment Analytics Warehouse

An end-to-end data engineering and business intelligence solution analyzing policy collections, premium revenue distributions, and payment status trends.

> 💡 **Interactive Files:**
> - 📄 [View Full PDF Report](data/insurance_operations_dashboard.pdf)
> - 📊 [Download Native Power BI Workbook (.pbix)](data/insurance_operations_dashboard.pbix)

## 🛠️ Tech Stack & Architecture
- **Data Warehouse:** DuckDB / MotherDuck (Cloud Data Warehousing)
- **Data Mart:** SQL Transformation Pipelines (`mart.operations_payment_mart`)
- **Business Intelligence:** Power BI Desktop & DAX Modeling
- **Language:** SQL, DAX

## 📌 Project Key Features
- **Data Modeling & Mart Creation:** Engineered an operational payment mart in MotherDuck consolidating policy attributes, customer demographics, and transaction status.
- **DAX Metric Development:** Custom DAX measures implemented for dynamic KPI tracking, including Collection Paid Rate (`73.21%`), Total Revenue (`$291.83K`), and Total Policies Processed (`112`).
- **Interactive Visual Analytics:** Visualized payment frequency distributions, regional revenue concentrations across Canadian provinces, and product portfolio splits (Life vs. Annuity).

## 📊 Key Insights
- **Collection Efficiency:** The overall collection paid rate stands at **73.21%**, driven primarily by monthly policy plans.
- **Geographic Distribution:** Ontario represents the highest revenue contribution at **$76K**, followed by British Columbia at **$54K**.
- **Product Split:** Life insurance products constitute **57.14%** ($166.75K) of total portfolio revenue compared to Annuity products at **42.86%** ($125.08K).

## 📁 Repository Structure
