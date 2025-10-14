from __future__ import annotations
from typing import Any, Dict, Optional, Mapping
import requests
from .config import get_options

class Client:
    """极简 HTTP 客户端（自动应用全局配置）。

    Args:
        api_base: 覆盖全局的 API 基地址。
        api_key: 覆盖全局的 API 令牌。
        timeout: 覆盖全局超时（秒）。
        extra_headers: 额外的请求头，优先级最高。
    """

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        opts = get_options()
        self.api_base = api_base or opts.api_base
        self.api_key = api_key or opts.api_key
        self.timeout = timeout or opts.timeout
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        if extra_headers:
            self.session.headers.update(dict(extra_headers))

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET 请求。"""
        url = self._join(self.api_base, endpoint)
        r = self.session.get(url, params=params or {}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """POST 请求（JSON）。"""
        url = self._join(self.api_base, endpoint)
        r = self.session.post(url, json=json or {}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _join(base: str, path: str) -> str:
        if path.startswith(("http://","https://")):
            return path
        return f"{base.rstrip('/')}/{path.lstrip('/')}"
