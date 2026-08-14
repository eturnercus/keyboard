#include "key_injector.hpp"

#include <linux/input.h>
#include <linux/uinput.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <cstring>
#include <iostream>

struct KeyInjector::Impl {
    int fd{-1};
    bool ok{false};
};

KeyInjector::KeyInjector() : impl_(new Impl) {
    impl_->fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (impl_->fd < 0) {
        std::cerr << "touchflow-cpp: no /dev/uinput access\n";
        return;
    }
    ioctl(impl_->fd, UI_SET_EVBIT, EV_KEY);
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

static void emit(int fd, int type, int code, int val) {
    input_event ev{};
    ev.type = type;
    ev.code = code;
    ev.value = val;
    write(fd, &ev, sizeof(ev));
}

void KeyInjector::tap_key(const std::string& key_name) {
    if (!impl_->ok) return;
    int code = KEY_SPACE;
    if (key_name == "KEY_ENTER") code = KEY_ENTER;
    else if (key_name == "KEY_BACKSPACE") code = KEY_BACKSPACE;
    else if (key_name.length() == 1) {
        char c = key_name[0];
        if (c >= 'a' && c <= 'z') code = KEY_A + (c - 'a');
        else if (c >= '0' && c <= '9') code = KEY_0 + (c - '0');
    }
    emit(impl_->fd, EV_KEY, code, 1);
    emit(impl_->fd, EV_SYN, SYN_REPORT, 0);
    emit(impl_->fd, EV_KEY, code, 0);
    emit(impl_->fd, EV_SYN, SYN_REPORT, 0);
}

void KeyInjector::copy_clipboard() {
    tap_key("KEY_LEFTCTRL");
    // simplified — full chord in next iteration
}

void KeyInjector::paste_clipboard() {}
