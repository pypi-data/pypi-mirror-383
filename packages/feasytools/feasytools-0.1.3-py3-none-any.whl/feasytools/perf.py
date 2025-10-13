from collections import defaultdict
from functools import wraps
import time


def time2str(tspan:float):
    tspan = round(tspan)
    s = tspan % 60
    m = tspan // 60 % 60
    h = tspan // 3600
    return f"{h:02}:{m:02}:{s:02}"


class _perf:
    __RES = defaultdict(float)

    def __call__(self, func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            _perf.__RES[func.__name__] += execution_time
            return result

        return func_wrapper
    
    @property
    def results(self):
        return self.__RES
    
    def report(self):
        print("Performance Report:")
        for k, v in self.__RES.items():
            if v > 1:
                print(f"  {k}: {v:.3f} s")
            elif v > 1e-3:
                print(f"  {k}: {v*1e3:.3f} ms")
            elif v > 1e-6:
                print(f"  {k}: {v*1e6:.3f} µs")
            else:
                print(f"  {k}: {v*1e9:.3f} ns")
                

FEasyTimer = _perf()


__all__ = ["FEasyTimer", "time2str"]