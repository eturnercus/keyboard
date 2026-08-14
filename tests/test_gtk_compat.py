"""Тесты GTK4 совместимости."""


def test_new_press_gesture_available():
    from touchflow.gtk_compat import new_press_gesture

    gesture = new_press_gesture(exclusive=False)
    assert gesture is not None
    assert hasattr(gesture, "set_exclusive")


def test_keyboard_widget_uses_gtk_compat():
    text = open("touchflow/keyboard_widget.py", encoding="utf-8").read()
    assert "new_press_gesture" in text
    assert "GestureMultiPress.new()" not in text
