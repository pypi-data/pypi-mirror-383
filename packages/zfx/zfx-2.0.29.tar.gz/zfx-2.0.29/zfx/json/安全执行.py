import functools
from typing import Any, Callable, TypeVar, Optional

F = TypeVar("F", bound=Callable[..., Any])

def 安全执行(默认返回: Any = None, *, 打日志: Optional[Callable[[Exception], None]] = None) -> Callable[[F], F]:
    """装饰器：捕获内部异常并返回默认值，防止异常数据导致程序崩溃。

    Args:
        默认返回: 异常发生时的返回值（常用 [] / {} / None）。
        打日志: 可选日志函数，例如 lambda e: print(f"[JSON错误] {e}")。
    """
    def 装饰(func: F) -> F:
        @functools.wraps(func)
        def 包装(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if 打日志:
                    try:
                        打日志(e)
                    except Exception:
                        pass
                return 默认返回
        return 包装  # type: ignore[return-value]
    return 装饰
