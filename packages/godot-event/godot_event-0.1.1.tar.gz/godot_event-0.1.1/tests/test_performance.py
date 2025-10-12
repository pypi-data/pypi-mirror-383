"""
性能测试模块
测试godot_event库的性能表现
"""

import time
import pytest
from godot_event import InputSystem, EventEmitter, profile_function


class TestPerformance:
    """性能测试类"""
    
    def test_event_emitter_performance(self):
        """测试事件发射器性能"""
        emitter = EventEmitter()
        
        # 添加大量监听器
        callback_count = 1000
        callbacks = []
        
        for i in range(callback_count):
            def callback(event):
                pass
            callbacks.append(callback)
            emitter.on("test_event", callback)
        
        # 性能测试
        start_time = time.time()
        for i in range(1000):
            emitter.emit("test_event")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"事件发射器性能: {execution_time:.4f}秒 (1000事件 × {callback_count}监听器)")
        assert execution_time < 1.0  # 应该在1秒内完成
    
    def test_input_system_performance(self):
        """测试输入系统性能"""
        input_system = InputSystem()
        
        # 创建大量事件绑定
        event_count = 100
        for i in range(event_count):
            event_name = f"event_{i}"
            input_system.MapAction(event_name, ["A", "B", "C", f"F{i % 12 + 1}"])
        
        # 模拟大量按键事件
        key_events = []
        for i in range(1000):
            key_events.append({"key": "A", "pressed": True})
            key_events.append({"key": "A", "pressed": False})
        
        # 性能测试
        start_time = time.time()
        input_system.UpdateInput(key_events)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"输入系统性能: {execution_time:.6f}秒 (处理1000个按键事件)")
        assert execution_time < 0.1  # 应该在0.1秒内完成
    
    @profile_function
    def test_combo_key_performance(self):
        """测试组合键性能（带性能分析）"""
        input_system = InputSystem()
        
        # 创建复杂的组合键绑定
        combinations = [
            "Ctrl+A", "Ctrl+Shift+A", "Alt+Shift+F1", 
            "Ctrl+Alt+Delete", "Win+Shift+S"
        ]
        
        for i, combo in enumerate(combinations):
            input_system.EventBindKey(f"combo_{i}", combo)
        
        # 模拟组合键事件序列
        events = []
        # Ctrl按下
        events.append({"key": "Ctrl", "pressed": True})
        # Shift按下
        events.append({"key": "Shift", "pressed": True})
        # A按下
        events.append({"key": "A", "pressed": True})
        # A释放
        events.append({"key": "A", "pressed": False})
        # Shift释放
        events.append({"key": "Shift", "pressed": False})
        # Ctrl释放
        events.append({"key": "Ctrl", "pressed": False})
        
        # 性能测试
        start_time = time.time()
        for _ in range(100):  # 重复100次
            input_system.UpdateInput(events)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"组合键性能: {execution_time:.4f}秒 (100次组合键检测)")
        assert execution_time < 0.5


def memory_usage_test():
    """内存使用测试"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 创建大量事件系统
    systems = []
    for i in range(100):
        system = InputSystem()
        system.MapAction(f"action_{i}", ["A", "B", "C", "D"])
        systems.append(system)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"内存使用: 初始{initial_memory:.2f}MB -> 最终{final_memory:.2f}MB")
    print(f"内存增加: {memory_increase:.2f}MB (100个输入系统)")
    
    # 清理
    del systems
    return memory_increase


if __name__ == "__main__":
    # 运行性能测试
    test = TestPerformance()
    
    print("=== GodotEvent 性能测试 ===")
    
    test.test_event_emitter_performance()
    test.test_input_system_performance()
    test.test_combo_key_performance()
    
    # 内存测试（可选）
    try:
        memory_increase = memory_usage_test()
        print(f"✅ 性能测试完成")
    except ImportError:
        print("⚠️  跳过内存测试（需要psutil库）")
        print(f"✅ 性能测试完成")