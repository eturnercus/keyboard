#include "settings_app.hpp"
#include "config.hpp"

#include <adwaita.h>

namespace touchflow {

struct SettingsCtx {
    Config cfg;
    GtkSwitch* sw_auto{nullptr};
    GtkSwitch* sw_ext{nullptr};
    GtkSwitch* sw_quick{nullptr};
    GtkSpinButton* spin_h{nullptr};
};

static void on_save_clicked(GtkButton*, gpointer data) {
    auto* ctx = static_cast<SettingsCtx*>(data);
    ctx->cfg.auto_show = gtk_switch_get_active(ctx->sw_auto);
    ctx->cfg.hide_on_external_keyboard = gtk_switch_get_active(ctx->sw_ext);
    ctx->cfg.show_quick_actions = gtk_switch_get_active(ctx->sw_quick);
    ctx->cfg.height_px = static_cast<int>(gtk_spin_button_get_value(ctx->spin_h));
    ctx->cfg.save();
    auto* win = gtk_widget_get_ancestor(GTK_WIDGET(ctx->sw_auto), GTK_TYPE_WINDOW);
    if (win) gtk_window_destroy(GTK_WINDOW(win));
}

static GtkWidget* add_switch_row(GtkBox* box, const char* title, bool active) {
    auto* row = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    auto* label = gtk_label_new(title);
    gtk_widget_set_hexpand(label, TRUE);
    gtk_label_set_xalign(GTK_LABEL(label), 0.0f);
    auto* sw = gtk_switch_new();
    gtk_switch_set_active(GTK_SWITCH(sw), active);
    gtk_box_append(GTK_BOX(row), label);
    gtk_box_append(GTK_BOX(row), sw);
    gtk_box_append(GTK_BOX(box), row);
    return sw;
}

static void on_activate(AdwApplication* app, gpointer data) {
    auto* ctx = static_cast<SettingsCtx*>(data);
    auto* win = adw_application_window_new(GTK_APPLICATION(app));
    gtk_window_set_title(GTK_WINDOW(win), "TouchFlow C++ — Настройки");
    gtk_window_set_default_size(GTK_WINDOW(win), 420, 320);

    auto* toolbar = adw_toolbar_view_new();
    auto* header = adw_header_bar_new();
    auto* save_btn = gtk_button_new_with_label("Сохранить");
    gtk_widget_add_css_class(save_btn, "suggested-action");
    g_signal_connect(save_btn, "clicked", G_CALLBACK(on_save_clicked), ctx);
    adw_header_bar_pack_end(ADW_HEADER_BAR(header), save_btn);
    adw_toolbar_view_add_top_bar(ADW_TOOLBAR_VIEW(toolbar), header);

    auto* box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 12);
    gtk_widget_set_margin_top(box, 16);
    gtk_widget_set_margin_bottom(box, 16);
    gtk_widget_set_margin_start(box, 16);
    gtk_widget_set_margin_end(box, 16);

    auto* title = gtk_label_new("TouchFlow C++ (experimental)");
    gtk_widget_add_css_class(title, "title-1");
    gtk_box_append(GTK_BOX(box), title);

    ctx->sw_auto = GTK_SWITCH(add_switch_row(GTK_BOX(box), "Авто-показ при фокусе", ctx->cfg.auto_show));
    ctx->sw_ext = GTK_SWITCH(add_switch_row(GTK_BOX(box), "Скрывать при USB-клавиатуре", ctx->cfg.hide_on_external_keyboard));
    ctx->sw_quick = GTK_SWITCH(add_switch_row(GTK_BOX(box), "Быстрые кнопки", ctx->cfg.show_quick_actions));

    auto* hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    gtk_box_append(GTK_BOX(hbox), gtk_label_new("Высота клавиатуры (px)"));
    ctx->spin_h = GTK_SPIN_BUTTON(gtk_spin_button_new_with_range(180, 480, 10));
    gtk_spin_button_set_value(ctx->spin_h, ctx->cfg.height_px);
    gtk_box_append(GTK_BOX(hbox), GTK_WIDGET(ctx->spin_h));
    gtk_box_append(GTK_BOX(box), hbox);

    adw_toolbar_view_set_content(ADW_TOOLBAR_VIEW(toolbar), box);
    adw_application_window_set_content(ADW_APPLICATION_WINDOW(win), toolbar);
    gtk_window_present(GTK_WINDOW(win));
}

int run_settings_app(int argc, char** argv) {
    SettingsCtx ctx{Config::load()};
    auto* app = adw_application_new("com.touchflow.Settings.Cpp", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), &ctx);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}

}  // namespace touchflow
