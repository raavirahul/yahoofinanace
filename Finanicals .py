# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 01:52:34 2023

@author: Source
"""

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

def main():
    st.title("Financials")
    st.write("Source: Yahoo Finance (https://finance.yahoo.com/)")
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    st.write("Github from creator URL: https://github.com/raavirahul/yahoofinance")

 # Select Ticker
    ticker = st.selectbox("Select Stock Ticker", ticker_list)
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

    # Render data for each tab
    render_tab(tab1, ticker, "financials")


def get_financial_data(ticker, data_type, is_quarterly=False):
    if is_quarterly:
        financial_data = getattr(yf.Ticker(ticker), f'quarterly_{data_type}')
    else:
        financial_data = getattr(yf.Ticker(ticker), data_type)

    financial_data = financial_data.rename(lambda t: t.strftime('%Y-%m-%d'), axis='columns')
    financial_data = financial_data.astype(float).apply(np.floor)
    return financial_data

def render_tab(tab_name, ticker, data_type):
    tabA, tabB = st.tabs(["Annually", "Quarterly"])
    with tab_name:
        with tabA:
            financial_data_a = get_financial_data(ticker, data_type)
            st.dataframe(financial_data_a.style.format(formatter='{:,.0f}'))
        with tabB:
            financial_data_q = get_financial_data(ticker, data_type, is_quarterly=True)
            st.dataframe(financial_data_q.style.format(formatter='{:,.0f}'))

if __name__ == "__main__":
    main()

