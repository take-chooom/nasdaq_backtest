import sqlite3
import pandas as pd

def load_prices(db_path:str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql_query(
        "SELECT * FROM prices_weekly WHERE symbol = ?;", 
        conn, 
        params=("QQQ",))
    
    conn.close()
    
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    #週次リターン行追加
    df["ret"] = df.groupby("symbol")["adj_close"].pct_change()
    return df


if __name__ == "__main__":
    db_path = "data/prices.sqlite"
    df = load_prices(db_path)
    
    print(df.head())
    print(df.tail())