## Установка

### AppImage (рекомендуется — один клик)

1. Проверьте архитектуру: `uname -m` (x86_64 или aarch64)
2. Скачайте нужный AppImage из [Releases](https://github.com/eturnercus/keyboard/releases)
3. `chmod +x TouchFlow-Keyboard-*.AppImage`
4. Запустите — откроется графический установщик

**Альтернатива (любая архитектура):**
```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/latest/download/touchflow-install-1.0.2.sh | bash
```

### Другие способы

| Файл | Назначение |
|------|------------|
| `touchflow_keyboard-*-py3-none-any.whl` | `pip install` |
| `touchflow-keyboard-*-linux.tar.gz` | Исходники + скрипты |
| `TouchFlow-Keyboard-*-x86_64.tar.gz` | Portable AppDir (без FUSE) |

### Из git

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
./scripts/install.sh
```
