import pandas as pd

from src.load_prices import load_prices
from src.strategies.dip_buy import dip_buy
from src.strategies.lumpsum import simulate_yearly_lumpsum

def main():
    df = load_prices("data/prices.sqlite")
    
    rows = []
    # --- lumpsum ---
    res = simulate_yearly_lumpsum(df,yearly_amount=10000)
    
    final_value, total_invested, return_pct, history_lump = (
        res["final_value"], res["total_invested"], res["return_pct"], res["history_df"])
    
    rows.append({
        "strategy": "lumpsum_yearly",
        "dip": None,
        "amount_usd": 10000,    #yearly_amount
        "buy_cnt": len(history_lump),
        "final_value": final_value,
        "total_invested": total_invested,
        "return_pct": return_pct,
    })
    
    for dip in [0.01*i for i in range(2,7)]:
        res = dip_buy(df,dip=dip, amount=1000)
        history_df = res["history_df"]
        buy_cnt = int(history_df["buy_signal"].sum())
        
        rows.append({
            "strategy": f"dip_buy_weekly_{int(dip*100)}pct",
            "dip": dip,
            "amount_usd": 1000,
            "buy_cnt": buy_cnt,
            "final_value": res["final_value"],
            "total_invested": res["total_invested"],
            "return_pct": res["return_pct"],
        })
    
    result_df = pd.DataFrame(rows).sort_values("return_pct", ascending=False)
    print(result_df.to_string(index=False))
    
if __name__ == "__main__":
    main()