![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

📊 Binance Trade Data Analysis
==============================

📌 Overview
-----------

This project analyzes Binance trade data to evaluate account performance based on key financial metrics. The dataset (`TRADES_CopyTr_90D_ROI.csv`) contains account identifiers (`Port_IDs`) and trade history stored as JSON-like strings. The analysis extracts, cleans, and processes this data to generate performance insights and rankings.

📂 Dataset
----------

Download the dataset from the following link:

🔗 [Binance Trade Dataset](https://drive.google.com/drive/folders/1ioZ56B5-zTmFuPrT7IihjOVozAgrXxhl?usp=sharing)

### 🔄 How to Use the Dataset

*   Download the dataset (`TRADES_CopyTr_90D_ROI.csv`) from the provided link.
*   Place the file in the project directory, alongside the analysis script.
*   The script will automatically process the file and generate structured output.

🔍 Features
-----------

*   **Data Parsing & Cleaning**: Converts trade history from JSON-like strings into structured data.
*   **Feature Engineering**: Standardizes text fields, categorizes trades, and derives key financial indicators.
*   **Financial Metrics Calculation**: Computes ROI, PnL, Sharpe Ratio, Maximum Drawdown (MDD), and Win Rate.
*   **Ranking Algorithm**: Uses a weighted composite score to rank accounts based on performance.
*   **Result Export**: Generates CSV files (`Account_Metrics.csv` & `Top_20_Accounts.csv`) for further analysis.

📊 Methodology
--------------

### 1️⃣ Data Extraction & Cleaning

*   Parses the `Trade_History` column (JSON-like string) into structured trade records.
*   Converts timestamps, standardizes text fields (`side`, `positionSide`), and filters essential trade data.

### 2️⃣ Feature Engineering

*   Creates new features like `tradeType`, `positionStatus`, and `tradeOutcome`.
*   Classifies trades into categories (`win`, `loss`, `breakeven`) based on `realizedProfit`.

### 3️⃣ Financial Metrics Calculation

*   **ROI (Return on Investment):** `PnL / Invested Capital`
*   **PnL (Profit & Loss):** Sum of `realizedProfit` from closing trades.
*   **Sharpe Ratio:** Trade-level returns to assess risk-adjusted performance.
*   **Maximum Drawdown (MDD):** Measures peak-to-trough loss in PnL.
*   **Win Rate:** Percentage of profitable trades.

### 4️⃣ Ranking Algorithm

*   Normalizes financial metrics and applies weighted scoring:

*   ROI (25%)
*   PnL (25%)
*   Sharpe Ratio (20%)
*   Win Rate (20%)
*   Inverted MDD (10%)

*   The top 20 accounts are selected based on composite ranking.

### 5️⃣ Output Deliverables

*   `Account_Metrics.csv` – Full financial metrics for all accounts.
*   `Top_20_Accounts.csv` – Top-performing accounts based on composite score.

🛠️ How to Run
--------------

1.  Clone the repository:
    
        git clone https://github.com/PIYUSH-MISHRA-00/Binance-Trade-Data-Analysis.git
        cd Binance-Trade-Data-Analysis
    
2.  Install dependencies:
    
        pip install -r requirements.txt
    
3.  Download the dataset and place it in the project directory.
4.  Run the script:
    
        python Analysis_Script.py
    
5.  Check the output CSV files in the results directory.

🎯 Expected Results
-------------------

*   A structured breakdown of each trade's financial impact.
*   Identification of top-performing accounts.
*   Insights into profitability, risk, and trading efficiency.

🏆 Use Case
-----------

This tool is useful for traders, analysts, and fund managers to evaluate trading performance, optimize strategies, and manage risk effectively.