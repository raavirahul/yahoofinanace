import yfinance as yf
import streamlit as st


# Decorator to cache the data and avoid reloading it every time the script runs
@st.cache(allow_output_mutation=True)
def get_stock_info(ticker):
    stock_info = yf.Ticker(ticker)
    return stock_info

def display_financials(stock_info, title, financial_type):
    st.markdown(f'**{title}**')

    financials = None
    # Access the financial data using the yfinance methods
    try:
        if financial_type == 'earnings':
            financials = stock_info.earnings  # Historical earnings data
        elif financial_type == 'revenue':
            financials = stock_info.quarterly_financials  # Quarterly financial data
        else:
            st.write(f"No financial type named {financial_type} found.")
            return

        if financials is not None and not financials.empty:
            st.table(financials)
        else:
            st.write(f"No data available for {financial_type}.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    st.set_page_config(layout="wide")
    st.title("Stock Analysis")
    ticker = st.selectbox("Select Stock Ticker", ['AAPL', 'GOOGL', 'AMZN', 'MSFT'], index=0)  # Add more tickers as needed

    if ticker:
        stock_info = get_stock_info(ticker)
        
        # Attempt to display earnings and revenue

        display_financials(stock_info, 'Quarterly Financials', 'revenue')
    
# Run the main function
main()