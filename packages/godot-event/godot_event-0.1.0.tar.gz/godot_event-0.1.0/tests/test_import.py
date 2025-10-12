def test_import():
    import godot_event
    assert hasattr(godot_event, "__version__")