import time
from functools import wraps


def timeit(func):
    """
    计算函数执行时间
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}执行时间: {end - start:.4f}秒")
        return result

    return wrapper
