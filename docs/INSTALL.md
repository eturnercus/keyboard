## Установка

### AppImage (рекомендуется — один клик)

1. Скачайте `TouchFlow-Keyboard-*-x86_64.AppImage` из [Releases](https://github.com/eturnercus/keyboard/releases)
2. `chmod +x TouchFlow-Keyboard-*.AppImage`
3. Запустите — откроется графический установщик

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
