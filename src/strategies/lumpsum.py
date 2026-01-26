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
    
    history_df = pd.DataFrame({
        "year": y_first_prices.index,
        "buy_price": y_first_prices.values,
        "year_end_price": y_end_prices.values,
        "units_bought": units_bought.values,
        "units_total": units_total.values,
        "value": value.values,
    }).reset_index(drop=True)
    
    
    history_df["value_10k_usd"] = history_df["value"] / 10000
    
    #総投資額追加 
    history_df["invested_10k_usd"] = yearly_amount * (history_df.index + 1) / 10000
    
    total_invested = history_df["invested_10k_usd"].iloc[-1] 
    final_value = history_df["value_10k_usd"].iloc[-1]
    return_pct = (final_value / total_invested - 1) * 100 if total_invested != 0 else float("nan")
    
    return {
        "final_value": final_value,
        "total_invested": total_invested,
        "return_pct": return_pct,
        "history_df": history_df
    } 

if __name__ == "__main__":
    from src.load_prices import load_prices
    
    db_path = "data/prices.sqlite"
    df = load_prices(db_path)
    
    res = simulate_yearly_lumpsum(df)
    
    final_value, total_invested, return_pct, history_df = (
        res["final_value"], res["total_invested"], res["return_pct"], res["history_df"])
    
    
    print(f"final_value:{final_value:.2f}万ドル,最終リターン(%):{return_pct:.2f}%")
    
    #グラフ表示
    x = history_df["year"]
    y1 = history_df["value_10k_usd"]
    y2 = history_df["invested_10k_usd"]
    
    plt.figure(figsize=(10,5))
    plt.plot(x, y1, label="Portfolio Value (10k USD)")
    plt.plot(x, y2, label="Total Invested (10k USD)", linestyle="--")
    
    plt.title("Yearly Lump Sum Portfolio Value (QQQ)")
    plt.xlabel("Year")
    plt.ylabel("Value (10k USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/lumpsum_value.png", dpi=150)
    