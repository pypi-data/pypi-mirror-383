import requests


def 发送_POST请求(网址, 数据, 异常返回=False):
    """
    功能：
        向指定网址发送一个 HTTP POST 请求，并在成功时返回响应文本内容。
        如果请求失败，可以选择返回 None 或错误信息字符串。

    参数：
        - 网址 (str)：
            请求目标的完整 URL，例如 "https://www.example.com/api"。
        - 数据 (dict)：
            要随 POST 请求一起发送的表单数据，字典形式。
            例如 {"username": "admin", "password": "123456"}。
        - 异常返回 (bool)：
            控制异常时的返回结果。
            * False（默认）：出现异常时返回 None。
            * True：出现异常时返回错误信息字符串（形如 "处理失败: 错误描述"）。

    返回：
        - str：
            请求成功时返回响应文本（可能是 HTML、JSON 字符串等）。
        - str：
            当异常返回=True 且请求失败时，返回错误描述字符串。
        - None：
            当异常返回=False 且请求失败时，返回 None。

    异常处理逻辑：
        1. 状态码：非 200 响应会触发 HTTPError 异常。
        2. 网络错误：如 DNS 解析失败、连接错误等，都会被捕获。
        3. 默认超时未设置，若目标长时间无响应可能会卡住。

    示例：
        >>> 内容 = 发送_POST请求("https://httpbin.org/post", {"k": "v"})
        >>> print(内容[:100])
        "{\n  \"args\": {}, \n  \"data\": \"\", \n  \"form\": {\"k\": \"v\"}, ..."

        >>> 内容 = 发送_POST请求("https://xx.invalid", {"k": "v"}, 异常返回=True)
        >>> print(内容)
        "处理失败: HTTPSConnectionPool(..."

    注意事项：
        - 默认无超时设置，如需避免长时间卡住，可在代码里加 timeout 参数。
        - 仅支持发送表单数据（application/x-www-form-urlencoded）。
        - 如果需要发送 JSON，请手动修改为 `requests.post(网址, json=数据)`。
    """
    try:
        响应 = requests.post(网址, data=数据)
        响应.raise_for_status()  # 非 200 会抛异常
        return 响应.text
    except Exception as e:
        if 异常返回:
            return f"处理失败: {e}"
        return None
