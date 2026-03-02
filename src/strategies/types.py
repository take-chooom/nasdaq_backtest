from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class SimResult:
    final_value: float
    total_invested: float
    return_pct: float
    max_drawdown_pct: float
    history_df: pd.DataFrame
    n_trades: int


@dataclass(frozen=True)
class DipBuyParams:
    dip_threshold: float
    buy_amount: float = 1000.0
    initial_amount: float | None = None  # 初期投資額（オプション、グリッドサーチで扱いやすいように）

@dataclass(frozen=True)
class LumpSumParams:
    yearly_amount: float = 10000.0
