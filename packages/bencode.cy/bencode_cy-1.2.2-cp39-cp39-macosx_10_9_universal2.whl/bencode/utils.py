import functools
import time


def timeit(f):
    @functools.wraps(f)
    def wapper(*arg, **kargs):
        now_time = time.time()
        res = f(*arg, **kargs)
        end_time = time.time()
        print(f"spend {end_time - now_time}")
        return res

    return wapper
