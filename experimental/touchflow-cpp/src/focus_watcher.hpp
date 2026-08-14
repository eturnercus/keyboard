#pragma once

#include <string>
#include <functional>

struct _AtspiAccessible;
struct _AtspiEvent;

namespace touchflow {

struct FocusInfo {
    std::string app_id;
    std::string window_class;
    std::string role;
    bool is_text_entry{false};
};

class FocusWatcher {
public:
    using Callback = std::function<void(const FocusInfo&)>;
    explicit FocusWatcher(Callback cb);
    ~FocusWatcher();
    bool start();
    void stop();
    void deliver_focus(const FocusInfo& info);

private:
    friend void atspi_focus_cb(_AtspiEvent* event, void* data);
    void deliver(_AtspiAccessible* focused);
    Callback callback_;
    void* listener_{nullptr};
    bool available_{false};
};

}  // namespace touchflow
