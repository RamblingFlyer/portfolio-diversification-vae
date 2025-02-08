url1 = 'https://www.google.com/finance/quote/INFY:NSE'
url2 = 'https://www.google.com/finance/quote/500209:BOM'

import requests
from bs4 import BeautifulSoup
import time

def get_stock_price(ticker, exchange):
    url = f'https://www.google.com/finance/quote/{ticker}:{exchange}'
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"
        price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
        return price
    except Exception as e:
        print(f"Error fetching price for {ticker}:{exchange} - {str(e)}")
        return None

def main():
    print("\n=== Real-Time Stock Price Monitor ===\n")
    print("Enter stock details (press Enter twice to start monitoring):")
    print("Format: TICKER EXCHANGE (e.g., INFY NSE or 500209 BOM)")
    
    stocks = []
    while True:
        stock_input = input("> ").strip()
        if not stock_input:
            break
            
        try:
            ticker, exchange = stock_input.split()
            stocks.append((ticker.upper(), exchange.upper()))
        except ValueError:
            print("Invalid format! Please use: TICKER EXCHANGE")
    
    if not stocks:
        print("No stocks entered. Exiting...")
        return
        
    print("\nStarting price monitoring (Press Ctrl+C to stop)...\n")
    try:
        while True:
            print("\033[H\033[J", end="")  # Clear screen
            print(f"=== Stock Prices at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            
            for ticker, exchange in stocks:
                price = get_stock_price(ticker, exchange)
                if price is not None:
                    print(f"{ticker}:{exchange} - ₹{price:,.2f}")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()