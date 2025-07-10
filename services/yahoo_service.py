import yfinance as yf
from utils.logger import log_message, get_logs


def enrich_data(symbol):
    
    stock = yf.Ticker(symbol+".NS")
    hist = stock.history(period="1y")

    if hist.empty:
        log_message(f"No data found for {symbol}")
        return

    current_price = hist['Close'].iloc[-1]
    low_52_week = hist['Low'].min()

    dist_from_52week_low = ((current_price - low_52_week) / low_52_week) * 100

    #log_message(f"Stock: {symbol}")
    #log_message(f"Current Price: ₹{current_price:.2f}")
    #log_message(f"52-Week Low: ₹{low_52_week:.2f}")
    #log_message(f"% Above 52-Week Low: {dist_from_52week_low:.2f}%")

    return float(current_price), float(low_52_week), float(dist_from_52week_low)

def get_nasdaq_last_day_change():
    nasdaq = yf.Ticker("^IXIC")
    hist = nasdaq.history(period="5d").dropna()

    if len(hist) < 2:
        log_message("Not enough data to compare.")
        return None

    last_two = hist.tail(2)
    prev_close = last_two['Close'].iloc[0]
    last_close = last_two['Close'].iloc[1]

    percent_change = ((last_close - prev_close) / prev_close) * 100

    log_message(f"Previous Close: {prev_close:.2f}")
    log_message(f"Last Close: {last_close:.2f}")
    log_message(f"Change: {percent_change:+.2f}%")

    return percent_change, last_close

