import yfinance as yf
import pandas as pd

def fetch_data():
    #ティッカーコード指定.今回はQQQに固定
    ticker_code = "QQQ"
    QQQ = yf.Ticker(ticker_code)
    
    #過去30年分の週足データ取得
    df = QQQ.history(period='30y', interval='1wk', auto_adjust=False)
    
    df.index = df.index.tz_localize(None)
    df = df.reset_index()
    
    df = df[["Date","Adj Close"]].copy()
    df = df.rename(columns={"Date":"date","Adj Close":"adj_close"})
    df["symbol"] = ticker_code
    df = df[["symbol","date","adj_close"]]

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    return df

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())
    print("--------------------")
    print(f'columns:{df.columns}')
    print(f'isnasum:{df.isna().sum()}')