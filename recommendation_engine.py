import pandas as pd
import numpy as np

def recommend_stocks(time_frame, existing_portfolio, stock_data):
    """
    Recommend stocks based on investment time frame and existing portfolio.
    :param time_frame: Investment horizon ('short', 'medium', 'long')
    :param existing_portfolio: List of tickers already in portfolio
    :param stock_data: Dictionary containing historical_data, features, and real_time_prices
    :return: Dictionary with recommended stocks and their scores
    """
    features = stock_data.get('features', {})
    historical_data = stock_data.get('historical_data')
    real_time_prices = stock_data.get('real_time_prices', {})
    
    if not features or not historical_data:
        raise ValueError("Insufficient data for making recommendations")
    
    # Convert features to DataFrame for easier manipulation
    feature_df = pd.DataFrame(features)
    
    # Calculate additional metrics
    returns = np.log(historical_data / historical_data.shift(1)).dropna()
    feature_df['Sharp Ratio'] = (feature_df['Mean Return'] - 0.02) / feature_df['Volatility']  # Assuming 2% risk-free rate
    feature_df['Price Momentum'] = historical_data.pct_change(periods=30).iloc[-1]  # 30-day momentum
    
    recommendations = {}
    
    if time_frame == 'short':
        # Short-term: High volatility, strong momentum, real-time price movement
        scores = (
            feature_df['Volatility'] * 0.4 +
            feature_df['Price Momentum'] * 0.4 +
            feature_df['Sharp Ratio'] * 0.2
        )
        confidence_threshold = 0.7
        
    elif time_frame == 'medium':
        # Medium-term: Balanced approach with momentum and sharp ratio
        scores = (
            feature_df['Sharp Ratio'] * 0.4 +
            feature_df['Price Momentum'] * 0.3 +
            (feature_df['Mean Return'] / feature_df['Volatility']) * 0.3
        )
        confidence_threshold = 0.6
        
    else:  # long-term
        # Long-term: Focus on consistent returns and lower volatility
        scores = (
            feature_df['Sharp Ratio'] * 0.5 +
            (feature_df['Mean Return'] / feature_df['Volatility']) * 0.3 +
            (1 / feature_df['Volatility']) * 0.2
        )
        confidence_threshold = 0.5
    
    # Normalize scores
    scores = (scores - scores.min()) / (scores.max() - scores.min())
    
    # Filter out existing portfolio and low confidence scores
    for ticker in scores.index:
        if ticker not in existing_portfolio and scores[ticker] >= confidence_threshold:
            recommendations[ticker] = {
                'score': round(float(scores[ticker]), 3),
                'metrics': {
                    'mean_return': round(float(feature_df.loc[ticker, 'Mean Return']), 4),
                    'volatility': round(float(feature_df.loc[ticker, 'Volatility']), 4),
                    'sharp_ratio': round(float(feature_df.loc[ticker, 'Sharp Ratio']), 2),
                    'momentum': round(float(feature_df.loc[ticker, 'Price Momentum']), 4)
                }
            }
            # Add real-time price if available
            for key, price in real_time_prices.items():
                if ticker in key:
                    recommendations[ticker]['current_price'] = price
    
    # Sort by score and get top 5
    recommendations = dict(sorted(recommendations.items(), 
                                key=lambda x: x[1]['score'], 
                                reverse=True)[:5])
    
    return recommendations
