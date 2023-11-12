# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 14:16:57 2023

@author: Source
"""

###############################################################################
# FINANCIAL DASHBOARD EXAMPLE - v3
###############################################################################
#==============================================================================
# Initiating
#==============================================================================
# Libraries
import numpy as np
from PIL import Image
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.offline import iplot, init_notebook_mode
import yfinance as yf
import streamlit as st
from tkinter import ttk
import seaborn as sns
 

#==============================================================================
# HOT FIX FOR YFINANCE .INFO METHOD
# Ref: https://github.com/ranaroussi/yfinance/issues/1729
#==============================================================================

import requests
import urllib

class YFinance:
    user_agent_key = "User-Agent"
    user_agent_value = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/58.0.3029.110 Safari/537.36")
    
    def __init__(self, ticker):
        self.yahoo_ticker = ticker

    def __str__(self):
        return self.yahoo_ticker

    def _get_yahoo_cookie(self):
        cookie = None

        headers = {self.user_agent_key: self.user_agent_value}
        response = requests.get("https://fc.yahoo.com",
                                headers=headers,
                                allow_redirects=True)

        if not response.cookies:
            raise Exception("Failed to obtain Yahoo auth cookie.")

        cookie = list(response.cookies)[0]

        return cookie

    def _get_yahoo_crumb(self, cookie):
        crumb = None

        headers = {self.user_agent_key: self.user_agent_value}

        crumb_response = requests.get(
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
            headers=headers,
            cookies={cookie.name: cookie.value},
            allow_redirects=True,
        )
        crumb = crumb_response.text

        if crumb is None:
            raise Exception("Failed to retrieve Yahoo crumb.")

        return crumb

    @property
    def info(self):
        # Yahoo modules doc informations :
        # https://cryptocointracker.com/yahoo-finance/yahoo-finance-api
        cookie = self._get_yahoo_cookie()
        crumb = self._get_yahoo_crumb(cookie)
        info = {}
        ret = {}

        headers = {self.user_agent_key: self.user_agent_value}

        yahoo_modules = ("assetProfile,"  # longBusinessSummary
                         "summaryDetail,"
                         "financialData,"
                         "indexTrend,"
                         "defaultKeyStatistics")

        url = ("https://query1.finance.yahoo.com/v10/finance/"
               f"quoteSummary/{self.yahoo_ticker}"
               f"?modules={urllib.parse.quote_plus(yahoo_modules)}"
               f"&ssl=true&crumb={urllib.parse.quote_plus(crumb)}")

        info_response = requests.get(url,
                                     headers=headers,
                                     cookies={cookie.name: cookie.value},
                                     allow_redirects=True)

        info = info_response.json()
        info = info['quoteSummary']['result'][0]

        for mainKeys in info.keys():
            for key in info[mainKeys].keys():
                if isinstance(info[mainKeys][key], dict):
                    try:
                        ret[key] = info[mainKeys][key]['raw']
                    except (KeyError, TypeError):
                        pass
                else:
                    ret[key] = info[mainKeys][key]

        return ret
#==============================================================================
# # Header
# #============================================================================
def render_header():
    """
    This function render the header of the dashboard with the following items:
        - Title
        - Dashboard description
        - 3 selection boxes to select: Ticker, Start Date, End Date
    """
    # Add dashboard title and description
    st.title("Insight Analysis Dashboard📈")

    col1, col2 = st.columns([1,5])
    col1.write("Data source:")
    col2.image('./img/yahoo_finance.png', width=100)
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    # Renew is used to refresh page 
    renew = st.button("Refresh", key="Renew")
    # Add the selection boxes
    col1, col2, col3 = st.columns(3)  # Create 3 columns
    # Ticker name
    global ticker  # Set this variable as global, so the functions in all of the tabs can read it
    ticker = col1.selectbox("Ticker", ticker_list)
    # Begin and end dates
    global start_date, end_date  # Set this variable as global, so all functions can read it
    start_date = col2.date_input("Start date", datetime.today().date() - timedelta(days=30))
    end_date = col3.date_input("End date", datetime.today().date())
#==============================================================================
    
# Tab 1
#==============================================================================
def render_tab1():
    """
    This function render the Tab 1 - Company Profile of the dashboard.
    """
    # Show to stock image
    col1, col2, col3 = st.columns([1, 3, 1])
    col2.image('./img/stock_market.jpg', use_column_width=True,
              caption='Company Stock Information')
    # Get the company information
    @st.cache_data
    def GetCompanyInfo(ticker):
        """
        This function get the company information from Yahoo Finance.
        """
        return YFinance(ticker).info
    # If the ticker is already selected
    if ticker != '':
        # Get the company information in list format
        info = GetCompanyInfo(ticker)
        
        # Show the company description using markdown + HTML
        st.write('**1. Business Summary:**')
        st.markdown('<div style="text-align: justify;">' + \
                    info['longBusinessSummary'] + \
                    '</div><br>',
                    unsafe_allow_html=True)
        
        # Show some statistics as a DataFrame
        st.write('**2. Key Statistics:**')
        info_keys = {'previousClose':'Previous Close',
                     'open'         :'Open',
                     'bid'          :'Bid',
                     'ask'          :'Ask',
                     'marketCap'    :'Market Cap',
                     'volume'       :'Volume'}
        company_stats = {}  # Dictionary
        for key in info_keys:
            company_stats.update({info_keys[key]:info[key]})
        company_stats = pd.DataFrame({'Value':pd.Series(company_stats)}) 
        
        # change to dataframe
        st.dataframe(company_stats)
        
        
        # Show duration of time in different intervals
    st.write('**3. Duration:**')
    from datetime import datetime, timedelta
    def calculate_duration(start_date, end_date):
        delta = end_date - start_date
        return delta.days
    def get_duration_option(interval_option, current_date):
        if interval_option == "1M":
            start_date = current_date - timedelta(days=30)
        elif interval_option == "3M":
            start_date = current_date - timedelta(days=90)
        elif interval_option == "6M":
            start_date = current_date - timedelta(days=180)
        elif interval_option == "YTD":
            start_date = datetime(current_date.year, 1, 1)
        elif interval_option == "1Y":
            start_date = current_date - timedelta(days=365)
        elif interval_option == "3Y":
            start_date = current_date - timedelta(days=3*365)
        elif interval_option == "5Y":
            start_date = current_date - timedelta(days=5*365)
        elif interval_option == "MAX":
            start_date = datetime(1970,1,1)
        else:
            raise ValueError("Invalid interval option")
            if not isinstance(start_date, datetime):
                start_date = datetime.combine(start_date, datetime.min.time())
        return calculate_duration(start_date, current_date)
    


    
# Get stock data
    def get_stock_data(symbol, interval_option):
        current_date = datetime.now()
        duration_mapping = {
            "1M": 30, "3M": 90, "6M": 180,
            "YTD": (current_date - datetime(current_date.year, 1, 1)).days,
            "1Y": 365, "3Y": 3 * 365, "5Y": 5 * 365,
            "MAX": (current_date - datetime(1970, 1, 1)).days,
    }
        start_date = current_date - timedelta(days=duration_mapping.get(interval_option, 30))
        return yf.download(symbol, start=start_date, end=current_date, interval="1d")



# Calculate duration
     #Stock Chart
    def plot_stock_chart(stock_data, symbol, interval_option):
        fig = go.Figure()

    # Add line trace
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data["Close"], mode='lines', name='Stock Prices'))

    # Update layout
        fig.update_layout(
        title=f"{symbol} Stock Prices Over {interval_option} Duration",
        xaxis_title="date",
        yaxis_title="Stock Price in in(USD)"
    )

        return fig
    def main():
        st.title("Stock Price Line Chart")
        ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
        symbol = st.selectbox("Enter Stock Symbol (e.g., AAPL):", ticker_list)
        interval_option = st.selectbox("Select Duration 2", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "MAX"])
# Plot line chart
   # Get and display stock data
        stock_data = get_stock_data(symbol, interval_option)
    
        if stock_data.empty:
            st.warning("No data available for the selected symbol and duration.")
        else:
        # Plotly chart using graph_objects
            fig = plot_stock_chart(stock_data, symbol, interval_option)
        
        # Show the figure
            st.plotly_chart(fig)

    if __name__ == "__main__":
        main()
        
        
        
        # Show Description 
        # Show Major shareholders

#=====================================
#==============================================================================
# Tab 2
#=============================================================================
def render_tab2():
    """
    This function render the Tab 2 - Chart of the dashboard.
    """
    # Add table to show stock data
    @st.cache_data
    def GetStockData(ticker, start_date, end_date):
        stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        stock_df.reset_index(inplace=True)  # Drop the indexes
        stock_df['Date'] = stock_df['Date'].dt.date  # Convert date-time to date
        return stock_df
   

   


#==============================================================================
# Tab 3
#===========================================================================                

def render_tab3():
    """
    This function render the Tab 4 - Chart of the dashboard.
    """
    # Add table to show stock data
    @st.cache_data
    def GetStockData(ticker, start_date, end_date):
        stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        stock_df.reset_index(inplace=True)  # Drop the indexes
        stock_df['Date'] = stock_df['Date'].dt.date  # Convert date-time to date
        return stock_df
    #==============================================================================
    # Tab 4
    #=========================================================================
def render_tab4():
        """
        This function render the Tab 4 - Chart of the dashboard.
        """
        # Add table to show stock data
        @st.cache_data
        def GetStockData(ticker, start_date, end_date):
            stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
            stock_df.reset_index(inplace=True)  # Drop the indexes
            stock_df['Date'] = stock_df['Date'].dt.date  # Convert date-time to date
            return stock_df
    
    
    #==============================================================================
      # Tab 5
      #=========================================================================
    
def render_tab5():
        """
        This function render the Tab 5 - Analysis.
        """
        # Add table to show stock data
        @st.cache_data
        def GetStockData(ticker, start_date, end_date):
            stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
            stock_df.reset_index(inplace=True)  # Drop the indexes
            stock_df['Date'] = stock_df['Date'].dt.date  # Convert date-time to date
            return stock_df
                   
        
#==============================================================================
# Main body
#==============================================================================
# Render the header
render_header()
 
 # Render the tabs
tab1, tab2,tab3, tab4, tab5 = st.tabs(["Company profile", "Chart","Monte Carlo simulation","Finacials","stock Analysis"])
with tab1:
    render_tab1()
with tab2:
    render_tab2()
with tab3:
    render_tab3()
with tab4:
    render_tab4()
with tab5:
    render_tab5()
        
###############################################################################
# END
###############################################################################