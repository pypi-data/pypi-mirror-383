"""
Godot风格输入事件系统 - 增强版
支持Windows键盘所有按键、组合键和特殊键
"""

import time
import warnings
from typing import Any, Callable, Dict, List, Optional, Set, Union, Tuple
from .core import Event, EventEmitter


class InputEvent(Event):
    """增强输入事件"""
    
    def __init__(self, name: str, key: str, pressed: bool, 
                 modifiers: Optional[Dict[str, bool]] = None, 
                 data: Optional[Dict[str, Any]] = None):
        super().__init__(name, data)
        self.key = key
        self.pressed = pressed
        self.modifiers = modifiers or {}
        self.timestamp = time.time()
        self.is_combo = len(self.modifiers) > 0
    
    def has_modifier(self, modifier: str) -> bool:
        """检查是否包含指定修饰键"""
        return self.modifiers.get(modifier, False)
    
    def get_combo_string(self) -> str:
        """获取组合键字符串表示"""
        if not self.is_combo:
            return self.key
        
        mods = []
        for mod, pressed in self.modifiers.items():
            if pressed:
                mods.append(mod)
        mods.sort()
        return "+".join(mods + [self.key])


class KeyCodes:
    """Windows键盘按键代码和名称定义"""
    
    # 字母键
    LETTERS = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    
    # 数字键
    NUMBERS = [str(i) for i in range(10)]
    
    # 功能键
    FUNCTION_KEYS = [f"F{i}" for i in range(1, 25)]  # F1-F24
    
    # 方向键
    ARROW_KEYS = ["Up", "Down", "Left", "Right"]
    
    # 特殊键
    SPECIAL_KEYS = [
        "Escape", "Tab", "CapsLock", "Shift", "Ctrl", "Alt", 
        "Space", "Enter", "Backspace", "Delete", "Insert",
        "Home", "End", "PageUp", "PageDown",
        "PrintScreen", "ScrollLock", "Pause",
        "NumLock", "Clear"
    ]
    
    # 数字小键盘
    NUMPAD_KEYS = [
        "Numpad0", "Numpad1", "Numpad2", "Numpad3", "Numpad4",
        "Numpad5", "Numpad6", "Numpad7", "Numpad8", "Numpad9",
        "NumpadMultiply", "NumpadAdd", "NumpadSubtract", 
        "NumpadDecimal", "NumpadDivide", "NumpadEnter"
    ]
    
    # 媒体键
    MEDIA_KEYS = [
        "VolumeMute", "VolumeDown", "VolumeUp",
        "MediaPlayPause", "MediaStop", 
        "MediaNextTrack", "MediaPrevTrack"
    ]
    
    # 修饰键
    MODIFIER_KEYS = ["Shift", "Ctrl", "Alt", "AltGr", "Win"]
    
    # 所有按键
    ALL_KEYS = LETTERS + NUMBERS + FUNCTION_KEYS + ARROW_KEYS + SPECIAL_KEYS + NUMPAD_KEYS + MEDIA_KEYS
    
    @classmethod
    def is_valid_key(cls, key: str) -> bool:
        """检查是否为有效按键"""
        return key in cls.ALL_KEYS or (len(key) == 1 and key.isalpha())
    
    @classmethod
    def normalize_key(cls, key: str) -> str:
        """标准化按键名称"""
        if len(key) == 1 and key.isalpha():
            return key.upper()
        return key


class ComboKey:
    """组合键处理类"""
    
    def __init__(self, key_string: str):
        self.original_string = key_string
        self.modifiers = set()
        self.base_key = ""
        self._parse_combo(key_string)
    
    def _parse_combo(self, key_string: str) -> None:
        """解析组合键字符串"""
        parts = key_string.split('+')
        if len(parts) == 1:
            self.base_key = KeyCodes.normalize_key(parts[0])
            return
        
        # 处理修饰键和基础键
        for part in parts[:-1]:
            mod = part.strip().lower()
            if mod in ['shift', 'ctrl', 'alt', 'win']:
                self.modifiers.add(mod)
            else:
                warnings.warn(f"未知修饰键: {part}")
        
        self.base_key = KeyCodes.normalize_key(parts[-1])
    
    def matches(self, key: str, modifiers: Dict[str, bool]) -> bool:
        """检查是否匹配当前按键和修饰键状态"""
        if key != self.base_key:
            return False
        
        # 检查所有要求的修饰键是否都按下
        for mod in self.modifiers:
            if not modifiers.get(mod, False):
                return False
        
        # 检查是否有额外的修饰键按下（严格匹配）
        for mod, pressed in modifiers.items():
            if pressed and mod not in self.modifiers:
                return False
        
        return True
    
    def __str__(self) -> str:
        if not self.modifiers:
            return self.base_key
        mods = sorted(self.modifiers)
        return "+".join([mod.capitalize() for mod in mods] + [self.base_key])


class InputSystem(EventEmitter):
    """增强版Godot风格输入系统 - 性能优化版"""
    
    __slots__ = ('_key_bindings', '_combo_bindings', '_event_bindings', 
                 '_key_states', '_modifier_states', '_just_pressed', 
                 '_just_released', '_conflict_warnings', '_performance_stats')
    
    def __init__(self):
        super().__init__()
        self._key_bindings: Dict[str, Set[str]] = {}  # 事件名 -> 按键集合（字符串形式）
        self._combo_bindings: Dict[str, List[ComboKey]] = {}  # 事件名 -> ComboKey列表
        self._event_bindings: Dict[str, str] = {}     # 基础按键 -> 事件名（用于快速查找）
        self._key_states: Dict[str, bool] = {}        # 按键当前状态
        self._modifier_states: Dict[str, bool] = {    # 修饰键状态
            'shift': False, 'ctrl': False, 'alt': False, 'win': False
        }
        self._just_pressed: Set[str] = set()          # 刚刚按下的按键
        self._just_released: Set[str] = set()         # 刚刚释放的按键
        self._conflict_warnings: Set[str] = set()     # 已警告的冲突
        self._performance_stats: Dict[str, Any] = {   # 性能统计
            'update_count': 0,
            'event_trigger_count': 0,
            'last_update_time': 0.0
        }
    
    def EventCreate(self, event_name: str) -> None:
        """创建新的事件"""
        if event_name not in self._key_bindings:
            self._key_bindings[event_name] = set()
            self._combo_bindings[event_name] = []
    
    def EventBindKey(self, event_name: str, key: str) -> None:
        """将按键绑定到事件（支持组合键）"""
        self.EventCreate(event_name)
        
        # 创建ComboKey对象
        combo = ComboKey(key)
        
        # 检查冲突（仅警告，不阻止）
        self._check_key_conflict(event_name, combo)
        
        # 添加到绑定
        key_str = str(combo)
        self._key_bindings[event_name].add(key_str)
        self._combo_bindings[event_name].append(combo)
        
        # 如果是单键，添加到快速查找
        if not combo.modifiers:
            if combo.base_key in self._event_bindings and self._event_bindings[combo.base_key] != event_name:
                warnings.warn(f"按键冲突: {combo.base_key} 已绑定到 {self._event_bindings[combo.base_key]}，现在绑定到 {event_name}")
            self._event_bindings[combo.base_key] = event_name
    
    def EventBindKeys(self, event_name: str, keys: List[str]) -> None:
        """将多个按键绑定到同一事件"""
        for key in keys:
            self.EventBindKey(event_name, key)
    
    def _check_key_conflict(self, event_name: str, combo: ComboKey) -> None:
        """检查按键冲突（仅警告）"""
        conflict_key = str(combo)
        if conflict_key in self._conflict_warnings:
            return
        
        # 检查是否已绑定到其他事件
        for existing_event, combos in self._combo_bindings.items():
            if existing_event == event_name:
                continue
            for existing_combo in combos:
                if str(existing_combo) == conflict_key:
                    warning_msg = f"按键冲突警告: {conflict_key} 已绑定到事件 '{existing_event}'，现在也绑定到 '{event_name}'"
                    warnings.warn(warning_msg)
                    self._conflict_warnings.add(conflict_key)
                    return
    
    def GetEventKeys(self, event_name: str) -> List[str]:
        """获取绑定到事件的所有按键（字符串形式）"""
        return list(self._key_bindings.get(event_name, set()))
    
    def GetEventCombos(self, event_name: str) -> List[ComboKey]:
        """获取绑定到事件的所有组合键对象"""
        return self._combo_bindings.get(event_name, [])
    
    def IsEventPressed(self, event_name: str) -> bool:
        """检查事件是否被触发（任一绑定按键按下）- 性能优化版本"""
        if event_name not in self._combo_bindings:
            return False
        
        # 缓存修饰键状态避免重复计算
        current_modifiers = self._modifier_states
        
        for combo in self._combo_bindings[event_name]:
            if combo.matches(combo.base_key, current_modifiers):
                if self._key_states.get(combo.base_key, False):
                    return True
        return False
    
    def IsEventJustPressed(self, event_name: str) -> bool:
        """检查事件是否刚刚被触发"""
        if event_name not in self._combo_bindings:
            return False
        
        for combo in self._combo_bindings[event_name]:
            if combo.matches(combo.base_key, self._modifier_states):
                if self.IsKeyJustPressed(combo.base_key):
                    return True
        return False
    
    def IsEventJustReleased(self, event_name: str) -> bool:
        """检查事件是否刚刚被释放"""
        if event_name not in self._combo_bindings:
            return False
        
        for combo in self._combo_bindings[event_name]:
            if combo.matches(combo.base_key, self._modifier_states):
                if self.IsKeyJustReleased(combo.base_key):
                    return True
        return False
    
    # 基础按键检测方法
    def IsKeyPressed(self, key: str) -> bool:
        """检查按键是否按下"""
        normalized = KeyCodes.normalize_key(key)
        return self._key_states.get(normalized, False)
    
    def IsKeyJustPressed(self, key: str) -> bool:
        """检查按键是否刚刚按下"""
        normalized = KeyCodes.normalize_key(key)
        return normalized in self._just_pressed
    
    def IsKeyJustReleased(self, key: str) -> bool:
        """检查按键是否刚刚释放"""
        normalized = KeyCodes.normalize_key(key)
        return normalized in self._just_released
    
    def IsModifierPressed(self, modifier: str) -> bool:
        """检查修饰键是否按下"""
        return self._modifier_states.get(modifier.lower(), False)
    
    def GetPressedKeys(self) -> List[str]:
        """获取所有按下的按键"""
        return [key for key, pressed in self._key_states.items() if pressed]
    
    def GetActiveModifiers(self) -> Dict[str, bool]:
        """获取当前激活的修饰键"""
        return self._modifier_states.copy()
    
    # 输入更新方法
    def UpdateInput(self, key_events: List[Dict[str, Any]]) -> None:
        """更新输入状态（处理按键事件列表）- 性能优化版本"""
        if not key_events:
            return  # 空事件列表直接返回
        
        # 性能统计
        start_time = time.time()
        self._performance_stats['update_count'] += 1
        
        self._just_pressed.clear()
        self._just_released.clear()
        
        # 批量处理事件，减少函数调用开销
        normalized_events = []
        for event_data in key_events:
            try:
                key = event_data.get('key', '')
                pressed = event_data.get('pressed', False)
                normalized_key = KeyCodes.normalize_key(key)
                normalized_events.append((normalized_key, pressed, event_data))
            except Exception as e:
                warnings.warn(f"处理按键事件时出错: {e}")
                continue
        
        # 先更新修饰键状态
        self._update_modifier_states(key_events)
        
        # 批量处理按键状态更新
        for normalized_key, pressed, event_data in normalized_events:
            previous_state = self._key_states.get(normalized_key, False)
            
            # 更新状态
            self._key_states[normalized_key] = pressed
            
            # 检测刚刚按下/释放
            if pressed and not previous_state:
                self._just_pressed.add(normalized_key)
            elif not pressed and previous_state:
                self._just_released.add(normalized_key)
        
        # 批量触发事件（减少循环嵌套）
        self._batch_trigger_events(normalized_events)
        
        # 更新性能统计
        self._performance_stats['last_update_time'] = time.time() - start_time
    
    def _batch_trigger_events(self, normalized_events: List[tuple]) -> None:
        """批量触发事件 - 性能优化"""
        # 使用字典按按键分组事件
        events_by_key = {}
        for normalized_key, pressed, event_data in normalized_events:
            if normalized_key not in events_by_key:
                events_by_key[normalized_key] = []
            events_by_key[normalized_key].append((pressed, event_data))
        
        # 对每个按键批量处理
        for key, events in events_by_key.items():
            for pressed, event_data in events:
                self._trigger_matching_events(key, pressed, event_data)
    
    def _update_modifier_states(self, key_events: List[Dict[str, Any]]) -> None:
        """更新修饰键状态"""
        # 重置修饰键状态（基于当前事件）
        modifier_keys = {
            'shift': ['Shift', 'LShift', 'RShift'],
            'ctrl': ['Ctrl', 'LCtrl', 'RCtrl'], 
            'alt': ['Alt', 'LAlt', 'RAlt'],
            'win': ['Win', 'LWin', 'RWin']
        }
        
        for mod, keys in modifier_keys.items():
            self._modifier_states[mod] = any(
                event_data.get('pressed', False) and 
                KeyCodes.normalize_key(event_data.get('key', '')) in keys
                for event_data in key_events
            )
    
    def _trigger_matching_events(self, key: str, pressed: bool, event_data: Dict[str, Any]) -> None:
        """触发匹配的事件 - 性能优化版本"""
        # 使用集合避免重复触发
        triggered_events = set()
        
        # 性能优化：先检查快速查找表
        if not pressed and key in self._event_bindings:
            event_name = self._event_bindings[key]
            if event_name not in triggered_events:
                try:
                    input_event = InputEvent(
                        event_name, key, pressed, 
                        self._modifier_states.copy(), event_data
                    )
                    self.emit(event_name, input_event)
                    triggered_events.add(event_name)
                    self._performance_stats['event_trigger_count'] += 1
                except Exception as e:
                    warnings.warn(f"触发事件 {event_name} 时出错: {e}")
        
        # 检查所有事件的所有组合键
        for event_name, combos in self._combo_bindings.items():
            if event_name in triggered_events:
                continue  # 已触发过
                
            for combo in combos:
                if combo.matches(key, self._modifier_states):
                    if event_name not in triggered_events:
                        try:
                            input_event = InputEvent(
                                event_name, key, pressed, 
                                self._modifier_states.copy(), event_data
                            )
                            self.emit(event_name, input_event)
                            triggered_events.add(event_name)
                            self._performance_stats['event_trigger_count'] += 1
                        except Exception as e:
                            warnings.warn(f"触发事件 {event_name} 时出错: {e}")
    
    # 便捷方法：Godot风格映射
    def MapAction(self, action_name: str, keys: List[str]) -> None:
        """映射动作到多个按键（Godot风格）"""
        self.EventCreate(action_name)
        self.EventBindKeys(action_name, keys)
    
    def GetActionStrength(self, action_name: str) -> float:
        """获取动作强度"""
        return 1.0 if self.IsEventPressed(action_name) else 0.0
    
    def GetVector(self, negative_x: str, positive_x: str, 
                 negative_y: str, positive_y: str) -> Tuple[float, float]:
        """获取2D向量输入"""
        x = 0.0
        y = 0.0
        
        if self.IsEventPressed(positive_x):
            x += 1.0
        if self.IsEventPressed(negative_x):
            x -= 1.0
        if self.IsEventPressed(positive_y):
            y += 1.0
        if self.IsEventPressed(negative_y):
            y -= 1.0
            
        return (x, y)
    
    # 高级功能
    def ClearBindings(self, event_name: str) -> None:
        """清除事件的所有绑定"""
        if event_name in self._key_bindings:
            self._key_bindings[event_name].clear()
            self._combo_bindings[event_name].clear()
    
    def ListAllEvents(self) -> List[str]:
        """列出所有已创建的事件"""
        return list(self._key_bindings.keys())
    
    def GetEventInfo(self, event_name: str) -> Dict[str, Any]:
        """获取事件的详细信息"""
        if event_name not in self._key_bindings:
            return {}
        
        return {
            'name': event_name,
            'bindings': self.GetEventKeys(event_name),
            'combos': [str(combo) for combo in self.GetEventCombos(event_name)],
            'is_pressed': self.IsEventPressed(event_name),
            'is_just_pressed': self.IsEventJustPressed(event_name),
            'is_just_released': self.IsEventJustReleased(event_name)
        }


    # 性能监控方法
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return self._performance_stats.copy()
    
    def reset_performance_stats(self) -> None:
        """重置性能统计"""
        self._performance_stats = {
            'update_count': 0,
            'event_trigger_count': 0,
            'last_update_time': 0.0
        }
    
    def optimize_memory(self) -> None:
        """优化内存使用"""
        # 清理空的绑定
        empty_events = [name for name, bindings in self._key_bindings.items() if not bindings]
        for event_name in empty_events:
            del self._key_bindings[event_name]
            del self._combo_bindings[event_name]
        
        # 清理未使用的按键状态
        active_keys = set()
        for combos in self._combo_bindings.values():
            for combo in combos:
                active_keys.add(combo.base_key)
        
        # 保留活跃按键的状态
        keys_to_remove = [key for key in self._key_states if key not in active_keys]
        for key in keys_to_remove:
            del self._key_states[key]


# 便捷全局函数
def CreateInputSystem() -> InputSystem:
    """创建输入系统实例"""
    return InputSystem()


# 错误处理装饰器
def handle_input_errors(func):
    """输入系统错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            warnings.warn(f"输入系统操作出错: {e}")
            return None
    return wrapper