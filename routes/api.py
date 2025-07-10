from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/etf_signals", methods=["GET"])
def get_etf_signals():
    # Replace this with dynamic or DB-based data
    signals = [
        {
            "symbol": "ALPHA", 
            "name": "Kotak Nifty Alpha 50 ETF",
            "price": 530.60, 
            "wk52low": 500.82, 
            "distance": 11.56,
            "symbol": "Buy",
            "chart" : "https://in.tradingview.com/chart/6YKS8gJ3/?symbol=NSE%3AGLENMARK"
        },
        {
            "symbol": "AUTOIETF", 
            "name": "Kotak Nifty Alpha 50 ETF",
            "price": 530.60, 
            "wk52low": 500.82, 
            "distance": 11.56,
            "symbol": "Buy",
            "chart" : "https://in.tradingview.com/chart/6YKS8gJ3/?symbol=NSE%3AGLENMARK"
        },
        {
            "symbol": "CPSEETF", 
            "name": "Nippon India CPSE ETF",
            "price": 530.60, 
            "wk52low": 500.82, 
            "distance": 11.56,
            "symbol": "Buy",
            "chart" : "https://in.tradingview.com/chart/6YKS8gJ3/?symbol=NSE%3AGLENMARK"
        },
        {
            "symbol": "DIVOPPBEES", 
            "name": "Nippon Nifty 50 DO ETF (DIVOPPBEES)",
            "price": 530.60, 
            "wk52low": 500.82, 
            "distance": 11.56,
            "symbol": "Buy",
            "chart" : "https://in.tradingview.com/chart/6YKS8gJ3/?symbol=NSE%3AGLENMARK"
        }
    ]
    return jsonify(signals)


