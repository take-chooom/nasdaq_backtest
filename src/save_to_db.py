import sqlite3
import pandas as pd

def create_prices_table(db_path:str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
                CREATE TABLE IF NOT EXISTS prices_weekly(
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    adj_close REAL NOT NULL,
                    PRIMARY KEY (symbol,date)
                )
                """)
    
    conn.commit()
    conn.close()

def insert_prices(df:pd.DataFrame,db_path:str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    rows = df[["symbol", "date", "adj_close"]].values.tolist()
    cur.executemany("""
                    INSERT OR IGNORE INTO prices_weekly (symbol, date, adj_close)
                    VALUES (?, ?, ?)
                    """, rows)
    
    conn.commit()
    conn.close()

def count_rows(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM prices_weekly;")
    n = cur.fetchone()[0]
    conn.close()
    return n


if __name__ == "__main__":
    from fetch_data import fetch_data
    
    db_path = "data/prices.sqlite"
    create_prices_table(db_path)
    
    df = fetch_data()
    insert_prices(df,db_path)
    
    print("rows:", count_rows(db_path))