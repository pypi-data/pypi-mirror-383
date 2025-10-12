# godot-event

GodotEvent utilities - Enhanced Godot-style input event system for Python.

[中文文档](docs/README_CN.md) | English

## 🚀 Features

- **Multi-key binding**: Support binding multiple keys to the same event
- **Combo key support**: Full combo key support (Ctrl+S, Shift+F12, etc.)
- **Windows keyboard support**: All Windows keyboard keys supported
- **Performance optimized**: Memory and performance optimizations
- **Robust error handling**: Comprehensive error handling system
- **Pygame integration**: Seamless integration with Pygame

## 📦 Installation

```bash
# Basic installation
pip install godot-event

# With Pygame support
pip install godot-event[pygame]
```

## 🚀 Quick Start

```python
from godot_event import CreateInputSystem

# Create input system
input_system = CreateInputSystem()

# Create event and bind keys
input_system.EventCreate("jump")
input_system.EventBindKey("jump", "Space")
input_system.EventBindKey("jump", "W")

# Event listening
@input_system.on("jump")
def on_jump(event):
    print("Jump event triggered!")

# Check event state
if input_system.IsEventPressed("jump"):
    print("Jumping...")
```

## 📚 Documentation

For complete documentation with detailed examples and API reference, see:
- [中文文档](docs/README_CN.md) - Complete Chinese documentation
- `examples/` directory - Practical usage examples

## 🧪 Examples

Check the `examples/` directory for complete working examples.

## 🔧 Advanced Features

- Performance monitoring and optimization
- Comprehensive error handling
- Memory optimization
- Type hints and modular design

## 📄 License

MIT License - See LICENSE file for details.