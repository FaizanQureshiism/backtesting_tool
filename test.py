import streamlit as st
import pandas as pd
import numpy as np

# Define constants
# ESTIMATED_MARGIN = st.selectbox("Enter the Estimated margin", ("2000000", "5000000", "1000000", "7000000", "500000", "30000000"))
ESTIMATED_MARGIN = st.text_input("Enter the Estimated margin")

# Function to calculate metrics
def calculated_matrix(df):
    pnl = df['Profit'].values
    cumulative_pnl = np.cumsum(pnl)

    # Overall profit
    overall_profit = cumulative_pnl[-1]
    overall_profit_percentage = round((overall_profit / int(ESTIMATED_MARGIN)) * 100, 2)
    overall_profit_combined = f"{overall_profit} ({overall_profit_percentage} %)"

    # Drawn-down
    max_cumulative_pnl = np.maximum.accumulate(cumulative_pnl)
    drawdown = max_cumulative_pnl - cumulative_pnl
    max_drawdown = np.max(drawdown)
    max_drawdown_percentage = round((max_drawdown / int(ESTIMATED_MARGIN)) * 100, 2)
    max_drawdown_combined = f"{max_drawdown} ({max_drawdown_percentage} %)"

    # Max profit and loss
    max_profit = np.max(pnl)
    max_profit_percentage = round((max_profit / int(ESTIMATED_MARGIN)) * 100, 2)
    max_profit_combine = f"{max_profit} ({max_profit_percentage} %)"

    max_loss = np.min(pnl)
    max_loss_percentage = round((max_loss / int(ESTIMATED_MARGIN)) * 100, 2)
    max_loss_combin = f"{max_loss} ({max_loss_percentage} %)"

    # Average day Profit
    avg_day_profit = np.mean(pnl)
    avg_day_profit_round = np.round(avg_day_profit, 2)

    avg_day_profit_percentage = round((avg_day_profit_round / int(ESTIMATED_MARGIN)) * 100, 2)
    avg_day_profit_combine = f"{avg_day_profit_round} ({avg_day_profit_percentage} %)"

    # Win days and Loss days Percentage
    total = len(pnl)

    positive_days = pnl[pnl > 0]
    win_per = len(positive_days) / total * 100
    negative_days = pnl[pnl < 0]
    neg_per = len(negative_days) / total * 100

    # Max win and max loss by win days and loss days
    avg_profit_days = np.mean(positive_days) if len(positive_days) > 0 else 0
    avg_profit_days_round = np.round(avg_profit_days, 2)
    avg_profit_percentage = round((avg_profit_days_round / int(ESTIMATED_MARGIN)) * 100, 2)
    avg_profit_days_combine = f"{avg_profit_days_round} ({avg_profit_percentage} %)"

    avg_loss_days = np.mean(negative_days) if len(negative_days) > 0 else 0
    avg_loss_days_round = np.round(avg_loss_days, 2)
    avg_loss_percentage = round((avg_loss_days_round / int(ESTIMATED_MARGIN)) * 100, 2)
    avg_loss_days_combine = f"{avg_loss_days_round} ({avg_loss_percentage} %)"

    # Expectancy
    risk_reward_ratio = round(abs(avg_profit_days / avg_loss_days), 2)
    risk_reward_win = round(risk_reward_ratio * (win_per / 100), 2)
    expectancy = risk_reward_win - (neg_per / 100)

    # Return to MDD
    df["Date"] = pd.to_datetime(df["Date"])

    total_months = df["Date"].dt.to_period('M').nunique()

    total_years = total_months / 12
    total_yearly_profit = overall_profit / total_years
    
    return_mdd = total_yearly_profit / max_drawdown

    # Maximum winning streak
    max_winning_streak = 0
    current_streak = 0
    for profit in pnl:
        if profit > 0:
            current_streak += 1
            if current_streak > max_winning_streak:
                max_winning_streak = current_streak
        else:
            current_streak = 0

    # Maximum losing streak
    max_losing_streak = 0
    current_streak = 0
    for profit in pnl:
        if profit < 0:
            current_streak += 1
            if current_streak > max_losing_streak:
                max_losing_streak = current_streak
        else:
            current_streak = 0

    # Prepare results as a dictionary
    results = {
        "Metric": [
            "Estimated Margin",
            "Overall Profit",
            "Max Drawdown",
            "Max Profit",
            "Max Loss",
            "Win Percentage",
            "Loss Percentage",
            "Average Day Profit",
            "Average Profit (Win Days  %)",
            "Average Loss (Loss Days  %)",
            "Expectancy",
            "Return to MDD",
            "Maximum winning streak",
            "Maximum losing streak"
        ],
        "Value": [
            ESTIMATED_MARGIN,
            overall_profit_combined,
            max_drawdown_combined,
            max_profit_combine,
            max_loss_combin,
            round(win_per, 2),
            round(neg_per, 2),
            avg_day_profit_combine,
            avg_profit_days_combine,
            avg_loss_days_combine,
            round(expectancy, 2),
            round(return_mdd, 2),
            max_winning_streak,
            max_losing_streak,
        ]
    }
    return pd.DataFrame(results)


# Streamlit app
uploaded_file = st.file_uploader("Enter your first excel file here:", type=["xlsx"], accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        file.seek(0)
    uploaded_data_read = [pd.read_excel(file, sheet_name="Basket Result") for file in uploaded_file]
    raw_data = pd.concat(uploaded_data_read)
    df = raw_data.sort_values(by="Date")

    col1, col2 = st.columns([2,2])
    with col1:
        st.write("After merging")
        st.dataframe(df[["Date", "Day", "Profit"]])

    # Calculate metrics
    metrics_df = calculated_matrix(df)
    metrics_df["Value"] = metrics_df["Value"].astype(str)

    with col2:
        # Display metrics in a table
        st.write("Summary")
        st.dataframe(metrics_df, width=800)
