#include "keyboard_view.hpp"
#include "layouts.hpp"

#include <gdk/gdk.h>
#include <string>
#include <vector>

namespace touchflow {

struct KeyCtx {
    KeyInjector* injector;
    KeyboardAction on_action;
    Config config;
    std::string* current_lang;
    GtkWidget* root;
};

static void fire_action(KeyCtx* ctx, const std::string& action) {
    if (action == "MOD_SHIFT") {
        static bool shift_on = false;
        shift_on = !shift_on;
        ctx->injector->toggle_modifier("shift", shift_on);
        return;
    }
    if (action == "MOD_CTRL") {
        static bool on = false;
        on = !on;
        ctx->injector->toggle_modifier("ctrl", on);
        return;
    }
    if (action == "MOD_ALT") {
        static bool on = false;
        on = !on;
        ctx->injector->toggle_modifier("alt", on);
        return;
    }
    if (action == "SWITCH_LANG") {
        *ctx->current_lang = ctx->config.next_language(*ctx->current_lang);
        ctx->injector->set_layout(*ctx->current_lang);
        ctx->on_action("switch_lang", *ctx->current_lang);
        // rebuild keyboard
        GtkWidget* parent = gtk_widget_get_parent(ctx->root);
        GtkWidget* new_kb = keyboard_view_new(ctx->config, ctx->injector, ctx->on_action);
        if (parent) {
            gtk_box_remove(GTK_BOX(parent), ctx->root);
            gtk_box_append(GTK_BOX(parent), new_kb);
        }
        return;
    }
    if (action == "HIDE") {
        ctx->on_action("hide", "");
        return;
    }
    if (action == "ACTION_COPY") { ctx->injector->copy(); return; }
    if (action == "ACTION_PASTE") { ctx->injector->paste(); return; }
    if (action == "ACTION_CUT") { ctx->injector->cut(); return; }
    if (action == "ACTION_SELECT_ALL") { ctx->injector->select_all(); return; }
    if (action == "ACTION_UNDO") { ctx->injector->undo(); return; }
    if (action == "ACTION_REDO") { ctx->injector->redo(); return; }
    if (action == "ACTION_FIND") { ctx->injector->find(); return; }
    if (action.rfind("KEY_", 0) == 0)
        ctx->injector->tap_key(action);
    else
        ctx->injector->type_text(action);
    ctx->on_action("key_pressed", action);
}

static void on_key_clicked(GtkButton*, gpointer data) {
    auto* pair = static_cast<std::pair<KeyCtx*, std::string>*>(data);
    fire_action(pair->first, pair->second);
}

static GtkWidget* make_key(KeyCtx* ctx, const KeyDef& def) {
    auto* btn = gtk_button_new_with_label(def.label.c_str());
    gtk_widget_add_css_class(btn, "touchflow-key");
    gtk_widget_set_hexpand(btn, TRUE);
    auto* payload = new std::pair<KeyCtx*, std::string>(ctx, def.action);
    g_object_set_data_full(G_OBJECT(btn), "payload", payload, [](gpointer p) {
        delete static_cast<std::pair<KeyCtx*, std::string>*>(p);
    });
    g_signal_connect(btn, "clicked", G_CALLBACK(on_key_clicked), payload);
    if (def.width > 1.0)
        gtk_widget_set_size_request(btn, static_cast<int>(40 * def.width), -1);
    return btn;
}

static GtkWidget* make_row(KeyCtx* ctx, const std::vector<KeyDef>& keys, int spacing) {
    auto* row = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, spacing);
    for (const auto& k : keys) {
        if (k.label.empty() && k.action.empty()) {
            auto* spacer = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
            gtk_widget_set_hexpand(spacer, TRUE);
            gtk_box_append(GTK_BOX(row), spacer);
            continue;
        }
        gtk_box_append(GTK_BOX(row), make_key(ctx, k));
    }
    return row;
}

GtkWidget* keyboard_view_new(const Config& cfg, KeyInjector* injector, KeyboardAction on_action) {
    static std::string current_lang = cfg.default_language();
    static KeyCtx ctx{injector, on_action, cfg, &current_lang, nullptr};

    injector->set_layout(current_lang);
    auto* box = gtk_box_new(GTK_ORIENTATION_VERTICAL, cfg.key_spacing);
    gtk_widget_add_css_class(box, "touchflow-keyboard");
    ctx.root = box;

    std::string css = ".touchflow-keyboard{background:" + cfg.bg_color + ";padding:" +
                      std::to_string(cfg.key_spacing) + "px;}";
    auto* provider = gtk_css_provider_new();
    gtk_css_provider_load_from_string(provider, css.c_str());
    gtk_style_context_add_provider_for_display(
        gdk_display_get_default(), GTK_STYLE_PROVIDER(provider), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);

    if (cfg.show_function_row)
        gtk_box_append(GTK_BOX(box), make_row(&ctx, function_row(), cfg.key_spacing));
    if (cfg.show_number_row)
        gtk_box_append(GTK_BOX(box), make_row(&ctx, number_row(), cfg.key_spacing));

    auto layout = layout_for(current_lang);
    for (const auto& row : layout.rows)
        gtk_box_append(GTK_BOX(box), make_row(&ctx, row, cfg.key_spacing));

    if (cfg.show_arrow_row)
        gtk_box_append(GTK_BOX(box), make_row(&ctx, arrow_row(), cfg.key_spacing));
    if (cfg.show_quick_actions)
        gtk_box_append(GTK_BOX(box), make_row(&ctx, quick_actions(), cfg.key_spacing));

    gtk_box_append(GTK_BOX(box), make_row(&ctx, bottom_row(current_lang), cfg.key_spacing));
    return box;
}

}  // namespace touchflow
