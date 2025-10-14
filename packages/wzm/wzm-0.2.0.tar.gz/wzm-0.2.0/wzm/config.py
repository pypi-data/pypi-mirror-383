from __future__ import annotations
from typing import Optional

try:
    from pydantic import BaseModel, Field
    _HAS_PYDANTIC = True
except Exception:  # pragma: no cover
    _HAS_PYDANTIC = False

if _HAS_PYDANTIC:
    class Options(BaseModel):
        """全局配置选项。

        Attributes:
            api_base: API 基地址，如 "https://api.example.com"。
            api_key: API 访问令牌。若不设置则不注入 Authorization 头。
            cache_dir: 预留；可用于本地缓存目录。
            timeout: HTTP 超时（秒）。
        """
        api_base: str = Field(default="https://api.example.com", description="API 基地址")
        api_key: Optional[str] = Field(default=None, description="API 令牌")
        cache_dir: Optional[str] = Field(default=None, description="本地缓存目录")
        timeout: float = Field(default=10.0, ge=0.1, description="HTTP 超时（秒）")

        def model_dump(self):
            # pydantic v2 signature
            return super().model_dump()

else:
    # 简单 fallback，不依赖 pydantic；保留同名接口
    from dataclasses import dataclass
    @dataclass
    class Options:
        api_base: str = "https://api.example.com"
        api_key: Optional[str] = None
        cache_dir: Optional[str] = None
        timeout: float = 10.0

    def _asdict(o: "Options"):
        return {
            "api_base": o.api_base,
            "api_key": o.api_key,
            "cache_dir": o.cache_dir,
            "timeout": o.timeout,
        }

_options = Options()

def set_options(
    *,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
    cache_dir: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Options:
    """更新全局配置，并返回新的配置快照。

    Args:
        api_base: API 基地址。
        api_key: 访问令牌。
        cache_dir: 缓存目录。
        timeout: 超时秒数（>=0.1）。

    Returns:
        Options: 新的配置。
    """
    global _options
    if _HAS_PYDANTIC:
        data = _options.model_dump()  # type: ignore[attr-defined]
    else:
        data = _asdict(_options)      # type: ignore[misc]

    if api_base is not None: data["api_base"] = api_base
    if api_key is not None:  data["api_key"] = api_key
    if cache_dir is not None:data["cache_dir"] = cache_dir
    if timeout is not None:  data["timeout"] = timeout
    _options = Options(**data)
    return _options

def get_options() -> Options:
    """获取当前全局配置。"""
    return _options
