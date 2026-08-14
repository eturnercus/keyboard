#pragma once

namespace touchflow {

class ExternalKeyboardMonitor {
public:
    using Callback = void (*)(bool connected, void* data);
    ExternalKeyboardMonitor(Callback cb, void* data);
    void poll();
    bool connected() const;

private:
    Callback callback_;
    void* data_;
    bool connected_{false};
    bool detect_pluggable() const;
};

}  // namespace touchflow
