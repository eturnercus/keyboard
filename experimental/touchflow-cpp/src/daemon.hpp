#pragma once

#include <gtk/gtk.h>
#include <adwaita.h>
#include <memory>
#include "config.hpp"
#include "focus_watcher.hpp"
#include "external_kb.hpp"
#include "learning.hpp"
#include "key_injector.hpp"

namespace touchflow {

class Daemon {
public:
    Daemon();
    int run(int argc, char** argv, bool virtual_keyboard);
    void show_keyboard(bool manual = false);
    void hide_keyboard(bool manual = false);

private:
    Config config_;
    KeyInjector injector_;
    LearningEngine learning_;
    std::unique_ptr<FocusWatcher> focus_;
    std::unique_ptr<ExternalKeyboardMonitor> ext_kb_;
    GtkWindow* window_{nullptr};
    GtkWidget* keyboard_{nullptr};
    bool visible_{false};
    bool manual_show_{false};
    FocusInfo current_focus_;
    guint poll_id_{0};

    void setup_ui(AdwApplication* app);
    void setup_services();
    void on_focus(const FocusInfo& info);
    static void on_ext_kb(bool connected, void* data);
    static gboolean poll_ext_kb(gpointer data);
    void on_keyboard_action(const std::string& action, const std::string& detail);
};

}  // namespace touchflow
