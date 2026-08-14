"""Тесты system_integration."""


def test_ensure_atspi_bus_imports_os():
    import inspect

    from touchflow import system_integration

    src = inspect.getsource(system_integration.ensure_atspi_bus)
    assert "os.getuid" in src
    assert "import os" in inspect.getsource(system_integration)
