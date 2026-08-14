#include "focus_watcher.hpp"

#include <atspi/atspi.h>
#include <gtk/gtk.h>
#include <iostream>
#include <cstring>

namespace touchflow {

static bool is_text_role(const char* role) {
    if (!role) return false;
    static const char* roles[] = {
        "entry", "password text", "text", "editable text",
        "terminal", "document text", "spin button", "combo box", nullptr
    };
    for (const char** r = roles; *r; ++r)
        if (std::strcmp(role, *r) == 0) return true;
    return false;
}

FocusWatcher::FocusWatcher(Callback cb) : callback_(std::move(cb)) {}

FocusWatcher::~FocusWatcher() { stop(); }

void FocusWatcher::deliver_focus(const FocusInfo& info) {
    if (callback_) callback_(info);
}

struct FocusDeliver {
    FocusWatcher* watcher;
    FocusInfo info;
};

static gboolean deliver_on_main_idle(gpointer data) {
    auto* d = static_cast<FocusDeliver*>(data);
    if (d->watcher) d->watcher->deliver_focus(d->info);
    delete d;
    return G_SOURCE_REMOVE;
}

void FocusWatcher::deliver(_AtspiAccessible* focused) {
    if (!callback_ || !focused) return;
    auto* acc = reinterpret_cast<AtspiAccessible*>(focused);
    auto* payload = new FocusDeliver{this, {}};
    gchar* role = atspi_accessible_get_role_name(acc, nullptr);
    payload->info.role = role ? role : "";
    g_free(role);
    payload->info.is_text_entry = is_text_role(payload->info.role.c_str());

    AtspiAccessible* app = atspi_accessible_get_application(acc, nullptr);
    if (app) {
        gchar* name = atspi_accessible_get_name(app, nullptr);
        payload->info.app_id = name ? name : "";
        g_free(name);
        g_object_unref(app);
    }
    g_idle_add(deliver_on_main_idle, payload);
}

void atspi_focus_cb(_AtspiEvent* raw, void* data) {
    auto* event = reinterpret_cast<AtspiEvent*>(raw);
    auto* self = static_cast<FocusWatcher*>(data);
    if (!self || !event || !event->source) return;
    if (event->detail1 != 1) return;
    self->deliver(event->source);
}

bool FocusWatcher::start() {
    GError* err = nullptr;
    if (!atspi_init()) {
        std::cerr << "touchflow-cpp: AT-SPI init failed\n";
        return false;
    }
    auto* listener = atspi_event_listener_new(atspi_focus_cb, this, nullptr);
    if (!listener) return false;
    if (!atspi_event_listener_register(listener, "object:state-change:focused", &err)) {
        if (err) {
            std::cerr << "touchflow-cpp: AT-SPI register: " << err->message << "\n";
            g_error_free(err);
        }
        g_object_unref(listener);
        return false;
    }
    listener_ = listener;
    available_ = true;
    return true;
}

void FocusWatcher::stop() {
    if (listener_) {
        GError* err = nullptr;
        atspi_event_listener_deregister(
            static_cast<AtspiEventListener*>(listener_),
            "object:state-change:focused", &err);
        if (err) g_error_free(err);
        g_object_unref(listener_);
        listener_ = nullptr;
    }
}

}  // namespace touchflow
