import pandas as pd
from utils.logger import log_message, get_logs

def read_stock_symbols1(csvFile="../data/symbols.csv"):
    df = pd.read_csv(csvFile)
    return df

def read_master_etfs(from_github=False):
    if from_github:
        log_message("Reading from github")
        url = "https://raw.githubusercontent.com/dineshtec01/data-reference/main/trade/etf-scrip-master.csv"
        df = pd.read_csv(url)
    else:
        log_message("Reading from local")
        df = pd.read_csv("../data/etf-scrip-master.csv", low_memory=False)

    # Filter ETF records
    filtered_df = df[
        (df['SEM_EXM_EXCH_ID'] == 'NSE') & 
        (df['SEM_EXCH_INSTRUMENT_TYPE'] == 'ETF') & 
        (df['SEM_SERIES'] == 'EQ')
    ]

    print(f"Filtered ETF count: {len(filtered_df)}")

    selected_columns = [
        "SEM_EXM_EXCH_ID", "SEM_SMST_SECURITY_ID",
        "SEM_TRADING_SYMBOL", "SEM_CUSTOM_SYMBOL", "SM_SYMBOL_NAME"
    ]
    
    # Optional: keep only selected columns
    filtered_df = filtered_df[selected_columns]

    return filtered_df
