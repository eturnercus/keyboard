#include "keyboard_window.hpp"

static void on_key_clicked(GtkButton* btn, gpointer data) {
    auto* inj = static_cast<KeyInjector*>(data);
    const char* action = static_cast<const char*>(g_object_get_data(G_OBJECT(btn), "action"));
    if (action && inj) inj->tap_key(action);
}

static GtkWidget* make_key(KeyInjector* inj, const char* label, const char* action) {
    auto* btn = gtk_button_new_with_label(label);
    g_object_set_data(G_OBJECT(btn), "action", (gpointer)action);
    g_signal_connect(btn, "clicked", G_CALLBACK(on_key_clicked), inj);
    return btn;
}

GtkWidget* touchflow_keyboard_window_new(KeyInjector* injector) {
    auto* box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 4);
    gtk_widget_add_css_class(box, "touchflow-keyboard");

    auto* row1 = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 4);
    gtk_box_append(GTK_BOX(row1), make_key(injector, "Копир.", "KEY_LEFTCTRL"));
    gtk_box_append(GTK_BOX(row1), make_key(injector, "Встав.", "KEY_LEFTCTRL"));
    gtk_box_append(GTK_BOX(row1), make_key(injector, "⌫", "KEY_BACKSPACE"));
    gtk_box_append(GTK_BOX(box), row1);

    const char* keys[] = {"й","ц","у","к","е","н","г","ш","щ","з","х","ъ"};
    const char* acts[] = {"й","ц","у","к","е","н","г","ш","щ","з","х","ъ"};
    auto* row2 = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 4);
    for (int i = 0; i < 12; ++i)
        gtk_box_append(GTK_BOX(row2), make_key(injector, keys[i], acts[i]));
    gtk_box_append(GTK_BOX(box), row2);

    auto* row3 = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 4);
    gtk_box_append(GTK_BOX(row3), make_key(injector, "Пробел", "KEY_SPACE"));
    gtk_box_append(GTK_BOX(row3), make_key(injector, "Enter", "KEY_ENTER"));
    gtk_box_append(GTK_BOX(box), row3);

    return box;
}
