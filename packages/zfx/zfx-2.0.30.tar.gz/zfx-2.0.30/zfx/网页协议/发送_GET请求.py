import requests


def 发送_GET请求(网址, 参数=None, 异常返回=False):
    """
    功能：
        发送一个 HTTP GET 请求，并在成功时返回响应对象。
        如果出现异常，可以根据参数选择返回 None 或错误信息。

    参数：
        - 网址 (str)：
            要访问的完整 URL 地址，例如 "https://www.example.com"。
        - 参数 (dict | None)：
            可选的查询参数，会自动拼接到 URL 中。例如 {"q": "python"}。
            默认为 None，即不附加额外参数。
        - 异常返回 (bool)：
            控制出现异常时的返回行为。
            * 如果为 False（默认值）：出现任何异常时返回 None。
            * 如果为 True：出现异常时返回错误信息字符串（例如 "处理失败: 连接超时"）。

    返回：
        - requests.Response 对象：
            当请求成功并且状态码为 200 时，返回完整响应对象，可以通过
            响应.text、响应.json()、响应.status_code 等方式获取内容。
        - str：
            当异常返回=True 且请求失败时，返回错误描述字符串。
        - None：
            当异常返回=False 且请求失败时，返回 None。

    异常处理逻辑：
        1. 设置超时时间为 60 秒。如果超过 60 秒没有响应，会触发 Timeout 异常。
        2. 如果返回的状态码不是 200，会触发 HTTPError 异常。
        3. 所有异常都会进入 except 块，根据 异常返回 参数决定返回 None 或错误信息。

    注意事项：
        - 超时时间固定为 60 秒，不可配置。
        - 函数只支持 GET 请求；POST/PUT 等需要单独实现。
        - 默认只认为状态码 200 是成功，其他状态会被视为异常。
    """
    try:
        响应 = requests.get(网址, params=参数, timeout=60)
        响应.raise_for_status()  # 非 200 状态会抛出 HTTPError
        return 响应
    except Exception as e:
        if 异常返回:
            return f"处理失败: {e}"
        return None
