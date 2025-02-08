import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from data_preprocessing import fetch_stock_data, preprocess_data
from vae_model import build_vae
from recommendation_engine import recommend_stocks
from stock_api import StockAPI
from sklearn.cluster import KMeans
from datetime import datetime, timedelta

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Page configuration
st.set_page_config(
    page_title="💼 Stock Portfolio Manager 📊",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styles with dark theme
st.markdown("""
    <style>
        .stApp {
            background: #0f0f0f;
            font-family: 'Arial', sans-serif;
            color: #e0e0e0;
        }
        .title {
            color: #ffffff;
            font-size: 2.5em;
            text-align: center;
            font-weight: bold;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            border-radius: 15px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: rgba(26, 26, 26, 0.95);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid #34e89e;
        }
        .stTextInput input {
            background-color: #2d3436;
            color: #ffffff;
            border: 1px solid #34e89e;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton>button {
            background: linear-gradient(135deg, #0f3443, #34e89e);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 232, 158, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Login Page
if not st.session_state.authenticated:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #34e89e; margin-bottom: 30px;'>🔐 Stock Portfolio Manager</h1>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("🚀 Login", use_container_width=True):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Stop execution here if not authenticated

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'stock_search'
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Custom styles with dark theme
st.markdown("""
    <style>
        .stApp {
            background: #0f0f0f;
            font-family: 'Arial', sans-serif;
            color: #e0e0e0;
        }
        .title {
            color: #ffffff;
            font-size: 2.5em;
            text-align: center;
            font-weight: bold;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            border-radius: 15px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }
        .sidebar .sidebar-content {
            background-color: #1f1f1f;
            padding: 20px;
            border-radius: 10px;
        }
        .stock-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #34e89e;
            margin: 10px 0;
            transition: transform 0.3s ease;
        }
        .stock-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(52, 232, 158, 0.2);
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: rgba(26, 26, 26, 0.95);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid #34e89e;
        }
        .stTextInput input {
            background-color: #2d3436;
            color: #ffffff;
            border: 1px solid #34e89e;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton>button {
            background: linear-gradient(135deg, #0f3443, #34e89e);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 232, 158, 0.3);
        }
        .section-title {
            color: #34e89e;
            font-size: 1.5em;
            margin: 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #34e89e;
        }
    </style>
""", unsafe_allow_html=True)

# Login Page
if not st.session_state.authenticated:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #34e89e; margin-bottom: 30px;'>🔐 Stock Portfolio Manager</h1>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("🚀 Login", use_container_width=True):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials!")
    st.markdown("</div>", unsafe_allow_html=True)

# Main Dashboard (only shown when authenticated)
if st.session_state.authenticated:
    # Title
    st.markdown("<div class='title'>💼 Stock Portfolio Manager</div>", unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.header("📱 Navigation")
    views = ['Stock Search', 'Portfolio Management', 'Stock Analysis']
    st.session_state.current_view = st.sidebar.radio("Select View", views)
    
    if st.session_state.current_view == 'Stock Search':
        st.markdown("<h2 class='section-title'>🔍 Stock Search & Real-time Prices</h2>", unsafe_allow_html=True)
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)")
        exchange = st.selectbox("Select Exchange", ['NSE', 'BOM', ''])
        
        if st.button("Get Real-time Price", use_container_width=True):
            if ticker:
                try:
                    api = StockAPI()
                    price = api.get_realtime_price(ticker.strip().upper(), exchange)
                    if price:
                        st.markdown(f"""
                        <div class='stock-card'>
                            <h3>{ticker.upper()} : {exchange}</h3>
                            <h2 style='color: #34e89e'>₹ {price:.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Unable to fetch price. Please check the ticker and exchange.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    elif st.session_state.current_view == 'Portfolio Management':
        st.markdown("<h2 class='section-title'>📊 Portfolio & Watchlist Management</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Initialize StockAPI instance once for both portfolio and watchlist
        api = StockAPI()
        
        with col1:
            st.markdown("<h3 style='color: #34e89e'>💼 Your Portfolio</h3>", unsafe_allow_html=True)
            
            # Stock search and selection
            exchange = st.selectbox("Select Exchange", ['NSE', 'BSE'], key='portfolio_exchange')
            search_query = st.text_input("🔍 Search company by name or symbol", key='company_search')
            
            if search_query:
                try:
                    price = api.get_realtime_price(search_query.strip().upper(), exchange)
                    
                    if price:
                        st.markdown(f"""<div class='stock-card'>
                            <h4>{search_query.upper()}</h4>
                            <p style='color: #34e89e'>Current Price: ₹ {price:.2f}</p>
                        </div>""", unsafe_allow_html=True)
                        
                        if st.button("➕ Add to Portfolio", key='add_searched_stock'):
                            if search_query.upper() not in st.session_state.portfolio:
                                st.session_state.portfolio.append(search_query.upper())
                                st.success(f"✅ {search_query.upper()} added to portfolio!")
                                st.rerun()
                    else:
                        st.warning("Unable to fetch price. Please verify the symbol and exchange.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.write("Current Portfolio:")
            for stock in st.session_state.portfolio:
                col1_1, col1_2 = st.columns([3, 1])
                with col1_1:
                    try:
                        price = api.get_realtime_price(stock, exchange)
                        if price:
                            st.markdown(f"""<div class='stock-card'>
                                <h4>{stock}</h4>
                                <p style='color: #34e89e'>Current Price: ₹ {price:.2f}</p>
                            </div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""<div class='stock-card'>
                            <h4>{stock}</h4>
                            <p style='color: #ff4444'>Unable to fetch price</p>
                        </div>""", unsafe_allow_html=True)
                with col1_2:
                    if st.button("🗑️", key=f"del_port_{stock}"):
                        st.session_state.portfolio.remove(stock)
                        st.rerun()
        
        with col2:
            st.markdown("<h3 style='color: #34e89e'>👀 Your Watchlist</h3>", unsafe_allow_html=True)
            watch_stock = st.text_input("Add stock to watchlist")
            if watch_stock:
                try:
                    price = api.get_realtime_price(watch_stock.strip().upper(), exchange)
                    if price:
                        st.markdown(f"""<div class='stock-card'>
                            <h4>{watch_stock.upper()}</h4>
                            <p style='color: #34e89e'>Current Price: ₹ {price:.2f}</p>
                        </div>""", unsafe_allow_html=True)
                        
                        if st.button("Add to Watchlist") and watch_stock:
                            if watch_stock.upper() not in st.session_state.watchlist:
                                st.session_state.watchlist.append(watch_stock.upper())
                                st.success(f"✅ {watch_stock.upper()} added to watchlist!")
                    else:
                        st.warning("Unable to fetch price. Please verify the symbol and exchange.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.write("Current Watchlist:")
            for stock in st.session_state.watchlist:
                col2_1, col2_2 = st.columns([3, 1])
                with col2_1:
                    try:
                        price = api.get_realtime_price(stock, exchange)
                        if price:
                            st.markdown(f"""<div class='stock-card'>
                                <h4>{stock}</h4>
                                <p style='color: #34e89e'>Current Price: ₹ {price:.2f}</p>
                            </div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""<div class='stock-card'>
                            <h4>{stock}</h4>
                            <p style='color: #ff4444'>Unable to fetch price</p>
                        </div>""", unsafe_allow_html=True)
                with col2_2:
                    if st.button("🗑️", key=f"del_watch_{stock}"):
                        st.session_state.watchlist.remove(stock)
                        st.rerun()
    
    elif st.session_state.current_view == 'Stock Analysis':
        st.markdown("<h2 class='section-title'>📈 Stock Analysis & Recommendations</h2>", unsafe_allow_html=True)
        
        # Get stocks from portfolio and watchlist
        portfolio_tickers = st.session_state.portfolio
        watchlist_tickers = st.session_state.watchlist
        all_tickers = list(set(portfolio_tickers + watchlist_tickers))
        
        if not all_tickers:
            st.warning("⚠️ Please add stocks to your portfolio or watchlist first!")
        else:
            # Time frame selection
            time_frame = st.selectbox("⏳ Select Investment Time Frame", ['short', 'medium', 'long'])
            
            # Date inputs with default range
            col1, col2 = st.columns(2)
            with col1:
                default_start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
                start_date = st.date_input("📅 Start Date", value=datetime.strptime(default_start_date, '%Y-%m-%d'))
            with col2:
                default_end_date = datetime.today().strftime('%Y-%m-%d')
                end_date = st.date_input("📅 End Date", value=datetime.strptime(default_end_date, '%Y-%m-%d'))
            
            # Fetch and analyze button
            if st.button("🚀 Analyze Portfolio", use_container_width=True):
                try:
                    with st.spinner("🪄 Analyzing your portfolio... Hold tight!"):
                        progress_bar = st.progress(0)
                        st.write("### Step 1/4: 📦 Fetching Stock Data...")
                        data = fetch_stock_data(all_tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                        progress_bar.progress(25)

                        if data is None or data.empty:
                            st.error("❌ No data received. Please check your tickers and date range.")
                        else:
                            st.write("### Step 2/4: 📊 Processing Financial Metrics...")
                            try:
                                log_returns, features = preprocess_data(data)
                                progress_bar.progress(50)

                                # Check if log_returns is valid before proceeding
                                if log_returns is None or log_returns.empty:
                                    st.error("❌ Could not calculate returns. Please check your data.")
                                    st.stop()
                            except ValueError as ve:
                                st.error(f"❌ {str(ve)}")
                                st.stop()
                            except Exception as e:
                                st.error(f"❌ Error processing data: {str(e)}")
                                st.stop()

                            features_df = pd.DataFrame.from_dict(features, orient='index').T
                            features_df.index = data.columns
                            st.session_state.features_df = features_df

                            feature_array = np.column_stack([
                                features_df['Mean Return'].values,
                                features_df['Volatility'].values
                            ])

                            st.write("### Step 3/4: 🤖 Training Variational Autoencoder (VAE)...")
                            vae, encoder = build_vae(input_dim=feature_array.shape[1])
                            vae.fit(feature_array, feature_array, epochs=50, batch_size=16, validation_split=0.1)
                            progress_bar.progress(75)

                            latent_space = encoder.predict(feature_array)

                            # Clustering
                            st.write("### Step 4/4: 🔍 Clustering Assets in Latent Space...")
                            kmeans = KMeans(n_clusters=3, random_state=42)
                            clusters = kmeans.fit_predict(latent_space)
                            features_df['Cluster'] = clusters

                            # Visualization
                            st.write("### 🎨 Portfolio Diversification in Latent Space")
                            plt.figure(figsize=(10, 7))
                            sns.scatterplot(x=latent_space[:, 0], y=latent_space[:, 1], hue=clusters, palette='viridis', s=100)
                            for i, ticker in enumerate(features_df.index):
                                plt.text(latent_space[i, 0], latent_space[i, 1], ticker, fontsize=10, fontweight='bold')
                            plt.title("📈 Asset Clusters in Latent Space", fontsize=16, color="#ff7043")
                            st.pyplot(plt)

                            # Generate recommendations
                            stock_data = {
                                'features': features_df.to_dict(),
                                'historical_data': data,
                                'real_time_prices': {}
                            }
                            recommendations = recommend_stocks(time_frame, portfolio_tickers, stock_data)
                            st.write(f"### 📊 Recommended Stocks for a **{time_frame.capitalize()}-term Investment** 🏆")
                            st.dataframe(recommendations)

                            st.balloons()
                            st.success("✅ Analysis complete!")
                            progress_bar.progress(100)
                except Exception as e:
                    st.error(f"❗ Oops! Something went wrong: {str(e)}")

    # Remove redundant sidebar components and stock analysis code
    st.sidebar.header("⚙️ Customize Your Experience")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()