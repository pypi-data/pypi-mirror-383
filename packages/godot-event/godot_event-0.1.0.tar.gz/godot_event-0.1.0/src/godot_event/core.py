"""
godot_event 核心模块
事件系统基础类 - 优化版
"""

import time
from typing import Any, Callable, Dict, List, Optional, Set


class Event:
    """事件基类 - 性能优化版"""
    
    __slots__ = ('name', 'data', '_is_cancelled', 'timestamp')
    
    def __init__(self, name: str, data: Optional[Dict[str, Any]] = None):
        self.name = name
        self.data = data or {}
        self._is_cancelled = False
        self.timestamp = time.time()  # 添加时间戳用于性能分析
    
    def cancel(self) -> None:
        """取消事件"""
        self._is_cancelled = True
    
    @property
    def is_cancelled(self) -> bool:
        """检查事件是否被取消"""
        return self._is_cancelled
    
    def __repr__(self) -> str:
        return f"Event(name='{self.name}', cancelled={self._is_cancelled})"


class EventEmitter:
    """事件发射器 - 性能优化版"""
    
    __slots__ = ('_listeners', '_once_listeners')
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, Set[Callable]] = {}  # 一次性监听器单独管理
    
    def on(self, event_name: str, callback: Callable) -> None:
        """注册事件监听器"""
        if not callable(callback):
            raise TypeError("回调函数必须是可调用对象")
        
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
    
    def off(self, event_name: str, callback: Callable) -> None:
        """移除事件监听器"""
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
            except ValueError:
                pass  # 监听器不存在时静默处理
        
        # 同时移除一次性监听器
        if event_name in self._once_listeners:
            self._once_listeners[event_name].discard(callback)
    
    def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None) -> Event:
        """触发事件 - 性能优化版本"""
        event = Event(event_name, data)
        
        # 处理普通监听器
        if event_name in self._listeners:
            # 使用列表切片避免在迭代过程中修改列表
            listeners = self._listeners[event_name]
            i = 0
            while i < len(listeners):
                try:
                    callback = listeners[i]
                    callback(event)
                    i += 1
                except IndexError:
                    break  # 防止列表越界
                if event.is_cancelled:
                    break
        
        # 处理一次性监听器
        if event_name in self._once_listeners:
            once_callbacks = self._once_listeners[event_name].copy()
            for callback in once_callbacks:
                try:
                    callback(event)
                    self._once_listeners[event_name].discard(callback)
                except Exception:
                    # 移除出错的一次性监听器
                    self._once_listeners[event_name].discard(callback)
                if event.is_cancelled:
                    break
        
        return event
    
    def once(self, event_name: str, callback: Callable) -> None:
        """注册一次性事件监听器 - 优化版本"""
        if not callable(callback):
            raise TypeError("回调函数必须是可调用对象")
        
        if event_name not in self._once_listeners:
            self._once_listeners[event_name] = set()
        self._once_listeners[event_name].add(callback)
    
    def remove_all_listeners(self, event_name: Optional[str] = None) -> None:
        """移除所有监听器"""
        if event_name is None:
            self._listeners.clear()
            self._once_listeners.clear()
        else:
            self._listeners.pop(event_name, None)
            self._once_listeners.pop(event_name, None)
    
    def listener_count(self, event_name: str) -> int:
        """获取指定事件的监听器数量"""
        count = 0
        if event_name in self._listeners:
            count += len(self._listeners[event_name])
        if event_name in self._once_listeners:
            count += len(self._once_listeners[event_name])
        return count
    
    def event_names(self) -> List[str]:
        """获取所有已注册的事件名称"""
        events = set(self._listeners.keys())
        events.update(self._once_listeners.keys())
        return list(events)