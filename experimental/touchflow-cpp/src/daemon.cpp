#include "daemon.hpp"
#include "keyboard_view.hpp"

#include <iostream>

namespace touchflow {

Daemon::Daemon()
    : config_(Config::load())
    , learning_(config_.learning_threshold) {}

void Daemon::on_keyboard_action(const std::string& action, const std::string& detail) {
    (void)detail;
    if (action == "hide") hide_keyboard(true);
}

void Daemon::show_keyboard(bool manual) {
    if (config_.hide_on_external_keyboard && ext_kb_ && ext_kb_->connected() && !manual)
        return;
    if (window_) {
        gtk_widget_set_visible(GTK_WIDGET(window_), TRUE);
        gtk_window_present(window_);
        visible_ = true;
        manual_show_ = manual;
        if (manual)
            learning_.on_auto_show(current_focus_.app_id, current_focus_.window_class);
    }
}

void Daemon::hide_keyboard(bool manual) {
    if (window_) {
        learning_.on_dismiss(current_focus_.app_id, current_focus_.window_class, manual);
        gtk_widget_set_visible(GTK_WIDGET(window_), FALSE);
        visible_ = false;
        manual_show_ = false;
    }
}

void Daemon::on_focus(const FocusInfo& info) {
    current_focus_ = info;
    if (!info.is_text_entry) {
        if (config_.auto_hide_on_blur && visible_ && !manual_show_)
            hide_keyboard(false);
        return;
    }
    if (config_.hide_on_external_keyboard && ext_kb_ && ext_kb_->connected())
        return;
    if (!config_.auto_show) return;
    if (!learning_.should_auto_show(info.app_id, info.window_class)) return;
    show_keyboard(false);
    learning_.on_auto_show(info.app_id, info.window_class);
}

void Daemon::on_ext_kb(bool connected, void* data) {
    auto* self = static_cast<Daemon*>(data);
    if (connected && self->config_.hide_on_external_keyboard && self->visible_)
        self->hide_keyboard(false);
}

gboolean Daemon::poll_ext_kb(gpointer data) {
    auto* self = static_cast<Daemon*>(data);
    if (self->ext_kb_) self->ext_kb_->poll();
    return G_SOURCE_CONTINUE;
}

void Daemon::setup_ui(AdwApplication* app) {
    window_ = GTK_WINDOW(adw_application_window_new(GTK_APPLICATION(app)));
    gtk_window_set_title(window_, "TouchFlow C++");
    gtk_window_set_decorated(window_, FALSE);
    gtk_window_set_resizable(window_, FALSE);
    gtk_window_set_default_size(window_, -1, config_.height_px);

    keyboard_ = keyboard_view_new(config_, &injector_,
        [this](const std::string& a, const std::string& d) { on_keyboard_action(a, d); });
    adw_application_window_set_content(ADW_APPLICATION_WINDOW(window_), keyboard_);
}

void Daemon::setup_services() {
    focus_ = std::make_unique<FocusWatcher>([this](const FocusInfo& i) { on_focus(i); });
    focus_->start();
    ext_kb_ = std::make_unique<ExternalKeyboardMonitor>(&Daemon::on_ext_kb, this);
    poll_id_ = g_timeout_add_seconds(2, poll_ext_kb, this);
    if (!injector_.available())
        std::cerr << "touchflow-cpp: key injection disabled — add user to input group\n";
}

int Daemon::run(int argc, char** argv, bool virtual_keyboard) {
    virtual_kb_ = virtual_keyboard;
    auto* app = adw_application_new("com.touchflow.Keyboard.Cpp", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(+[](AdwApplication* app, gpointer data) {
        auto* self = static_cast<Daemon*>(data);
        self->setup_ui(app);
        self->setup_services();
        if (self->virtual_kb_ || !self->config_.startup_hidden)
            self->show_keyboard(self->virtual_kb_);
    }), this);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    if (poll_id_) g_source_remove(poll_id_);
    g_object_unref(app);
    return status;
}

}  // namespace touchflow
