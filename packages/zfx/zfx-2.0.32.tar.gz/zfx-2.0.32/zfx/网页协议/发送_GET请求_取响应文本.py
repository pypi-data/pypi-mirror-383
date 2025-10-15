import requests


def 发送_GET请求_取响应文本(网址, 参数=None, 异常返回=False):
    """
    功能：
        发送一个 HTTP GET 请求，并在成功时返回响应的文本内容（str）。
        如果出现异常，可以根据参数选择返回 None 或错误信息字符串。
        默认的超时时间为 60 秒。

    参数：
        - 网址 (str)：
            请求目标的完整 URL，例如 "https://www.example.com"。
        - 参数 (dict | None)：
            可选的查询参数，会以字典形式传入，并自动拼接到 URL。
            例如 {"q": "python"}。默认为 None。
        - 异常返回 (bool)：
            控制异常时的返回行为。
            * False（默认）：异常时返回 None。
            * True：异常时返回错误信息字符串（形如 "处理失败: 错误描述"）。

    返回：
        - str：
            当请求成功时，返回响应的文本内容（通常是 HTML 或 JSON 字符串）。
        - str：
            当异常返回=True 且请求失败时，返回错误描述字符串。
        - None：
            当异常返回=False 且请求失败时，返回 None。

    异常处理逻辑：
        1. 超时：超过 60 秒未响应会触发 Timeout 异常。
        2. 状态码：非 200 状态码会触发 HTTPError 异常。
        3. 其他错误：如 DNS 解析失败、连接错误等，都会被捕获。

    示例：
        >>> 内容 = 发送_GET请求_取响应文本("https://httpbin.org/get")
        >>> print(内容[:100])
        "{\n  \"args\": {}, \n  \"headers\": { ..."

        >>> 内容 = 发送_GET请求_取响应文本("https://xx.invalid", 异常返回=True)
        >>> print(内容)
        "处理失败: HTTPSConnectionPool(..."

    注意事项：
        - 超时时间固定为 60 秒，如需修改需调整代码。
        - 仅返回响应文本，不返回状态码或响应头。
        - 如果需要获取 Response 对象，请使用另一个专门函数。
    """
    try:
        响应 = requests.get(网址, params=参数, timeout=60)
        响应.raise_for_status()  # 非 200 状态会抛出异常
        return 响应.text
    except Exception as e:
        if 异常返回:
            return f"处理失败: {e}"
        return None
