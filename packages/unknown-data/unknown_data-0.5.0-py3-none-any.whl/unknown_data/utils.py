import functools
import tracemalloc
from typing import Callable, Any

def memory_tracker(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        tracemalloc.start()
        
        # 함수 실행 전 메모리 사용량
        snap_before = tracemalloc.take_snapshot()
        
        result = func(*args, **kwargs)
        
        # 함수 실행 후 메모리 사용량
        snap_after = tracemalloc.take_snapshot()
        
        tracemalloc.stop()
        
        top_stats = snap_after.compare_to(snap_before, 'lineno')
        
        instance = args[0]
        logger = getattr(instance, 'logger', None)
        
        if logger:
            logger.log(f"Memory usage for {func.__name__}:")
            total_allocated = sum(stat.size for stat in top_stats) / 1024
            logger.log(f"Total allocated memory: {total_allocated:.2f} KiB")
            
            # 가장 많이 사용된 5개 라인 출력
            for stat in top_stats[:5]:
                logger.log(str(stat))
        
        return result
    return wrapper
