import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_api import StockAPI

def fetch_stock_data(tickers, exchange='', start_date=None, end_date=None):
    """
    Fetches stock data using StockAPI for given tickers.
    :param tickers: List of stock tickers.
    :param exchange: Stock exchange (e.g., NSE, BOM) for real-time data.
    :param start_date: Start date in the format 'YYYY-MM-DD' (optional).
    :param end_date: End date in the format 'YYYY-MM-DD' (optional).
    :return: DataFrame with stock data.
    """
    api = StockAPI()
    analysis = api.get_stock_analysis(tickers, exchange, start_date, end_date)
    return analysis['historical_data']

def preprocess_data(data):
    """
    Preprocesses stock data to compute log returns and features.
    :param data: DataFrame of stock adjusted close prices.
    :return: Tuple (log_returns, features dictionary).
    """
    # Handle potential empty or invalid data
    if data is None or data.empty:
        raise ValueError("Input data is empty")
        
    log_returns = np.log(data / data.shift(1)).dropna()
    features = {
        'Mean Return': log_returns.mean().to_dict(),
        'Volatility': log_returns.std().to_dict()
    }
    return log_returns, features

# Main execution
if __name__ == "__main__":
    tickers = input("Enter stock tickers (comma-separated, e.g., AAPL, MSFT): ").split(',')
    tickers = [ticker.strip().upper() for ticker in tickers]
    exchange = input("Enter exchange (e.g., NSE, BOM) or press Enter to skip: ").strip().upper()
    print("Fetching data for tickers:", tickers)
    
    try:
        # Fetch data
        historical_data, features, real_time_prices = fetch_stock_data(tickers, exchange)
        
        # Display real-time prices if available
        if real_time_prices:
            print("\nReal-time Prices:")
            for ticker_exchange, price in real_time_prices.items():
                print(f"{ticker_exchange}: {price}")
        
        if historical_data is not None:
            # Process historical data
            log_returns, calc_features = preprocess_data(historical_data)
            
            # Display results
            print("\nLog Returns:")
            print(log_returns.head())
            
            print("\nFeatures:")
            for key in features:
                for ticker, value in features[key].items():
                    print(f"{ticker} - {key}: {value:.6f}")
                    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

