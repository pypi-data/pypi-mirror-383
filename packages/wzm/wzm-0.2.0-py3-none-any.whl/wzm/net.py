from __future__ import annotations
from typing import Dict, Any, Optional
import requests

def get_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
    """发送 GET 并解析 JSON。

    Args:
        url: 完整 URL。
        params: 查询参数。
        timeout: 超时秒数。

    Returns:
        Any: JSON 解码结果（一般是 dict/list）。
    """
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()
