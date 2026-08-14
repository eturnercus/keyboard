#include "external_kb.hpp"

#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>

namespace touchflow {

static std::string lower(const std::string& s) {
    std::string r = s;
    std::transform(r.begin(), r.end(), r.begin(), [](unsigned char c) { return std::tolower(c); });
    return r;
}

static bool should_skip(const std::string& name) {
    static const char* patterns[] = {
        "touchflow", "virtual", "uinput", "dummy", "power button",
        "sleep button", "video bus", "gpio", nullptr
    };
    auto n = lower(name);
    for (const char** p = patterns; *p; ++p)
        if (n.find(*p) != std::string::npos) return true;
    return false;
}

static bool is_keyboard_block(const std::string& name, const std::string& handlers, bool has_keys) {
    if (!has_keys || should_skip(name)) return false;
    return handlers.find("event") != std::string::npos && handlers.find("kbd") != std::string::npos;
}

ExternalKeyboardMonitor::ExternalKeyboardMonitor(Callback cb, void* data)
    : callback_(cb), data_(data) {
    connected_ = detect_pluggable();
}

bool ExternalKeyboardMonitor::detect_pluggable() const {
    std::ifstream in("/proc/bus/input/devices");
    if (!in) return false;
    std::string line, name, bus, handlers;
    bool has_keys = false;
    auto check = [&]() -> bool {
        if (!is_keyboard_block(name, handlers, has_keys)) return false;
        // USB / Bluetooth / I2C HID — блокируют авто-показ
        if (bus == "0003" || bus == "0005" || bus == "0018") return true;
        return false;
    };
    auto reset = [&]() {
        has_keys = false;
        name.clear();
        bus.clear();
        handlers.clear();
    };
    while (std::getline(in, line)) {
        if (line.empty()) {
            if (check()) return true;
            reset();
            continue;
        }
        if (line.rfind("N:", 0) == 0) {
            auto pos = line.find("Name=");
            if (pos != std::string::npos)
                name = line.substr(pos + 5);
            while (!name.empty() && (name.front() == '"' || name.front() == '\'')) name.erase(name.begin());
            while (!name.empty() && (name.back() == '"' || name.back() == '\'')) name.pop_back();
        } else if (line.rfind("I:", 0) == 0) {
            auto pos = line.find("bus=");
            if (pos != std::string::npos) {
                auto end = line.find_first_of(" \t", pos + 4);
                bus = line.substr(pos + 4, end == std::string::npos ? std::string::npos : end - pos - 4);
            }
        } else if (line.rfind("H:", 0) == 0) {
            auto pos = line.find("Handlers=");
            if (pos != std::string::npos) handlers = line.substr(pos + 9);
        } else if (line.rfind("B:", 0) == 0 && line.find("EV_KEY") != std::string::npos) {
            has_keys = true;
        }
    }
    return check();
}

void ExternalKeyboardMonitor::poll() {
    bool now = detect_pluggable();
    if (now != connected_) {
        connected_ = now;
        if (callback_) callback_(connected_, data_);
    }
}

bool ExternalKeyboardMonitor::connected() const { return connected_; }

}  // namespace touchflow
