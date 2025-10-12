"""
错误处理模块
提供统一的错误处理机制
"""

import warnings
import logging
from typing import Any, Callable, Optional


class GodotEventError(Exception):
    """GodotEvent库基础异常"""
    pass


class InputSystemError(GodotEventError):
    """输入系统异常"""
    pass


class EventError(GodotEventError):
    """事件系统异常"""
    pass


class PygameIntegrationError(GodotEventError):
    """Pygame集成异常"""
    pass


def setup_logging(level: int = logging.WARNING) -> None:
    """设置日志记录"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def error_handler(func: Callable) -> Callable:
    """通用错误处理装饰器"""
    def wrapper(*args, **kwargs) -> Optional[Any]:
        try:
            return func(*args, **kwargs)
        except GodotEventError as e:
            # 库内部异常，记录但不重新抛出
            logging.warning(f"GodotEvent操作警告: {e}")
            return None
        except Exception as e:
            # 外部异常，记录并重新抛出
            logging.error(f"GodotEvent操作错误: {e}")
            raise
    return wrapper


def validate_event_name(event_name: str) -> bool:
    """验证事件名称有效性"""
    if not event_name or not isinstance(event_name, str):
        raise EventError("事件名称必须是非空字符串")
    
    if len(event_name) > 100:
        raise EventError("事件名称过长（最大100字符）")
    
    # 检查是否包含非法字符
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in event_name for char in illegal_chars):
        raise EventError(f"事件名称包含非法字符: {illegal_chars}")
    
    return True


def validate_key_name(key: str) -> bool:
    """验证按键名称有效性"""
    if not key or not isinstance(key, str):
        raise InputSystemError("按键名称必须是非空字符串")
    
    if len(key) > 50:
        raise InputSystemError("按键名称过长（最大50字符）")
    
    return True


def safe_execute(func: Callable, default_return: Any = None) -> Any:
    """安全执行函数，捕获所有异常"""
    try:
        return func()
    except Exception as e:
        logging.error(f"安全执行失败: {e}")
        return default_return


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._metrics = {}
        self._enabled = True
    
    def measure_time(self, operation_name: str):
        """测量执行时间的装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)
                
                import time
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    self._metrics[operation_name] = {
                        'time': elapsed,
                        'count': self._metrics.get(operation_name, {}).get('count', 0) + 1
                    }
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    self._metrics[operation_name] = {
                        'time': elapsed,
                        'error': str(e),
                        'count': self._metrics.get(operation_name, {}).get('count', 0) + 1
                    }
                    raise
            return wrapper
        return decorator
    
    def get_metrics(self) -> dict:
        """获取性能指标"""
        return self._metrics.copy()
    
    def reset_metrics(self) -> None:
        """重置性能指标"""
        self._metrics.clear()
    
    def enable(self) -> None:
        """启用性能监控"""
        self._enabled = True
    
    def disable(self) -> None:
        """禁用性能监控"""
        self._enabled = False


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()