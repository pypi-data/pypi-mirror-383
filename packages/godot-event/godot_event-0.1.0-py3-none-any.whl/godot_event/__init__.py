"""
godot_event package
Godot风格的事件系统工具库 - 增强优化版
"""

__version__ = "0.1.0"

# 延迟导入以提高启动性能
def __getattr__(name):
    if name in {"Event", "EventEmitter"}:
        from .core import Event, EventEmitter
        return locals()[name]
    elif name in {"InputSystem", "InputEvent", "KeyCodes", "ComboKey", "CreateInputSystem"}:
        from .input_system import InputSystem, InputEvent, KeyCodes, ComboKey, CreateInputSystem
        return locals()[name]
    elif name == "PygameInputAdapter":
        from .pygame_integration import PygameInputAdapter
        return PygameInputAdapter
    elif name in {"GodotEventError", "InputSystemError", "EventError", "PygameIntegrationError",
                  "setup_logging", "error_handler", "validate_event_name", "validate_key_name",
                  "safe_execute", "performance_monitor"}:
        from .error_handling import (
            GodotEventError, InputSystemError, EventError, PygameIntegrationError,
            setup_logging, error_handler, validate_event_name, validate_key_name,
            safe_execute, performance_monitor
        )
        return locals()[name]
    else:
        raise AttributeError(f"module 'godot_event' has no attribute '{name}'")

# 显式导出公共API
__all__ = [
    "Event", "EventEmitter", 
    "InputSystem", "InputEvent", 
    "KeyCodes", "ComboKey", "CreateInputSystem",
    "PygameInputAdapter",
    "GodotEventError", "InputSystemError", "EventError", "PygameIntegrationError",
    "setup_logging", "error_handler", "validate_event_name", "validate_key_name",
    "safe_execute", "performance_monitor"
]

# 添加性能分析工具
try:
    import cProfile
    import pstats
    from io import StringIO
    
    def profile_function(func):
        """性能分析装饰器"""
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()
            
            # 输出性能分析结果
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # 显示前10个最耗时的函数
            print(f"性能分析 - {func.__name__}:")
            print(s.getvalue())
            
            return result
        return wrapper
    
    __all__.append("profile_function")
    
except ImportError:
    # 如果没有cProfile，提供空装饰器
    def profile_function(func):
        return func
    __all__.append("profile_function")

# 自动设置日志记录
try:
    from .error_handling import setup_logging
    setup_logging()
except ImportError:
    pass