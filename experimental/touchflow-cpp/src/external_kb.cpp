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

ExternalKeyboardMonitor::ExternalKeyboardMonitor(Callback cb, void* data)
    : callback_(cb), data_(data) {
    connected_ = detect();
}

bool ExternalKeyboardMonitor::detect() const {
    std::ifstream in("/proc/bus/input/devices");
    if (!in) return false;
    std::string block, line;
    bool has_keys = false;
    std::string name, bus;
    auto flush = [&]() {
        if (has_keys && !name.empty() && !should_skip(name)) {
            if (bus.find("0019") == std::string::npos) return true;
        }
        has_keys = false;
        name.clear();
        bus.clear();
        return false;
    };
    while (std::getline(in, line)) {
        if (line.empty()) {
            if (flush()) return true;
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
            if (pos != std::string::npos) bus = line.substr(pos + 4);
        } else if (line.rfind("B:", 0) == 0 && line.find("EV_KEY") != std::string::npos) {
            has_keys = true;
        }
    }
    return flush();
}

void ExternalKeyboardMonitor::poll() {
    bool now = detect();
    if (now != connected_) {
        connected_ = now;
        if (callback_) callback_(connected_, data_);
    }
}

bool ExternalKeyboardMonitor::connected() const { return connected_; }

}  // namespace touchflow
