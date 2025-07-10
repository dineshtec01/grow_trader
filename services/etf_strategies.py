
from services import trade_logic
from services import yahoo_service
from tabulate import tabulate
from utils.logger import log_message, get_logs
#from utils.csv_reader import read_master_etfs
from utils.csv_reader import read_master_etfs




def etf_daily_strategy():    
    etf_daily_strategy_sell()
    etf_daily_strategy_buy()

def etf_daily_strategy_buy():
    ## read the ETF csv file
    stocks = read_master_etfs("data/etf-scrip-master.csv")
    #stocks =  read_master_etfs()
    #log_message(stocks)

    ## Calculate the cmp, 52 week low value & % low from 52 weeks
    df_etfs = trade_logic.evaluate_etf(stocks)
   # log_message(tabulate(df_etfs, headers='keys', tablefmt='github'))

    df_holdings = trade_logic.all_holdings()
    df_holdings = trade_logic.enrich_holdings(df_holdings, df_etfs)
    log_message("----------- holdings --------------")
    log_message(df_holdings)
    ## BUY ETF strategy on daily basis
    trade_logic.evaluate_and_buy_etf_daily_strategy(df_etfs,df_holdings)

def etf_daily_strategy_sell():

    df_holdings = trade_logic.all_holdings()

    ## SELL ETF strategy on daily basis
    trade_logic.evaluate_and_sell_etf_daily_strategy(df_holdings)

# NASDAQ and MON100 (Motiwal oswal)
# NASDAQ fluctuate between 1.5 to 2 % in every 2-3 days
# If NASDAQ is positive then high chances is that MON100 will also grow that % 
# So, buy if NASDAQ is positive. Wait till Motilal reaches that% 
def NASDAQ_and_MON100():
    change, last_close = yahoo_service.get_nasdaq_last_day_change()
    
    ## BUY ETF strategy
    trade_logic.evaluate_and_buy_etf_nasdaq_strategy(change, last_close)

    ## Create GTT SELL strategy for this BUY


def etf_longterm_nifty50_strategy():
    if trade_logic.is_nifty_positive_supertrend():
        if  not trade_logic.is_nifty_positive_today():
            log_message("⚠️ NIFTY is in supertred. NIFTY is negative today. Allowed to invest.")
            trade_logic.buy_etf_supertrend_strategy()
        else:
            log_message("🚫 NIFTY is in supertred. NIFTY is Positive today. NOT allowed to invest.")

    else:
        log_message("🚫 NIFTY is not in supertred. Do not invest.")


