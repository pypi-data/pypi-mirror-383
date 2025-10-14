from __future__ import annotations
from typing import Sequence, Literal, overload
import pandas as pd

Number = float

def _to_series(x: Sequence[Number], name: str = "x") -> pd.Series:
    return pd.Series(list(x), dtype="float64", name=name)

@overload
def momentum(prices: Sequence[Number], window: int = 5, return_type: Literal["series"] = "series") -> pd.Series: ...
@overload
def momentum(prices: Sequence[Number], window: int = 5, return_type: Literal["list"]   = "series") -> list[float]: ...

def momentum(prices, window: int = 5, return_type: Literal["series","list"] = "series"):
    """简单动量：p_t / p_{t-window} - 1。

    Args:
        prices: 价格序列（list/tuple/可迭代）。
        window: 窗口大小，>=1。
        return_type: 返回类型；"series" -> pandas.Series；"list" -> list[float]。

    Returns:
        pandas.Series | list[float]: 动量序列（前 window 个为 NaN）。

    Examples:
        >>> momentum([100, 105, 110, 120], window=2).tolist()
        [nan, nan, 0.05, 0.09090909090909094]
        >>> momentum([100, 105, 110, 120], window=2, return_type="list")
        [nan, nan, 0.05, 0.09090909090909094]
    """
    if window <= 0:
        raise ValueError("window must be >= 1")
    s = _to_series(prices, "price")
    out = s / s.shift(window) - 1.0
    return out if return_type == "series" else out.tolist()

@overload
def ema(values: Sequence[Number], span: int = 12, adjust: bool = False, return_type: Literal["series"] = "series") -> pd.Series: ...
@overload
def ema(values: Sequence[Number], span: int = 12, adjust: bool = False, return_type: Literal["list"]   = "series") -> list[float]: ...

def ema(values, span: int = 12, adjust: bool = False, return_type: Literal["series","list"] = "series"):
    """指数移动平均（封装 pandas.Series.ewm）。

    Args:
        values: 数值序列。
        span: 平滑跨度，>=1。
        adjust: pandas ewm 的 adjust 参数。
        return_type: "series" 或 "list"。

    Returns:
        pandas.Series | list[float]: EMA 序列。
    """
    if span <= 0:
        raise ValueError("span must be >= 1")
    s = _to_series(values, "value").ewm(span=span, adjust=adjust).mean()
    return s if return_type == "series" else s.tolist()

@overload
def drawdown(prices: Sequence[Number], return_type: Literal["series"] = "series") -> pd.Series: ...
@overload
def drawdown(prices: Sequence[Number], return_type: Literal["list"]   = "series") -> list[float]: ...

def drawdown(prices, return_type: Literal["series","list"] = "series"):
    """回撤：(p / cummax(p)) - 1。

    Args:
        prices: 价格序列。
        return_type: "series" 或 "list"。

    Returns:
        pandas.Series | list[float]: 回撤序列，最小值即最大回撤。
    """
    s = _to_series(prices, "price")
    dd = s / s.cummax() - 1.0
    return dd if return_type == "series" else dd.tolist()
