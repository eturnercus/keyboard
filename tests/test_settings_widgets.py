"""Тесты виджетов настроек."""


def test_float_spin_row_accepts_subtitle():
    from touchflow_settings.widgets import FloatSpinRow

    # Не создаём GTK — проверяем сигнатуру через inspect
    import inspect
    sig = inspect.signature(FloatSpinRow.__init__)
    params = list(sig.parameters.keys())
    assert "subtitle" in params or len(params) >= 7  # self, label, subtitle, value, min, max, on_change

    # Убедимся что subtitle — второй параметр после label
    assert params[2] == "subtitle" if len(params) > 2 else True
