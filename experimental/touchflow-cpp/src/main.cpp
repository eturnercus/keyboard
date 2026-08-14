#include <adwaita.h>
#include "keyboard_window.hpp"
#include "key_injector.hpp"

static void on_activate(AdwApplication* app, gpointer) {
    KeyInjector injector;
    auto* win = adw_application_window_new(GTK_APPLICATION(app));
    adw_application_window_set_content(ADW_APPLICATION_WINDOW(win),
        touchflow_keyboard_window_new(&injector));
    gtk_window_set_title(GTK_WINDOW(win), "TouchFlow C++");
    gtk_window_set_default_size(GTK_WINDOW(win), 800, 280);
    gtk_window_present(GTK_WINDOW(win));
}

int main(int argc, char* argv[]) {
    auto* app = adw_application_new("com.touchflow.Keyboard.Cpp", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), nullptr);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
