import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class StockAPI:
    def __init__(self):
        pass

    def get_realtime_price(self, ticker, exchange):
        """
        Get real-time stock price from Google Finance.
        :param ticker: Stock ticker symbol
        :param exchange: Stock exchange (e.g., NSE, BOM)
        :return: Current stock price
        """
        url = f'https://www.google.com/finance/quote/{ticker}:{exchange}'
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            class1 = "YMlKec fxKbKc"
            price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
            return price
        except Exception as e:
            print(f"Error fetching real-time price for {ticker}:{exchange} - {str(e)}")
            return None

    def get_historical_data(self, tickers, start_date=None, end_date=None):
        """
        Get historical stock data from Yahoo Finance.
        :param tickers: List of stock tickers
        :param start_date: Start date in 'YYYY-MM-DD' format
        :param end_date: End date in 'YYYY-MM-DD' format
        :return: DataFrame with adjusted closing prices
        """
        if not end_date:
            end_date = datetime.today().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

        try:
            data = yf.download(tickers, start=start_date, end=end_date)['Adj Close'].dropna()
            return data
        except Exception as e:
            print(f"Error fetching historical data - {str(e)}")
            return None

    def calculate_features(self, data):
        """
        Calculate features from historical price data.
        :param data: DataFrame of historical prices
        :return: Dictionary of features
        """
        if data is None or data.empty:
            return None

        try:
            log_returns = np.log(data / data.shift(1)).dropna()
            features = {
                'Mean Return': log_returns.mean().to_dict(),
                'Volatility': log_returns.std().to_dict()
            }
            return features
        except Exception as e:
            print(f"Error calculating features - {str(e)}")
            return None

    def get_stock_analysis(self, tickers, exchange='', start_date=None, end_date=None):
        """
        Get comprehensive stock analysis including real-time and historical data.
        :param tickers: List of stock tickers
        :param exchange: Exchange for real-time data (optional)
        :param start_date: Start date for historical data
        :param end_date: End date for historical data
        :return: Dictionary containing real-time prices and historical analysis
        """
        result = {
            'real_time_prices': {},
            'historical_data': None,
            'features': None
        }

        # Get real-time prices if exchange is provided
        if exchange:
            for ticker in tickers:
                price = self.get_realtime_price(ticker, exchange)
                if price:
                    result['real_time_prices'][f"{ticker}:{exchange}"] = price

        # Get historical data and features
        historical_data = self.get_historical_data(tickers, start_date, end_date)
        if historical_data is not None:
            result['historical_data'] = historical_data
            result['features'] = self.calculate_features(historical_data)

        return result