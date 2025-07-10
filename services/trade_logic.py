
import pandas as pd
import yfinance as yf
import pandas as pd
from dotenv import dotenv_values
from services import dhan_service
from services import yahoo_service
from tabulate import tabulate
from datetime import datetime, timedelta
from utils.logger import log_message, get_logs



config = dotenv_values("config/config.properties")

MAX_AMOUNT_DAILY_ETF = float(config.get("MAX_AMOUNT_DAILY_ETF"))
MAX_AMOUNT_NASDAQ = float(config.get("MAX_AMOUNT_NASDAQ"))
MAX_AMOUNT_LONGTERM = float(config.get("MAX_AMOUNT_LONGTERM"))

def find_max_loss_today(prices):
    # Placeholder for max loss logic
    return prices[0]  # Simplified

def evaluate_and_buy_etf_daily_strategy(df_etfs, df_holdings):
    sorted_etfs = df_etfs.sort_values(by='dist_from_52week_low')
    log_message("----------- sorted_etfs --------------")
    log_message(sorted_etfs.head(10))

    buy_executed = False  # ✅ Flag to track if a buy has been placed

    # log_message("----------- df_holdings --------------")
    # log_message(df_holdings)

    for _, row in sorted_etfs.head(10).iterrows():  
        symbol = row['SEM_TRADING_SYMBOL']
        cmp = row['current_price']
        security_id = row['SEM_SMST_SECURITY_ID']


               
        # Check if already in holdings
        if symbol in df_holdings['tradingSymbol'].values:
            log_message(f"{symbol} already in holdings. Checking averaging eligibility")

            if average_logic("etf",df_holdings[df_holdings['tradingSymbol'] == symbol]):
                #log_message(f"Buying {symbol} as it is eligible for averaging.")
                # ✅ Place buy logic here
                quantity = get_quantity(MAX_AMOUNT_DAILY_ETF)
                log_message(f"Buying {symbol} {security_id} quantity : {quantity} as it is eligible for averaging.")
                dhan_service.place_buy_order(security_id, quantity, cmp)
                buy_executed = True
                break
            else:
                profit_loss_percent = df_holdings[df_holdings['tradingSymbol'] == symbol]['change_percentage'].iloc[0]
                log_message(f"{symbol} is not eligible for averaging as its profit loss % is {profit_loss_percent}")
                continue  # ✅ Skip to next symbol
            
        # Buy if symbol is NOT in holdings
        else:
            log_message(f"Buying {symbol} as it is a fresh buy.")
            # ✅ Place buy logic here
            dhan_service.place_buy_order(security_id, get_quantity(MAX_AMOUNT_DAILY_ETF, cmp))
            buy_executed = True
            break  # ✅ # stop after 1 buy

    # ✅ Fallback logic only runs if no buy was executed
    if not buy_executed:
        # If no eligible buy happened in loop, fallback to first ETF
        log_message("⚠️ No ETF was eligible in top 10. Buying the first one as fallback.")
        fallback_row = sorted_etfs.iloc[0]
        symbol = fallback_row['SEM_TRADING_SYMBOL']
        cmp = fallback_row['current_price']
        security_id = fallback_row['SEM_SMST_SECURITY_ID']
        log_message(f"Buying {symbol} {security_id} quantity : {quantity} at price {cmp} as fallback")
        dhan_service.place_buy_order(security_id, get_quantity(MAX_AMOUNT_DAILY_ETF, cmp))

def evaluate_and_sell_etf_daily_strategy(df_holdings):
    #log_message("SELL logic started")
    
    df_holdings=add_price_data(df_holdings)
    sorted_holdings = df_holdings.sort_values(by='change_percentage', ascending=False )
    #sorted_holdings.to_csv('df_holdings_price.csv', index=False)

    sell_count = 0

    for _, row in sorted_holdings.iterrows():
        symbol = row['tradingSymbol'].strip().upper()
        security_id = row['securityId']
        quantity = row['availableQty']

        if symbol in config.get("LONG_TERM_ETFS"):
            log_message(f"Skipping sell for {symbol} \t -  Its in LONG_TERM_ETFS")
            continue
        
        # sale logic
        if(row['change_percentage'] > 6.28):
            log_message(f"Selling {symbol} as it's not in LONG_ETFS & profit % > 6.28")
            # write sell logic
            log_message(f"Selling {symbol} {security_id} quantity : {quantity}")
            res = dhan_service.place_sell_order(security_id, quantity)
            log_message(res)
            sell_count =  sell_count+1
            break
        else:
            log_message(f"Skipping sell for {symbol} \t —  profit is {round(row['change_percentage'], 4)}% which is below 6.28% threshold.")
    
    if(sell_count < 1):
            log_message("❌ No sell today on etf_daily_strategy")
        

def evaluate_etf(df_etf):

    for index, row in df_etf.iterrows():
        stock_details = yahoo_service.enrich_data(row['SEM_TRADING_SYMBOL'])
        #log_message(stock_details)
        current_price, low_52_week, dist_from_52week_low = stock_details
        df_etf.at[index, 'current_price'] = current_price
        df_etf.at[index, 'low_52_week'] = low_52_week
        df_etf.at[index, 'dist_from_52week_low'] = dist_from_52week_low

    return df_etf



def all_holdings():
    response = dhan_service.get_holdings()
    #log_message(response)
    
    # Convert list of dicts to DataFrame
    #df_holdings = pd.DataFrame(response) 
    # Check for errors in response
    if isinstance(response, dict) and 'errorCode' in response:
        log_message(f"❌ API Error: {response.get('errorCode')} - {response.get('internalErrorMessage', response.get('message'))}")
        df_holdings = pd.DataFrame()  # return empty DataFrame to avoid crash
    else:
        try:
            # Ensure response is a list of dicts
            if isinstance(response, list):
                df_holdings = pd.DataFrame(response)
            else:
                log_message("❌ Unexpected response format.")
                df_holdings = pd.DataFrame()
        except Exception as e:
            log_message(f"❌ Exception while parsing response: {e}")
            df_holdings = pd.DataFrame()

    return df_holdings

def enrich_holdings(df_holdings, df_etfs):
    # Ensure symbol columns are clean and matchable
    df_holdings['tradingSymbol'] = df_holdings['tradingSymbol'].str.strip().str.upper()
    df_etfs['SEM_TRADING_SYMBOL'] = df_etfs['SEM_TRADING_SYMBOL'].str.strip().str.upper()

    # Merge on trading symbol
    merged_df = pd.merge(
        df_holdings,
        df_etfs[['SEM_TRADING_SYMBOL', 'current_price', 'low_52_week', 'dist_from_52week_low']],
        left_on='tradingSymbol',
        right_on='SEM_TRADING_SYMBOL',
        how='left'
    )

    # Calculate change_percentage and loss_gain_amt
    merged_df['change_percentage'] = 100 *(merged_df['current_price'] - merged_df['avgCostPrice']) / merged_df['avgCostPrice']
    merged_df['loss_gain_amt'] = (merged_df['current_price'] - merged_df['avgCostPrice']) * merged_df['totalQty']

    # Optional: round the new columns
    merged_df['change_percentage'] = merged_df['change_percentage'].round(4)
    merged_df['loss_gain_amt'] = merged_df['loss_gain_amt'].round(2)

    merged_df = merged_df.sort_values(by='change_percentage')
    return merged_df

def average_logic(type, df):
     # Check if loss is > 3.14% and not recently added. If yes buy
    # Not implemented the code till now
    if(df['change_percentage'].iloc[0] < -3.14):
        return True
    else:
        return False

def get_quantity(max_amount, currentPrice):
    
    max_total_amount = int(max_amount) * 1.1
    quantity = int(max_amount / currentPrice)

    if((currentPrice * (quantity+1)) < max_total_amount):
        quantity = quantity + 1

    return quantity

def evaluate_and_buy_etf_nasdaq_strategy(change, last_close):
    if change is not None:
        if change > 1.49:
            
            log_message("✅ NASDAQ closed positive. Change % = "+ change + ". Placing buy order")
            symbol = "MON100"
            security_id = 22739
            ticker = symbol_details(symbol)
            cmp = ticker.fast_info['lastPrice']      
            dhan_service.place_buy_order(security_id, get_quantity(MAX_AMOUNT_NASDAQ, cmp))

        elif change < 0:
            log_message("❌ NASDAQ closed negative. Change % = "+ str(change) + ". Not eligible for fresh order")
        else:
            log_message("❌ NASDAQ closed flat. Change % = "+ str(change) + ". Not eligible for fresh order")

def is_nifty_positive_supertrend():
    #log_message("implement buy logic")
    result = compute_supertrend()
    log_message(f"Is Nifty in positive SuperTrend? {'✅ Yes' if result else '❌ No'}")
    return result

def compute_supertrend():
    period=10
    multiplier=3
    today = datetime.today().date()
    start_date = today - timedelta(days=365)
    
    df = yf.download("^NSEI", start=start_date, end=today, interval="1d", auto_adjust=True, progress=False)
    
    if df.empty:
        raise ValueError("No data downloaded. Check date range or ticker.")

    high = df['High'].squeeze()
    low = df['Low'].squeeze()
    close = df['Close'].squeeze()

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, min_periods=period).mean()
    hl2 = ((high + low) / 2).squeeze()

    basic_ub = hl2 + multiplier * atr
    basic_lb = hl2 - multiplier * atr

    final_ub = basic_ub.copy()
    final_lb = basic_lb.copy()

    supertrend = pd.Series(True, index=df.index)

    for i in range(1, len(df)):
        if (basic_ub.iat[i] < final_ub.iat[i-1]) or (close.iat[i-1] > final_ub.iat[i-1]):
            final_ub.iat[i] = basic_ub.iat[i]
        else:
            final_ub.iat[i] = final_ub.iat[i-1]

        if (basic_lb.iat[i] > final_lb.iat[i-1]) or (close.iat[i-1] < final_lb.iat[i-1]):
            final_lb.iat[i] = basic_lb.iat[i]
        else:
            final_lb.iat[i] = final_lb.iat[i-1]

    for i in range(1, len(df)):
        if close.iat[i] > final_ub.iat[i-1]:
            supertrend.iat[i] = True
        elif close.iat[i] < final_lb.iat[i-1]:
            supertrend.iat[i] = False
        else:
            supertrend.iat[i] = supertrend.iat[i-1]
            if supertrend.iat[i] and (final_lb.iat[i] < final_lb.iat[i-1]):
                final_lb.iat[i] = final_lb.iat[i-1]
            if not supertrend.iat[i] and (final_ub.iat[i] > final_ub.iat[i-1]):
                final_ub.iat[i] = final_ub.iat[i-1]

    # Return True if latest supertrend is positive (uptrend), else False
    return bool(supertrend.iat[-1])

def is_nifty_positive_today():
    # Download last 5 days of data
    df = yf.download("^NSEI", period="5d", interval="1d", progress=False, auto_adjust=True)

    # Check if data is returned
    if df.empty:
        raise ValueError("Downloaded data is empty. Check internet or symbol.")

    # If multi-index columns, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Check if 'Close' exists
    if "Close" not in df.columns:
        raise KeyError(f"'Close' column not found. Columns available: {df.columns.tolist()}")

    # Drop rows with missing Close values
    df = df.dropna(subset=["Close"])

    if len(df) < 2:
        raise ValueError("Not enough valid data points to compare today vs yesterday.")

    # Get today's and yesterday's close
    today_close = df['Close'].iloc[-1]
    yesterday_close = df['Close'].iloc[-2]

    # Get last two close prices
    today_close = df['Close'].iloc[-1]
    yesterday_close = df['Close'].iloc[-2]

    result = today_close > yesterday_close
    log_message(f"Nifty is {'positive 📈' if result else 'negative 📉'} today.")

    # Compare and return result
    if result:
        return True  # Positive
    else:
        return False  # Negative


def buy_etf_supertrend_strategy():
    # ✅ Place buy logic here    
    security_id=10576
    symbol="NIFTYBEES.NS"
    ticker = symbol_details(symbol)
    cmp = ticker.fast_info['lastPrice']
    quantity = get_quantity(MAX_AMOUNT_LONGTERM, cmp)
    log_message(f"Buying {symbol} {security_id} quantity : {quantity} at price {cmp}")
    dhan_service.place_buy_order(security_id, quantity)

def symbol_details(symbol):    
    try:
        ticker = yf.Ticker(symbol)
        #log_message(ticker.fast_info['lastPrice'])
        return ticker
    except Exception as e:
        log_message(f"Error fetching details for {symbol}: {e}")
        return None

def add_price_data(df_holdings):
    current_prices = []
    change_percentages = []
    gain_losses = []

    for symbol, qty, avg_price in zip(df_holdings['tradingSymbol'], 
                                       df_holdings['totalQty'], 
                                       df_holdings['avgCostPrice']):
        try:
            yf_symbol = symbol if symbol.endswith('.NS') else symbol + '.NS'
            ticker = yf.Ticker(yf_symbol)
            price = ticker.fast_info['lastPrice']
            previous_close = ticker.fast_info['previousClose']

            change_pct = ((price - avg_price) / avg_price) * 100 if avg_price else 0
            gain_loss = (price - avg_price) * qty

        except Exception as e:
            log_message(f"⚠️ Could not fetch data for {symbol}: {e}")
            price = None
            change_pct = None
            gain_loss = None

        current_prices.append(price)
        change_percentages.append(change_pct)
        gain_losses.append(gain_loss)

    df_holdings['current_price'] = current_prices
    df_holdings['change_percentage'] = change_percentages
    df_holdings['loss_gain_amount'] = gain_losses

    return df_holdings