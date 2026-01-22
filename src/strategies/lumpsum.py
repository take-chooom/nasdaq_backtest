import pandas as pd
from matplotlib import pyplot as plt

def simulate_yearly_lumpsum(df,yearly_amount=10000): #yearly_amount($)
    #年初で購入する価格を決定
    df = df.copy()
    df["year"] = df["date"].dt.year
    
    y_first_prices = df.groupby("year").first()["adj_close"]
    y_end_prices = df.groupby("year").last()["adj_close"]
    
    units_bought = yearly_amount / y_first_prices
    units_total = units_bought.cumsum()
    
    value = units_total * y_end_prices
    
    final_value = value.iloc[-1]
    
    history_df = pd.DataFrame({
        "year": y_first_prices.index,
        "buy_price": y_first_prices.values,
        "year_end_price": y_end_prices.values,
        "units_bought": units_bought.values,
        "units_total": units_total.values,
        "value": value.values,
    }).reset_index(drop=True)
    
    history_df["value_10k_usd"] = history_df["value"] / 10000
    
    return final_value, history_df

if __name__ == "__main__":
    from src.load_prices import load_prices
    
    db_path = "data/prices.sqlite"
    df = load_prices(db_path)
    
    final_value, history_df = simulate_yearly_lumpsum(df)
    
    print(f"final_value:{final_value}")
    print("------history_df------")
    print(history_df.tail())
    
    #グラフ表示
    x = history_df["year"]
    y = history_df["value_10k_usd"]
    
    plt.figure(figsize=(10,5))
    plt.plot(x,y)
    plt.title("Yearly Lump Sum Portfolio Value (QQQ)")
    plt.xlabel("year")
    plt.ylabel("Portfolio Value (10k USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("output/lumpsum_value.png", dpi=150)
    