from services import trade_logic, etf_strategies
from tabulate import tabulate
from utils.logger import log_message, get_logs
from utils.csv_reader import read_master_etfs

def main():
    log_message("📊 Starting stock trader bot...")

    log_message("=================== DAILY ETF Buy Sell started... =================== ")
    etf_strategies.etf_daily_strategy()
    log_message("=================== DAILY ETF Buy Sell end... =================== ")

    log_message("=================== NASDAQ_and_MON100 ETF Buy Sell started...=================== ")
    etf_strategies.NASDAQ_and_MON100()
    log_message("=================== NASDAQ_and_MON100 ETF Buy Sell end... =================== ")

    log_message("=================== Longterm ETF Buy Sell started... =================== ")
    etf_strategies.etf_longterm_nifty50_strategy()
    log_message("=================== Longterm ETF Buy Sell end... =================== ")  


if __name__ == "__main__":
    main()
