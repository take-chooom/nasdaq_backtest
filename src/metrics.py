import pandas as pd

def max_drawdown(value: pd.Series) -> float:
    """
    value: 資産推移
    return: 最大ドローダウン
    """
    
    v = value.astype(float)
    peak = v.cummax()
    dd = v / peak - 1.0
    return float(dd.min())
