"""
Pygame集成模块
提供与Pygame的输入系统集成
"""

import pygame
from typing import Dict, List
from .input_system import InputSystem


class PygameInputAdapter:
    """Pygame输入适配器"""
    
    # Pygame按键到基础字符串映射（增强版）
    BASE_KEY_MAPPING = {
        # 字母键
        pygame.K_a: "A", pygame.K_b: "B", pygame.K_c: "C", pygame.K_d: "D",
        pygame.K_e: "E", pygame.K_f: "F", pygame.K_g: "G", pygame.K_h: "H",
        pygame.K_i: "I", pygame.K_j: "J", pygame.K_k: "K", pygame.K_l: "L",
        pygame.K_m: "M", pygame.K_n: "N", pygame.K_o: "O", pygame.K_p: "P",
        pygame.K_q: "Q", pygame.K_r: "R", pygame.K_s: "S", pygame.K_t: "T",
        pygame.K_u: "U", pygame.K_v: "V", pygame.K_w: "W", pygame.K_x: "X",
        pygame.K_y: "Y", pygame.K_z: "Z",
        
        # 数字键
        pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3",
        pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7",
        pygame.K_8: "8", pygame.K_9: "9",
        
        # 功能键
        pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3", pygame.K_F4: "F4",
        pygame.K_F5: "F5", pygame.K_F6: "F6", pygame.K_F7: "F7", pygame.K_F8: "F8",
        pygame.K_F9: "F9", pygame.K_F10: "F10", pygame.K_F11: "F11", pygame.K_F12: "F12",
        
        # 方向键
        pygame.K_UP: "Up", pygame.K_DOWN: "Down", 
        pygame.K_LEFT: "Left", pygame.K_RIGHT: "Right",
        
        # 特殊键
        pygame.K_SPACE: "Space", pygame.K_RETURN: "Enter", pygame.K_ESCAPE: "Escape",
        pygame.K_TAB: "Tab", pygame.K_CAPSLOCK: "CapsLock", pygame.K_BACKSPACE: "Backspace",
        pygame.K_DELETE: "Delete", pygame.K_INSERT: "Insert",
        pygame.K_HOME: "Home", pygame.K_END: "End", pygame.K_PAGEUP: "PageUp", pygame.K_PAGEDOWN: "PageDown",
        pygame.K_PRINTSCREEN: "PrintScreen", pygame.K_SCROLLLOCK: "ScrollLock", pygame.K_PAUSE: "Pause",
        
        # 修饰键
        pygame.K_LSHIFT: "Shift", pygame.K_RSHIFT: "Shift",
        pygame.K_LCTRL: "Ctrl", pygame.K_RCTRL: "Ctrl",
        pygame.K_LALT: "Alt", pygame.K_RALT: "Alt",
        pygame.K_LSUPER: "Win", pygame.K_RSUPER: "Win",
        
        # 数字小键盘
        pygame.K_KP0: "Numpad0", pygame.K_KP1: "Numpad1", pygame.K_KP2: "Numpad2",
        pygame.K_KP3: "Numpad3", pygame.K_KP4: "Numpad4", pygame.K_KP5: "Numpad5",
        pygame.K_KP6: "Numpad6", pygame.K_KP7: "Numpad7", pygame.K_KP8: "Numpad8",
        pygame.K_KP9: "Numpad9", pygame.K_KP_MULTIPLY: "NumpadMultiply", pygame.K_KP_PLUS: "NumpadAdd",
        pygame.K_KP_MINUS: "NumpadSubtract", pygame.K_KP_PERIOD: "NumpadDecimal", pygame.K_KP_DIVIDE: "NumpadDivide",
        pygame.K_KP_ENTER: "NumpadEnter",
    }
    
    def __init__(self, input_system: InputSystem):
        self.input_system = input_system
    
    def process_pygame_events(self) -> None:
        """处理Pygame事件并更新输入系统（支持大小写区分）- 性能优化版本"""
        key_events = []
        
        # 批量获取所有事件
        events = pygame.event.get()
        if not events:
            return  # 没有事件直接返回
        
        # 获取当前修饰键状态（一次性获取）
        modifiers = pygame.key.get_mods()
        shift_pressed = modifiers & pygame.KMOD_SHIFT
        caps_lock = modifiers & pygame.KMOD_CAPS
        
        # 预计算字母键范围
        letter_key_range = range(pygame.K_a, pygame.K_z + 1)
        
        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                # 基础按键映射
                base_key = self.BASE_KEY_MAPPING.get(event.key, f"key_{event.key}")
                
                # 处理大小写：字母键根据Shift和Caps Lock状态调整
                if event.key in letter_key_range:
                    # 优化大小写转换逻辑
                    if shift_pressed ^ caps_lock:  # 使用异或简化逻辑
                        key_name = base_key.upper()
                    else:
                        key_name = base_key.lower()
                else:
                    key_name = base_key
                
                pressed = event.type == pygame.KEYDOWN
                key_events.append({
                    "key": key_name, 
                    "pressed": pressed, 
                    "scancode": event.scancode,
                    "shift": shift_pressed,
                    "caps": caps_lock
                })
        
        # 批量更新输入系统
        if key_events:
            self.input_system.UpdateInput(key_events)
    
    def setup_default_bindings(self) -> None:
        """设置默认的Godot风格按键绑定"""
        # 移动控制
        self.input_system.MapAction("move_up", ["w", "W", "Up"])
        self.input_system.MapAction("move_down", ["s", "S", "Down"])
        self.input_system.MapAction("move_left", ["a", "A", "Left"])
        self.input_system.MapAction("move_right", ["d", "D", "Right"])
        
        # 动作控制
        self.input_system.MapAction("jump", ["Space", "w", "Up"])
        self.input_system.MapAction("attack", ["z", "x", "c"])
        self.input_system.MapAction("interact", ["e", "f"])
        
        # 系统控制
        self.input_system.MapAction("pause", ["Escape", "p"])
        self.input_system.MapAction("menu", ["m", "Tab"])


def create_headless_demo() -> None:
    """创建无界面Pygame演示程序（仅控制台输出）"""
    pygame.init()
    
    # 创建输入系统和适配器
    input_system = InputSystem()
    adapter = PygameInputAdapter(input_system)
    adapter.setup_default_bindings()
    
    # 注册事件监听器
    def on_move(event):
        if event.pressed:
            print(f"移动事件: {event.name} - 按键: {event.key}")
    
    def on_jump(event):
        if event.pressed:
            print("跳跃!")
    
    def on_system(event):
        if event.pressed:
            print(f"系统事件: {event.name}")
    
    input_system.on("move_up", on_move)
    input_system.on("move_down", on_move)
    input_system.on("move_left", on_move)
    input_system.on("move_right", on_move)
    input_system.on("jump", on_jump)
    input_system.on("pause", on_system)
    input_system.on("menu", on_system)
    
    print("=== GodotEvent Pygame 无界面演示 ===")
    print("监听键盘输入（按Escape退出）")
    print("支持的按键: WASD, 方向键, 空格, Escape, P, M, Tab")
    print()
    
    # 使用pygame.event.get()但不创建窗口
    running = True
    while running:
        # 处理输入事件
        adapter.process_pygame_events()
        
        # 检查退出条件
        if input_system.IsEventPressed("pause"):
            running = False
        
        # 避免CPU占用过高
        pygame.time.wait(10)
    
    print("演示结束")
    pygame.quit()


if __name__ == "__main__":
    create_headless_demo()