import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import ta  # Technical Analysis library

# Streamlit App Title
st.title("📈 Trade Signal Generator Using Technical Indicators")

# Sidebar for user input
st.sidebar.header("Select Stock & Parameters")
ticker = st.sidebar.text_input("Enter Stock Ticker (Default: NIFTY 50)", "^NSEI")
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y"], index=1)

# Fetch Data
data = yf.Ticker(ticker).history(period=period)

if data.empty:
    st.error("No data available for the given stock.")
else:
    # Reset index for plotting
    data.reset_index(inplace=True)

    # Compute Moving Averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Compute Bollinger Bands
    std_dev = data['Close'].rolling(window=20).std()
    data['BB_Mid'] = data['SMA_20']
    data['BB_Upper'] = data['BB_Mid'] + (std_dev * 2)
    data['BB_Lower'] = data['BB_Mid'] - (std_dev * 2)

    # Compute RSI
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()

    # Compute MACD
    macd_indicator = ta.trend.MACD(data['Close'])
    data['MACD'] = macd_indicator.macd()
    data['MACD_Signal'] = macd_indicator.macd_signal()

    # Generate Buy/Sell Signals
    data['Buy_Signal'] = (data['Close'] < data['BB_Lower']) & (data['RSI'] < 40)
    data['Sell_Signal'] = (data['Close'] > data['BB_Upper']) & (data['RSI'] > 60)

    # 📊 Candlestick Chart
    fig = go.Figure()

    # Add Candlestick
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price",
        increasing_line_color='green', decreasing_line_color='red'
    ))

    # Add Indicators
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA_20'], mode='lines', name='SMA 20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='purple')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Upper'], mode='lines', name='Upper BB', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Lower'], mode='lines', name='Lower BB', line=dict(color='orange')))

    # Add Buy/Sell Signals
    fig.add_trace(go.Scatter(x=data['Date'][data['Buy_Signal']], y=data['Close'][data['Buy_Signal']],
                             mode='markers', name='Buy Signal', marker=dict(color='green', size=10, symbol='triangle-up')))
    fig.add_trace(go.Scatter(x=data['Date'][data['Sell_Signal']], y=data['Close'][data['Sell_Signal']],
                             mode='markers', name='Sell Signal', marker=dict(color='red', size=10, symbol='triangle-down')))

    # Layout Configurations
    fig.update_layout(
        title=f"Stock Price Chart for {ticker}",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )

    # Display the chart
    st.plotly_chart(fig)

    # 📌 Display Data with Signals
    st.subheader("📌 Latest Trade Signals")
    st.dataframe(data[['Date', 'Close', 'RSI', 'MACD', 'Buy_Signal', 'Sell_Signal']].tail(10))
