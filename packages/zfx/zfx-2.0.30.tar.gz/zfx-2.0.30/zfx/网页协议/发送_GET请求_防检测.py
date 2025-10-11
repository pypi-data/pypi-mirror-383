import time
import requests


def 发送_GET请求_防检测(网址, 过检等级=3, 参数=None, 异常返回=False):
    """
    功能：
        向指定网址发送一个 HTTP GET 请求，并在成功时返回响应对象。
        与普通 GET 请求的区别在于：函数会在请求完成后额外 sleep，
        以降低访问频率、模拟人工操作，从而减轻被目标网站识别为“爬虫/自动化”的风险。

    参数：
        - 网址 (str)：
            目标 URL，例如 "https://www.example.com"。
        - 过检等级 (int)：
            控制请求后的等待时间（单位：秒）。
            * 1 = 最小延迟，适合低强度访问。
            * 2、3、... = 等待秒数逐渐增加，等级越高，延迟越久，被检测风险越低。
            默认值为 3，即请求后等待 3 秒。
        - 参数 (dict | None)：
            GET 请求的查询参数，字典形式，会自动拼接到 URL。
            默认为 None。
        - 异常返回 (bool)：
            控制异常时的返回结果。
            * False（默认）：出现异常时返回 None。
            * True：出现异常时返回错误描述字符串。

    返回：
        - requests.Response 对象：
            请求成功时返回完整响应对象。
        - str：
            当异常返回=True 且请求失败时，返回错误信息字符串。
        - None：
            当异常返回=False 且请求失败时，返回 None。

    异常处理逻辑：
        1. 超时：超过 60 秒未响应会触发 Timeout。
        2. 状态码：非 200 会触发 HTTPError。
        3. 其他错误（如 DNS/连接错误）也会被捕获。

    示例：
        >>> r = 发送_GET请求_防检测("https://httpbin.org/get")
        >>> print(r.status_code)
        200

        >>> r = 发送_GET请求_防检测("https://xx.invalid", 异常返回=True)
        >>> print(r)
        "处理失败: HTTPSConnectionPool(..."

    注意事项：
        - 延迟时间直接取决于 过检等级 的数值，过大可能显著降低爬取效率。
        - 仅支持 GET 请求；POST/PUT 等需另写函数。
        - 本函数不会随机化等待时间，如需更高拟人化效果，可以改成随机 sleep。
    """
    try:
        响应 = requests.get(网址, params=参数, timeout=60)
        响应.raise_for_status()  # 非 200 会抛异常
        time.sleep(int(过检等级))  # 请求完成后等待，模拟人工延迟
        return 响应
    except Exception as e:
        if 异常返回:
            return f"处理失败: {e}"
        return None
