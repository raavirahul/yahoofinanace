# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 20:42:20 2023

@author: Source
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def render_tab5():
    """
    This function renders Tab 5 - Chart of the dashboard.
    """
    st.title("Monte Carlo Simulation")
    st.write("Source: Yahoo Finance (https://finance.yahoo.com/)")
    st.write("Github from creator URl:https://github.com/raavirahul/yahoofinanace")


    # Get user inputst.title("Stock Price Line Chart")
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    ticker = st.selectbox("Enter Stock Symbol (e.g., AAPL):", ticker_list)
    start_date = st.date_input("Select Start Date:", datetime(2020, 1, 1))
    end_date = st.date_input("Select End Date:", datetime.today())

    # Get stock data using the cache_data decorator
    @st.cache_data
    def GetStockData(ticker, start_date, end_date):
        stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        stock_df.reset_index(inplace=True)
        stock_df['Date'] = stock_df['Date'].dt.date
        return stock_df

    # Get stock data
    stock_data = GetStockData(ticker, start_date, end_date)

    # Check if stock_data is not empty
    if not stock_data.empty:
        # Perform Monte Carlo Simulation
        st.subheader("Monte Carlo Simulation")
        
        # Number of simulations
        num_simulations = st.selectbox("Number of Simulations", [200, 500, 1000])

        # Time horizon for simulation in days
        time_horizon = st.selectbox("Time Horizon (Days)", [30, 60, 90])

        # Calculate daily returns
        daily_returns = stock_data['Close'].pct_change().dropna()

        # Calculate mean and standard deviation of daily returns
        mean_return = daily_returns.mean()
        std_return = daily_returns.std()

        # Run Monte Carlo Simulation
        simulations = np.random.normal(loc=mean_return, scale=std_return, size=(time_horizon, num_simulations))
        price_simulations = stock_data['Close'].iloc[-1] * (1 + np.cumsum(simulations, axis=0))

        # Plot simulation results
        st.line_chart(price_simulations)
        
    # Estimate and present the Value at Risk (VaR) at 95% confidence interval
        st.subheader('Value at Risk (VaR)')
        ending_price = price_simulations[-1, :]
        fig1, ax = plt.subplots(figsize=(15, 10))
        ax.hist(ending_price, bins=50)
        plt.axvline(np.percentile(ending_price, 5), color='red', linestyle='--', linewidth=1)
        plt.legend(['5th Percentile of the Future Price: ' + str(np.round(np.percentile(ending_price, 5), 2))])
        plt.title('Distribution of the Ending Price')
        plt.xlabel('Price')
        plt.ylabel('Frequency')
        st.pyplot(fig1)

        future_price_95ci = np.percentile(ending_price, 5)
        # Value at Risk
        VaR = stock_data['Close'].iloc[-1] - future_price_95ci
        st.write('VaR at 95% confidence interval is: ' + str(np.round(VaR, 2)) + ' USD')

    else:
        st.warning("No data available for the selected stock and duration.")

if __name__ == "__main__":
    render_tab5()
