#pragma once
#include <string>
#include <vector>

namespace touchflow {

struct LanguageEntry {
    std::string code = "ru";
    std::string name = "Русский";
    bool enabled = true;
    bool is_default = true;
};

struct Config {
    bool auto_show = true;
    bool auto_hide_on_blur = true;
    bool hide_on_external_keyboard = true;
    bool swipe_from_bottom = true;
    bool learning_enabled = true;
    bool startup_hidden = false;
    bool show_quick_actions = true;
    bool show_function_row = true;
    bool show_number_row = true;
    bool show_arrow_row = true;
    int height_px = 280;
    int key_spacing = 4;
    int row_height = 52;
    int key_radius = 8;
    float learning_threshold = 0.35f;
    std::string bg_color = "#1e1e2e";
    std::string key_color = "#313244";
    std::string pressed_color = "#89b4fa";
    std::string text_color = "#cdd6f4";
    std::vector<LanguageEntry> languages;

    static Config load();
    void save() const;
    std::string default_language() const;
    std::string next_language(const std::string& current) const;
};

}  // namespace touchflow
