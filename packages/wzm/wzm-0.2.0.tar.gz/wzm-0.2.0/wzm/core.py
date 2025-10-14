from __future__ import annotations
from typing import Sequence, Literal, overload
import pandas as pd

def hello(name: str = "world", punctuation: str = "!") -> str:
    """返回问候语。

    Args:
        name: 名字。
        punctuation: 结尾标点，默认 "!".

    Returns:
        str: 形如 "Hello, Alice!" 的字符串。
    """
    return f"Hello, {name}{punctuation}"

@overload
def moving_avg(seq: Sequence[float], window: int = 3, center: bool = False, return_type: Literal["list","series"] = "list") -> list[float]: ...
@overload
def moving_avg(seq: Sequence[float], window: int = 3, center: bool = False, return_type: Literal["series"] = "list") -> pd.Series: ...

def moving_avg(seq, window: int = 3, center: bool = False, return_type: Literal["list","series"] = "list"):
    """简单移动平均（支持是否居中、返回类型）。

    Args:
        seq: 数值序列。
        window: 窗口（>=1）。
        center: 是否居中窗口（True 使用等权滑动居中平均）。
        return_type: "list" 或 "series"。

    Returns:
        list[float] | pandas.Series: 移动平均结果（边界处含 NaN）。

    Examples:
        >>> moving_avg([1,2,3,4], window=2)
        [nan, 1.5, 2.5, 3.5]
        >>> moving_avg([1,2,3,4], window=3, center=True, return_type="series")
        0    NaN
        1    2.0
        2    3.0
        3    NaN
        dtype: float64
    """
    if window <= 0:
        raise ValueError("window must be >= 1")
    s = pd.Series(list(seq), dtype="float64")
    out = s.rolling(window=window, center=center).mean()
    return out if return_type == "series" else out.tolist()

def describe(seq: Sequence[float]) -> dict:
    """统计描述（count/mean/std/min/25%/50%/75%/max），NaN 会被自动忽略。"""
    s = pd.Series(list(seq), dtype="float64")
    d = s.describe()
    return {k: (float(d[k]) if pd.notna(d[k]) else None) for k in ["count","mean","std","min","25%","50%","75%","max"]}

def table(data: dict[str, Sequence]) -> pd.DataFrame:
    """将列字典快速转换为 DataFrame。"""
    return pd.DataFrame(data)
