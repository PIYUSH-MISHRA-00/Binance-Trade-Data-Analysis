![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Binance Trade Data Analysis Report
==================================

Methodology and Findings
------------------------

### 1\. Data Extraction and Cleaning

The dataset (`TRADES_CopyTr_90D_ROI.csv`) contains two primary columns: `Port_IDs` (unique account identifiers) and `Trade_History`. The `Trade_History` column stores a JSON‐like string representing a list of trade records.

*   A parsing function attempts to convert each `Trade_History` string into a list of dictionaries using `json.loads`, fixes for single quotes, and `ast.literal_eval` as a fallback.
*   The extracted trade records are flattened into a new DataFrame with one row per trade, with the associated `Port_IDs` added to each record.
*   The script then checks for required fields (e.g. `timestamp` or `time`, `side`, `positionSide`, `price`, `quantity`, `qty`, and `realizedProfit`) and converts the timestamp to a datetime object.

### 2\. Feature Engineering

Key text fields (`side` and `positionSide`) are standardized to lowercase. A new column `tradeType` is created by concatenating `side` and `positionSide`. Additionally, if an `activeBuy` column is present, it is used to derive a `positionStatus` (either `open` or `close`). Trades are also classified by outcome (`win`, `loss`, or `breakeven`) based on their `realizedProfit`.

### 3\. Financial Metrics Calculation

For each account (`Port_IDs`), the following metrics are computed:

*   **PnL (Profit and Loss):** Sum of `realizedProfit` from closing trades.
*   **Invested Capital:** Sum of `quantity` for opening trades (if available).
*   **ROI (Return on Investment):** Calculated as `PnL / Invested Capital` (if invested capital > 0).
*   **Sharpe Ratio:** Based on trade-level returns computed as `realizedProfit / quantity` for closing trades.
*   **Maximum Drawdown (MDD):** Derived from the cumulative PnL curve of closing trades.
*   **Win Positions and Win Rate:**
    *   `WinPositions`: Count of closing trades with a positive `realizedProfit`.
    *   `TotalPositions`: Total number of closing trades.
    *   `WinRate`: Ratio of win positions to total positions.

### 4\. Ranking Algorithm

The calculated metrics are first normalized using min–max normalization. Since a lower drawdown (MDD) is preferable, its normalized value is inverted. A composite score is then computed as a weighted sum of the normalized metrics:

*   ROI: 25%
*   PnL: 25%
*   Sharpe Ratio: 20%
*   Win Rate: 20%
*   Inverted MDD: 10%

Accounts are sorted by this composite score, and the top 20 accounts are selected.

### 5\. Output Deliverables

*   **Account\_Metrics.csv:** Contains full financial metrics for each account.
*   **Top\_20\_Accounts.csv:** Contains the top 20 accounts ranked by the composite score.

### 6\. Summary

This analysis framework enables a comprehensive evaluation of Binance account performance using detailed trade data. The modular approach (from parsing JSON to computing advanced metrics) allows for future adjustments and ensures accurate identification of top-performing accounts.

### 7\. How to Run and What to Expect

**How to Run:**

*   Place the CSV file `TRADES_CopyTr_90D_ROI.csv` in the same directory as the Python script.
*   Ensure that Python (with the required packages: `pandas` and `numpy`) is installed.
*   Run the script using a command like: `python Analysis_Script.py` (or run it within a Jupyter Notebook).

**What to Expect:**

*   The script will load the raw CSV and attempt to parse the `Trade_History` field into individual trade records.
*   It will perform data cleaning and feature engineering to extract necessary trade details (timestamp, side, positionSide, price, quantity, qty, realizedProfit).
*   It calculates financial metrics for each account including ROI, PnL, Sharpe Ratio, Maximum Drawdown (MDD), Win Positions, Total Positions, and Win Rate.
*   The script normalizes these metrics, computes a composite score, and ranks the accounts.
*   Two CSV files will be generated:
    *   `Account_Metrics.csv` – containing the full set of calculated metrics for each account.
    *   `Top_20_Accounts.csv` – containing the top 20 accounts based on the composite ranking.
*   Console output will indicate when the analysis is complete and where the CSV files have been saved.