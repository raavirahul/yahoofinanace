import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Title and Sidebar
st.title("Chart")
st.write("Source: Yahoo Finance (https://finance.yahoo.com/)")
st.write("Github from creator URl:https://github.com/raavirahul/yahoofinanace")
ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
ticker = st.selectbox("Select a ticker", ticker_list, index=45)

start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=360))
end_date = st.date_input("End date", datetime.today().date())
period_list = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
period = st.selectbox("Period", period_list, index=5)
interval_list = ['1d', '5d', '1wk', '1mo', '3mo']
interval = st.selectbox("Interval", interval_list)
chart_list = ['Candle', 'Line']
stock_chart = st.selectbox("Chart type", chart_list)

# Button
get = st.button("Get data", key="get")

# Download info 
stock_price = yf.download(ticker, period=period, interval=interval, start=start_date, end=end_date)

# Calculate 'color' column
stock_price['diff'] = stock_price['Close'] - stock_price['Open']
stock_price.loc[stock_price['diff'] >= 0, 'color'] = 'yellow'
stock_price.loc[stock_price['diff'] < 0, 'color'] = 'blue'

# Plots
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Candlestick(x=stock_price.index,
                             open=stock_price['Open'],
                             high=stock_price['High'],
                             low=stock_price['Low'],
                             close=stock_price['Close'],
                             name='Price'))
fig.add_trace(go.Scatter(x=stock_price.index,
                         y=stock_price['Close'].rolling(window=50).mean(),
                         marker_color='skyblue', name='MA 50 days'))
fig.add_trace(go.Bar(x=stock_price.index,
                     y=stock_price['Volume'],
                     name='Volume',
                     marker={'color': stock_price['color']}), secondary_y=True)
fig.update_layout(xaxis_rangeslider_visible=False,
                  autosize=False,
                  width=1000,
                  height=500,
                  margin=dict(l=50, r=10, b=50, t=50, pad=4))
fig.update_yaxes(range=[0, 5e9], secondary_y=True)
fig.update_yaxes(visible=False, secondary_y=True)

# Show chart
if get:
    st.plotly_chart(fig, use_container_width=True)
