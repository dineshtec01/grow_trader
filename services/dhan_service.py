import requests
import os
import uuid
from dotenv import dotenv_values
from unittest.mock import Mock
from utils.logger import log_message, get_logs
from dotenv import load_dotenv

config = dotenv_values("config/config.properties")

load_dotenv()

#CLIENT_ID = config.get("DHAN_CLIENT_ID")
CLIENT_ID = os.getenv("DHAN_CLIENT_ID", config.get("DHAN_CLIENT_ID"))

#ACCESS_TOKEN = config.get("DHAN_ACCESS_TOKEN")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")  # No fallback for sensitive tokens

#BASE_URL = config.get("DHAN_BASE_URL")
BASE_URL = os.getenv("DHAN_BASE_URL", config.get("DHAN_BASE_URL"))

if not CLIENT_ID:
    raise ValueError("Missing CLIENT_ID in environment variables.")

if not ACCESS_TOKEN:
    raise ValueError("Missing DHAN_ACCESS_TOKEN in environment variables.")

TESTING = config.get("TESTING")

HEADERS = {
    "access-token": ACCESS_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def isTesting():
    if(TESTING == "yes"):
        log_message("===================> Testing phase")
        return True
    else:
        return False

def get_live_price(symbol):
    url = f"{BASE_URL}/market/live/{symbol}"  # Replace with real endpoint
    response = requests.get(url, headers=HEADERS)
    return response.json()  # Adapt as per real Dhan response

def place_buy_order(security_id, quantity):
    response = Mock()
    order_data = {
        "dhanClientId": CLIENT_ID,
        "correlationId": str(uuid.uuid4().hex[:10]),
        "transactionType": "BUY",
        "exchangeSegment": "NSE_EQ",
        "productType": "CNC",
        "orderType": "MARKET",
        "validity": "DAY",
        "securityId": security_id,
        "quantity": int(quantity),
        "disclosedQuantity": 0,
        "price": 0,
        "afterMarketOrder": False,
        "icebergOrder": False,
        "userOrderTag": "etf-buy"
    }
    url = f"{BASE_URL}/orders"
    
    if(not(isTesting())):
           response = requests.post(url, headers=HEADERS, json=order_data)
           
    log_message(f"✅ Buying done. response {response.json()}")
    return response.json()

def place_sell_order(security_id, quantity):    
    response = Mock()
    order_data = {
        "dhanClientId": CLIENT_ID,
        "correlationId": str(uuid.uuid4().hex[:10]),
        "transactionType": "SELL",
        "exchangeSegment": "NSE_EQ",
        "productType": "CNC",
        "orderType": "MARKET",
        "validity": "DAY",
        "securityId": "string",
        "quantity": quantity,
        "disclosedQuantity": 0,
        "price": 0,
        "afterMarketOrder": False,
        "icebergOrder": False,
        "userOrderTag": "etf-buy"
    }
    url = f"{BASE_URL}/orders"
    if(not(isTesting())):
        response = requests.post(url, headers=HEADERS, json=order_data)
    log_message(f"✅ Selling done. response {response.json()}")
    return response.json()

def get_holdings():
    #print("==========> BASE_URL is:", BASE_URL)
    url = f"{BASE_URL}/holdings"
    response = requests.get(url, headers=HEADERS)
    return response.json()
