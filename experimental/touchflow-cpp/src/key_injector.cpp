#include "key_injector.hpp"

#include <linux/input.h>
#include <linux/uinput.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <cstring>
#include <iostream>
#include <map>
#include <vector>

struct KeyInjector::Impl {
    int fd{-1};
    bool ok{false};
    bool shift{false};
    bool ctrl{false};
    bool alt{false};
    std::string layout{"ru"};
};

static const std::map<std::string, int> KEY_CODES = {
    {"KEY_ESC", KEY_ESC}, {"KEY_TAB", KEY_TAB}, {"KEY_ENTER", KEY_ENTER},
    {"KEY_SPACE", KEY_SPACE}, {"KEY_BACKSPACE", KEY_BACKSPACE}, {"KEY_DELETE", KEY_DELETE},
    {"KEY_LEFT", KEY_LEFT}, {"KEY_RIGHT", KEY_RIGHT}, {"KEY_UP", KEY_UP}, {"KEY_DOWN", KEY_DOWN},
    {"KEY_HOME", KEY_HOME}, {"KEY_END", KEY_END},
    {"KEY_LEFTCTRL", KEY_LEFTCTRL}, {"KEY_RIGHTCTRL", KEY_RIGHTCTRL},
    {"KEY_LEFTSHIFT", KEY_LEFTSHIFT}, {"KEY_RIGHTSHIFT", KEY_RIGHTSHIFT},
    {"KEY_LEFTALT", KEY_LEFTALT}, {"KEY_RIGHTALT", KEY_RIGHTALT},
    {"KEY_F1", KEY_F1}, {"KEY_F2", KEY_F2}, {"KEY_F3", KEY_F3}, {"KEY_F4", KEY_F4},
    {"KEY_F5", KEY_F5}, {"KEY_F6", KEY_F6}, {"KEY_F7", KEY_F7}, {"KEY_F8", KEY_F8},
    {"KEY_F9", KEY_F9}, {"KEY_F10", KEY_F10}, {"KEY_F11", KEY_F11}, {"KEY_F12", KEY_F12},
    {"KEY_MINUS", KEY_MINUS}, {"KEY_EQUAL", KEY_EQUAL},
    {"KEY_COMMA", KEY_COMMA}, {"KEY_DOT", KEY_DOT}, {"KEY_SLASH", KEY_SLASH},
    {"KEY_SEMICOLON", KEY_SEMICOLON}, {"KEY_APOSTROPHE", KEY_APOSTROPHE},
    {"KEY_LEFTBRACE", KEY_LEFTBRACE}, {"KEY_RIGHTBRACE", KEY_RIGHTBRACE},
    {"KEY_BACKSLASH", KEY_BACKSLASH}, {"KEY_GRAVE", KEY_GRAVE},
};

static const std::map<std::string, std::string> RU_MAP = {
    {"й", "q"}, {"ц", "w"}, {"у", "e"}, {"к", "r"}, {"е", "t"}, {"н", "y"},
    {"г", "u"}, {"ш", "i"}, {"щ", "o"}, {"з", "p"}, {"х", "bracketleft"}, {"ъ", "bracketright"},
    {"ф", "a"}, {"ы", "s"}, {"в", "d"}, {"а", "f"}, {"п", "g"}, {"р", "h"},
    {"о", "j"}, {"л", "k"}, {"д", "l"}, {"ж", "semicolon"}, {"э", "apostrophe"},
    {"я", "z"}, {"ч", "x"}, {"с", "c"}, {"м", "v"}, {"и", "b"}, {"т", "n"},
    {"ь", "m"}, {"б", "comma"}, {"ю", "period"}, {"ё", "grave"},
};

static const std::map<std::string, int> NAME_TO_CODE = {
    {"q", KEY_Q}, {"w", KEY_W}, {"e", KEY_E}, {"r", KEY_R}, {"t", KEY_T},
    {"y", KEY_Y}, {"u", KEY_U}, {"i", KEY_I}, {"o", KEY_O}, {"p", KEY_P},
    {"a", KEY_A}, {"s", KEY_S}, {"d", KEY_D}, {"f", KEY_F}, {"g", KEY_G},
    {"h", KEY_H}, {"j", KEY_J}, {"k", KEY_K}, {"l", KEY_L},
    {"z", KEY_Z}, {"x", KEY_X}, {"c", KEY_C}, {"v", KEY_V}, {"b", KEY_B},
    {"n", KEY_N}, {"m", KEY_M},
    {"0", KEY_0}, {"1", KEY_1}, {"2", KEY_2}, {"3", KEY_3}, {"4", KEY_4},
    {"5", KEY_5}, {"6", KEY_6}, {"7", KEY_7}, {"8", KEY_8}, {"9", KEY_9},
    {"space", KEY_SPACE}, {"enter", KEY_ENTER}, {"tab", KEY_TAB},
    {"backspace", KEY_BACKSPACE}, {"left", KEY_LEFT}, {"right", KEY_RIGHT},
    {"up", KEY_UP}, {"down", KEY_DOWN},
    {"leftctrl", KEY_LEFTCTRL}, {"rightctrl", KEY_RIGHTCTRL},
    {"leftshift", KEY_LEFTSHIFT}, {"rightshift", KEY_RIGHTSHIFT},
    {"leftalt", KEY_LEFTALT}, {"rightalt", KEY_RIGHTALT},
    {"comma", KEY_COMMA}, {"period", KEY_DOT}, {"minus", KEY_MINUS},
    {"equal", KEY_EQUAL}, {"semicolon", KEY_SEMICOLON},
    {"apostrophe", KEY_APOSTROPHE}, {"bracketleft", KEY_LEFTBRACE},
    {"bracketright", KEY_RIGHTBRACE}, {"grave", KEY_GRAVE},
};

KeyInjector::KeyInjector() : impl_(new Impl) {
    impl_->fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (impl_->fd < 0) {
        std::cerr << "touchflow-cpp: no /dev/uinput access (add user to input group)\n";
        return;
    }
    ioctl(impl_->fd, UI_SET_EVBIT, EV_KEY);
    ioctl(impl_->fd, UI_SET_EVBIT, EV_SYN);
    for (int k = 0; k < KEY_MAX; ++k)
        ioctl(impl_->fd, UI_SET_KEYBIT, k);
    uinput_user_dev uidev{};
    std::strncpy(uidev.name, "TouchFlow C++ Keyboard", UINPUT_MAX_NAME_SIZE);
    uidev.id.bustype = BUS_USB;
    write(impl_->fd, &uidev, sizeof(uidev));
    ioctl(impl_->fd, UI_DEV_CREATE);
    impl_->ok = true;
}

KeyInjector::~KeyInjector() {
    if (impl_->fd >= 0) {
        ioctl(impl_->fd, UI_DEV_DESTROY);
        close(impl_->fd);
    }
    delete impl_;
}

bool KeyInjector::available() const { return impl_->ok; }

void KeyInjector::set_layout(const std::string& lang) { impl_->layout = lang; }

static void emit(int fd, int type, int code, int val) {
    input_event ev{};
    ev.type = type;
    ev.code = code;
    ev.value = val;
    write(fd, &ev, sizeof(ev));
}

static void sync(int fd) { emit(fd, EV_SYN, SYN_REPORT, 0); }

static int resolve_code(const std::string& name) {
    auto it = KEY_CODES.find(name);
    if (it != KEY_CODES.end()) return it->second;
    if (name.size() == 1) {
        char c = name[0];
        if (c >= 'a' && c <= 'z') return KEY_A + (c - 'a');
        if (c >= 'A' && c <= 'Z') return KEY_A + (c - 'A');
        if (c >= '0' && c <= '9') return KEY_0 + (c - '0');
    }
    auto nit = NAME_TO_CODE.find(name);
    if (nit != NAME_TO_CODE.end()) return nit->second;
    return -1;
}

void KeyInjector::toggle_modifier(const std::string& mod, bool active) {
    if (mod == "shift") impl_->shift = active;
    else if (mod == "ctrl") impl_->ctrl = active;
    else if (mod == "alt") impl_->alt = active;
}

void KeyInjector::tap_key(const std::string& key_name) {
    if (!impl_->ok) return;
    int code = resolve_code(key_name);
    if (code < 0) return;
    if (impl_->shift) emit(impl_->fd, EV_KEY, KEY_LEFTSHIFT, 1);
    if (impl_->ctrl) emit(impl_->fd, EV_KEY, KEY_LEFTCTRL, 1);
    if (impl_->alt) emit(impl_->fd, EV_KEY, KEY_LEFTALT, 1);
    emit(impl_->fd, EV_KEY, code, 1);
    sync(impl_->fd);
    emit(impl_->fd, EV_KEY, code, 0);
    if (impl_->alt) emit(impl_->fd, EV_KEY, KEY_LEFTALT, 0);
    if (impl_->ctrl) emit(impl_->fd, EV_KEY, KEY_LEFTCTRL, 0);
    if (impl_->shift) emit(impl_->fd, EV_KEY, KEY_LEFTSHIFT, 0);
    sync(impl_->fd);
}

void KeyInjector::type_text(const std::string& text) {
    if (!impl_->ok || text.empty()) return;
    if (impl_->layout == "ru") {
        auto it = RU_MAP.find(text);
        if (it != RU_MAP.end()) {
            tap_key(it->second);
            return;
        }
    }
    tap_key(text);
}

void KeyInjector::chord(const std::string& modifier, const std::string& key) {
    if (!impl_->ok) return;
    int mod_code = resolve_code(modifier);
    int key_code = resolve_code(key);
    if (mod_code < 0 || key_code < 0) return;
    emit(impl_->fd, EV_KEY, mod_code, 1);
    emit(impl_->fd, EV_KEY, key_code, 1);
    sync(impl_->fd);
    emit(impl_->fd, EV_KEY, key_code, 0);
    emit(impl_->fd, EV_KEY, mod_code, 0);
    sync(impl_->fd);
}

void KeyInjector::copy() { chord("KEY_LEFTCTRL", "c"); }
void KeyInjector::paste() { chord("KEY_LEFTCTRL", "v"); }
void KeyInjector::cut() { chord("KEY_LEFTCTRL", "x"); }
void KeyInjector::select_all() { chord("KEY_LEFTCTRL", "a"); }
void KeyInjector::undo() { chord("KEY_LEFTCTRL", "z"); }
void KeyInjector::redo() { chord("KEY_LEFTCTRL", "y"); }
void KeyInjector::find() { chord("KEY_LEFTCTRL", "f"); }
