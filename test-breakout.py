import yfinance as yf, pandas as pd, numpy as np, talib, backtrader as bt

# === 1. Fetch data ===
def fetch(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df.dropna()

# === 2. Preprocess ===
def preprocess(df, v_window, cons_window):
    df['res'] = df['High'].rolling(v_window).max()
    df['sup'] = df['Low'].rolling(v_window).min()
    df['v30'] = df['Volume'].rolling(v_window).mean()
    df['vcon'] = df['Volume'].rolling(cons_window).max()
    return df

# === 3. Detect price patterns ===
def has_patterns(df, idx):
    c = df.iloc[idx]
    o,h,l,cl = c[['Open','High','Low','Close']]
    # Double bottom: local minima
    if df['Low'][idx] <= df['Low'][idx-2:idx+3].min():
        return True
    # Flag: narrow channel post strong rally
    # Cup&Handle candidates via TA-Lib (NA support but simplified)
    return False

# === 4. Valid breakout ===
def is_breakout(df, idx, vol_mult):
    t = df.iloc[idx]
    cond = (t.Close>t.res and
            t.Volume>=vol_mult*max(t.v30,t.vcon) and
            talib.CDLDOJI(df.Open,df.High,df.Low,df.Close)[idx]==0 and
            (talib.CDLMARUBOZU(df.Open,df.High,df.Low,df.Close)[idx]!=0 or
             abs(t.Close-t.Open) > (t.High-t.Low - abs(t.Close-t.Open))))
    return cond and has_patterns(df, idx)

# === 5. Reward/Risk and sizing ===
class PercentRiskSizer(bt.Sizer):
    params = dict(risk_perc=0.01)
    def _getsizing(self, comminfo, cash, data, isbuy):
        price, stop = data.close[0], data.sup[0]
        risk = (price - stop) * data.close[0].size if stop else 0
        cap = self.broker.getvalue()
        size = (cap*self.p.risk_perc) // risk if risk>0 else 0
        return int(size)

# === 6. Strategy definition ===
class Breakout(bt.Strategy):
    params = dict(v_window=30, cons_window=20, vol_mult=2, rr=2)
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.df = preprocess(self.datas[0].p.dataname, self.p.v_window, self.p.cons_window)

    def next(self):
        idx = len(self.df) -1
        if is_breakout(self.df, idx, self.p.vol_mult):
            if self.dataclose[0] > self.df.res.iloc[idx]:  # confirmation
                rr, sl, tgt = compute_rr(self.df, idx, self.p.rr)
                if rr>=self.p.rr and not self.position:
                    self.buy()
                    self.stop_price=sl; self.target_price=tgt
        if self.position:
            if (self.dataclose[0]<=self.stop_price or self.dataclose[0]>=self.target_price):
                self.close()

# === 7. Reward/Risk utility ===
def compute_rr(df, idx, target_rr):
    bp, sl = df.res.iloc[idx], df.sup.iloc[idx]
    tgt = bp + target_rr*(bp-sl)
    rr = (tgt - df.Close.iloc[idx+1])/(bp-sl) if idx+1<len(df) else 0
    return rr, sl, tgt

# === 8. Execution and optimization ===
if __name__=='__main__':
    df = fetch('AAPL','2023-01-01','2025-07-01')
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(Breakout)
    cerebro.addsizer(PercentRiskSizer, risk_perc=0.01)
    cerebro.broker.setcash(100000)
    cerebro.optstrategy(
      Breakout,
      v_window=[20,30,40],
      cons_window=[15,20],
      vol_mult=[1.5,2,2.5],
      rr=[1.5,2,2.5]
    )
    results = cerebro.run(maxcpus=1)
    print("Best result:", sorted(results, key=lambda strat: strat.broker.getvalue())[-1].broker.getvalue())
