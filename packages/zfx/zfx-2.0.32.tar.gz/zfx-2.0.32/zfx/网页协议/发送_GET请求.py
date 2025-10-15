import requests
from typing import Optional, Dict, Union
from requests import Response


def 发送_GET请求(
    url: str,
    params: Optional[Dict] = None,
    timeout: Union[int, float] = 60,
    headers: Optional[Dict[str, str]] = None,
    严格模式: bool = True,
) -> Union[Response, str]:
    """
    安全发送 HTTP GET 请求。

    功能说明：
        本函数用于安全地发送 GET 请求。成功时返回 requests.Response 对象；
        发生异常时，不会抛出错误，而是返回错误信息字符串，保证调用安全性。
        可通过“严格模式”参数控制是否将非 2xx 状态码视为异常。

    参数：
        url (str):
            请求的完整 URL 地址，例如 "https://www.example.com"。
        params (dict | None):
            查询参数，将自动拼接到 URL，例如 {"q": "python"}。
            默认值为 None。
        timeout (int | float):
            请求超时时间（单位：秒），默认值为 60。
        headers (dict[str, str] | None):
            自定义请求头，例如 {"User-Agent": "Mozilla/5.0"}。
            默认值为 None。
        严格模式 (bool):
            控制状态码异常行为：
              - True：仅当响应状态码为 2xx 时返回响应对象；
                      其他状态码（如 404、500）将触发异常并返回错误信息。
              - False：无论状态码是否正常，均直接返回响应对象。
            默认值为 True。

    返回：
        requests.Response | str:
            - 当请求成功（或严格模式关闭）时，返回 Response 对象；
              可直接访问属性：.text、.json()、.status_code。
            - 当出现任何异常（网络超时、连接错误、状态码异常等）时，
              返回错误信息字符串，格式如："请求失败: 连接超时"。

    使用说明：
        1. 本函数永不抛出异常，适合用于批量请求或无人值守任务。
        2. 若需要自行判断 HTTP 状态码，请将“严格模式”设为 False。
        3. 若需要代理、重试或会话保持，可在外层通过 requests.Session() 实现。
    """
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if 严格模式:
            resp.raise_for_status()
        return resp
    except Exception as e:
        return f"请求失败: {e}"