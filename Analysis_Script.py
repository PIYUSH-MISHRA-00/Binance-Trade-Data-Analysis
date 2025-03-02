import pandas as pd
import numpy as np
import json, ast, os

# ----------------------------
# 1. Load the CSV File
# ----------------------------
file_path = "TRADES_CopyTr_90D_ROI.csv"
df_raw = pd.read_csv(file_path)
print("Columns in CSV:", df_raw.columns.tolist())

# Check that the base columns exist
for col in ["Port_IDs", "Trade_History"]:
    if col not in df_raw.columns:
        raise ValueError(f"Missing required column: {col}")

# ----------------------------
# 2. Extract Trade Details from Trade_History
# ----------------------------
def parse_trade_history(th, port_id):
    """
    Attempts to parse a trade history string into a Python object.
    Uses json.loads first; if that fails, tries replacing single quotes;
    finally, falls back to ast.literal_eval.
    """
    if not isinstance(th, str):
        return th
    try:
        return json.loads(th)
    except Exception as e:
        try:
            fixed_th = th.replace("'", '"')
            return json.loads(fixed_th)
        except Exception as e2:
            try:
                return ast.literal_eval(th)
            except Exception as e3:
                print(f"Error parsing trade history for Port_ID {port_id}: {e3}")
                return None

trade_rows = []
for idx, row in df_raw.iterrows():
    port_id = row["Port_IDs"]
    trade_history = row["Trade_History"]
    parsed_trades = parse_trade_history(trade_history, port_id)
    if parsed_trades is None:
        continue
    if isinstance(parsed_trades, list):
        for trade in parsed_trades:
            if isinstance(trade, dict):
                # Add the Port_ID to each trade record
                trade["Port_IDs"] = port_id
                trade_rows.append(trade)
            else:
                print(f"Unexpected trade format for Port_ID {port_id}: {trade}")
    else:
        print(f"Unexpected format for Trade_History of Port_ID {port_id}")

df_trades = pd.DataFrame(trade_rows)
print("Extracted trade details columns:", df_trades.columns.tolist())

# ----------------------------
# 3. Data Cleaning & Feature Engineering
# ----------------------------
# The required trade fields (as per the task) include:
# - A timestamp (or time)
# - side, positionSide, price, quantity, qty, realizedProfit
# Check for a timestamp: if "timestamp" is missing but "time" exists, rename it.
if "timestamp" not in df_trades.columns:
    if "time" in df_trades.columns:
        df_trades.rename(columns={"time": "timestamp"}, inplace=True)
    else:
        raise ValueError("No timestamp found in trade records.")

required_trade_columns = ["Port_IDs", "timestamp", "side", "positionSide", "price", "quantity", "qty", "realizedProfit"]
for col in required_trade_columns:
    if col not in df_trades.columns:
        raise ValueError(f"Missing required trade column: {col}")

# Convert timestamp to datetime
df_trades["timestamp"] = pd.to_datetime(df_trades["timestamp"], errors="coerce")
df_trades.dropna(subset=["Port_IDs", "timestamp", "side", "positionSide", "price", "quantity", "qty", "realizedProfit"], inplace=True)

# Standardize text columns
df_trades["side"] = df_trades["side"].str.lower()
df_trades["positionSide"] = df_trades["positionSide"].str.lower()

# Create a new column "tradeType" (e.g., "buy_open" or "sell_close")
# Here we use side and positionSide, but if an "activeBuy" column is available, we can further differentiate open/close.
df_trades["tradeType"] = df_trades["side"] + "_" + df_trades["positionSide"]

# If "activeBuy" exists, use it to define a position status: open (True) vs. close (False).
if "activeBuy" in df_trades.columns:
    df_trades["positionStatus"] = df_trades["activeBuy"].apply(lambda x: "open" if x else "close")
else:
    # Otherwise, assume all trades represent complete positions.
    df_trades["positionStatus"] = "close"

# Also, classify trade outcomes based on realizedProfit.
df_trades["tradeOutcome"] = df_trades["realizedProfit"].apply(lambda x: "win" if x > 0 else ("loss" if x < 0 else "breakeven"))

# ----------------------------
# 4. Calculate Financial Metrics per Account
# ----------------------------
account_metrics = []
for port_id, group in df_trades.groupby("Port_IDs"):
    group = group.sort_values(by="timestamp")
    
    # Total PnL: Sum of realizedProfit for closing trades (assuming only closed positions yield realized profit)
    pnl = group[group["positionStatus"]=="close"]["realizedProfit"].sum()
    
    # Invested Capital: Sum of quantity for opening trades (if available)
    invested_capital = group[group["positionStatus"]=="open"]["quantity"].sum()
    
    # ROI: PnL divided by invested capital (if invested capital > 0)
    roi = pnl / invested_capital if invested_capital > 0 else np.nan
    
    # Sharpe Ratio: Compute trade returns for closing trades.
    valid = group[group["positionStatus"]=="close"]
    valid = valid[valid["quantity"] != 0]
    if len(valid) > 1 and valid["realizedProfit"].std() != 0:
        trade_returns = valid["realizedProfit"] / valid["quantity"]
        sharpe = trade_returns.mean() / trade_returns.std()
    else:
        sharpe = np.nan
    
    # Maximum Drawdown (MDD): Compute from the cumulative PnL of closing trades.
    valid = group[group["positionStatus"]=="close"].sort_values(by="timestamp")
    cum_pnl = valid["realizedProfit"].cumsum()
    running_max = cum_pnl.cummax()
    drawdown = running_max - cum_pnl
    mdd = drawdown.max() if not drawdown.empty else np.nan
    
    # Win Positions and Win Rate: Count closing trades with positive realizedProfit.
    win_positions = (group[group["positionStatus"]=="close"]["realizedProfit"] > 0).sum()
    total_positions = len(group[group["positionStatus"]=="close"])
    win_rate = win_positions / total_positions if total_positions > 0 else np.nan
    
    account_metrics.append({
        "Port_IDs": port_id,
        "PnL": pnl,
        "InvestedCapital": invested_capital,
        "ROI": roi,
        "SharpeRatio": sharpe,
        "MDD": mdd,
        "WinPositions": win_positions,
        "TotalPositions": total_positions,
        "WinRate": win_rate
    })

metrics_df = pd.DataFrame(account_metrics)

# ----------------------------
# 5. Ranking Accounts Based on Metrics
# ----------------------------
def min_max_norm(series):
    if series.max() == series.min():
        return series
    return (series - series.min()) / (series.max() - series.min())

metrics_df["norm_ROI"] = min_max_norm(metrics_df["ROI"])
metrics_df["norm_PnL"] = min_max_norm(metrics_df["PnL"])
metrics_df["norm_Sharpe"] = min_max_norm(metrics_df["SharpeRatio"])
metrics_df["norm_WinRate"] = min_max_norm(metrics_df["WinRate"])
# For MDD, lower is better so we invert the normalized value.
metrics_df["norm_MDD"] = 1 - min_max_norm(metrics_df["MDD"])

# Define weights for the composite score:
# ROI: 25%, PnL: 25%, Sharpe Ratio: 20%, Win Rate: 20%, Inverted MDD: 10%
metrics_df["Score"] = (
    0.25 * metrics_df["norm_ROI"] +
    0.25 * metrics_df["norm_PnL"] +
    0.20 * metrics_df["norm_Sharpe"] +
    0.20 * metrics_df["norm_WinRate"] +
    0.10 * metrics_df["norm_MDD"]
)

metrics_df.sort_values(by="Score", ascending=False, inplace=True)
top_20 = metrics_df.head(20)

# ----------------------------
# 6. Save the Results to CSV Files
# ----------------------------
account_metrics_path = "Account_Metrics.csv"
top_20_path = "Top_20_Accounts.csv"
metrics_df.to_csv(account_metrics_path, index=False)
top_20.to_csv(top_20_path, index=False)

print("Analysis Complete!")
print("Full account metrics saved to:", account_metrics_path)
print("Top 20 accounts saved to:", top_20_path)
