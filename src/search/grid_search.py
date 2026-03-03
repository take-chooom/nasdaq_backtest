import os
import math
import itertools
import pandas as pd

from src.load_prices import load_prices
from src.strategies.types import DipBuyParams
from src.strategies.dip_buy import simulate
from src.metrics import max_drawdown

def calc_years(history_df: pd.DataFrame) -> float:
    df = history_df.dropna(subset=["date"])
    if len(df) < 2:
        return 0.0
    
    return (df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25

def calc_cagr(history_df: pd.DataFrame, years: float) -> float:
    """
    CAGR(年平均リターン) = (end/start)^(1/years) - 1
    """
    df = history_df.dropna(subset=["date", "value"]).copy()
    
    if len(df) < 2:
        return float("nan")

    start = float(df["value"].iloc[0])
    end = float(df["value"].iloc[-1])
    if start <= 0 or end <= 0 or years <= 0:
        return float("nan")

    return (end / start) ** (1.0 / years) - 1.0

def cnt_adjustment(cnt: int, years: float) -> float:
    #年数に応じた適切な取引回数の目安（例: 1年なら1回、5年なら5回程度）
    year_amount = max(1,int(round(years))) #19.6年とかなら大体20年運用したとみる
    
    rate = cnt / year_amount  # 一年あたりの購入回数
    
    # 適切な取引回数の範囲を定め、そこからの乖離に応じてスコアを調整する
    #2年に一度しか買わないとなると、機会損失が大きいと考える。
    if rate < 0.5: 
        return 0.9
    #多すぎなとき
    elif rate > 3.0:
        #rate = 3 -> 0.9くらい。それ以上はさらに減点していくイメージ
        k = 0.5 #指数ペナルティの強さ、1年で何回も買わないといけないのはきついので強めがおすすめ
        adj = 0.9 * math.exp(-k * (rate - 3.0))
        return max(adj, 0.3)  # マイナス補正の下限は0.3とする
    else:
        return 1.0

def buy_amount_adjustment(buy_amount: float, target: float, sigma: float = 0.5,
                          bonus: float = 1.1, floor: float = 0.85) -> float:
    """
    target: ユーザーの現実的な1回あたり投資額（例: monthly_budget）
    sigma: どの程度のズレまで許容するか（対数スケール）
    
    引数を個人によって変えることでその人の最適な買い方をみつけることができる
    """
    if buy_amount <= 0 or target <= 0:
        return 1.0

    # 比率のズレを対数で扱う（2倍/半分が対称になる）
    d = math.log(buy_amount / target)
    adj = 1.0 + (bonus - 1.0) * math.exp(-(d * d) / (2 * sigma * sigma))
    return max(floor, adj)


def score_fn(cagr: float, mdd_pct: float, cnt: int, years: float,
             buy_amount: float, target_buy_amount: float, lam: float = 0.5) -> float:
    """
    cnt = 総投資回数 (n_trades)
    score = (CAGR - lam * |MDD| )* cnt_adjustment * buy_amount_adjustment
    mdd_pct は負（例:-35.2）
    """
    if pd.isna(cagr) or pd.isna(mdd_pct) or years <= 0:
        return float("-inf")
    
    base = cagr - lam * (abs(mdd_pct) / 100.0)
    cnt_adj = cnt_adjustment(cnt=cnt, years=years)
    buy_adj = buy_amount_adjustment(buy_amount=buy_amount, target=target_buy_amount)

    return base * cnt_adj * buy_adj


def run_grid_search(df_prices: pd.DataFrame, param_grid: dict, target_buy_amount: float, lam: float = 0.5) -> pd.DataFrame:
    keys = list(param_grid.keys())
    rows = []
    
    for values in itertools.product(*(param_grid[k] for k in keys)):
        params_dict = dict(zip(keys, values))
        params = DipBuyParams(**params_dict)

        res = simulate(df_prices, params)
        hist = res.history_df

        years = calc_years(hist)
        cagr = calc_cagr(hist, years)
        mdd_pct = res.max_drawdown_pct
        cnt = res.n_trades
        
        score = score_fn(cagr=cagr, mdd_pct=mdd_pct, cnt=cnt, years=years,
                         buy_amount=params.buy_amount, target_buy_amount=target_buy_amount, lam=lam)

        rows.append({
            **params_dict,
            "CAGR": cagr,
            "MDD_pct": mdd_pct,
            "final_value": res.final_value,
            "total_invested": res.total_invested,
            "return_pct": res.return_pct,
            "n_trades": res.n_trades,
            "years": years,
            "rate_per_year": cnt / max(1,int(round(years))),
            "score": score,
            
        })

    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def main():
    os.makedirs("output", exist_ok=True)

    df = load_prices("data/prices.sqlite")

    # 最小構成（dip_threshold × buy_amount）
    param_grid = {
        "dip_threshold": [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10],
        "buy_amount": [1000, 2000, 5000, 10000],
        "initial_amount": [10000],  # 初期投資額固定
    }

    # ユーザーが設定するところ 一例として、lam = 0.1,target_buy_amount = 5000に設定した。
    lam = 0.1  # MDDのペナルティ係数（大きくするとMDDの影響が強くなる。大きく減るのが怖いときはこの値を大きくすること）
    target_buy_amount = 5000  # 投資余力。常にこのくらいは投資できる額。人によって変わってくる
    
    results = run_grid_search(df, param_grid, target_buy_amount=target_buy_amount, lam=lam)

    results.to_csv("output/results2.csv", index=False)
    results.to_excel("output/results2.xlsx", index=False)#見やすいように
    results.head(10).to_csv("output/top10.csv", index=False)

    print("=== TOP 10 ===")
    print(results.head(10).to_string(index=False))
    print("\nSaved: output/results2.csv, output/results2.xlsx, output/top10.csv")


if __name__ == "__main__":
    main()