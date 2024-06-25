import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(layout="wide")
# ESTIMATED_MARGIN = st.selectbox"Enter the Estimated margin", ("2000000", "5000000", "1000000", "7000000",
# "500000","30000000"))
ESTIMATED_MARGIN = st.text_input("Enter the Estimated margin")


def calculate_matrix(df):
    pnl = df['profit'].values
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
    max_loss_combine = f"{max_loss} ({max_loss_percentage} %)"

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

    strategies = [col for col in df.columns if col != "Date" and col != "Profit" and col != "profit" and col != "Day"]


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
            "Maximum losing streak",
            "No. of Strategies"
        ],
        "Value": [
            ESTIMATED_MARGIN,
            overall_profit_combined,
            max_drawdown_combined,
            max_profit_combine,
            max_loss_combine,
            round(win_per, 2),
            round(neg_per, 2),
            avg_day_profit_combine,
            avg_profit_days_combine,
            avg_loss_days_combine,
            round(expectancy, 2),
            round(return_mdd, 2),
            max_winning_streak,
            max_losing_streak,
            len(strategies)
        ]
    }
    return pd.DataFrame(results)


# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xlsm"])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file, sheet_name="Basket Result")

    # Create a new column 'profit'
    df["profit"] = df["Profit"]

    # Display column names for user to select (excluding 'Date' and 'Profit' for subtraction)
    selectable_columns = [col for col in df.columns if col != "Date" and col != "Profit" and col != "profit"
                          and col != "Day"]

    select_all = st.checkbox("Select all", value=selectable_columns)
    if select_all:
        selected_column = st.multiselect("Select a column to subtract from 'Profit':", selectable_columns,
                                         selectable_columns)
    else:
        selected_column = st.multiselect("Select a column to subtract from 'Profit':", selectable_columns)

    if selected_column:
        # Subtract the selected column's values from 'Profit'
        for column in selected_column:
            df["profit"] -= df[column]

        df = df.drop(selected_column, axis=1)

    # Display the 'profit' column
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Profits Based on Tags")
        st.dataframe(df[["Date", "profit"] + [col for col in df.columns if col not in ["Date", "profit", "Profit"]]],
                     width=1500)

    # Calculate metrics
    metrics_df = calculate_matrix(df)

    # 2024-06-11 16:37:01.130 Serialization of dataframe to Arrow table was unsuccessful due to:
    # ("Expected bytes, got a 'float' object", 'Conversion failed for column Value with type object').
    # Applying automatic fixes for column types to make the dataframe Arrow-compatible.
    # this error is solved by this
    metrics_df["Value"] = metrics_df["Value"].astype(str)

    with col2:
        # Display metrics in a table
        st.write("Summary")
        st.dataframe(metrics_df)
