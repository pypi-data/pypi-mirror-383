"""wzm — A typed demo SDK.

本包提供常用的小功能（金融/统计/网络）以及一个最简 HTTP 客户端。
所有公共 API 都带完整类型标注和参数说明，IDE 会显示代码提示。

Docstring 风格：Google style
"""
__docformat__ = "google"

from .core import hello, moving_avg, describe, table
from .finance import momentum, ema, drawdown
from .net import get_json
from .config import set_options, get_options, Options
from .client import Client

__all__ = [
    "hello", "moving_avg", "describe", "table",
    "momentum", "ema", "drawdown",
    "get_json",
    "set_options", "get_options", "Options",
    "Client",
]
