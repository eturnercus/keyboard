#include "config.hpp"
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <sstream>

namespace fs = std::filesystem;

namespace touchflow {

static fs::path config_dir() {
    if (const char* xdg = std::getenv("XDG_CONFIG_HOME"))
        return fs::path(xdg) / "touchflow";
    if (const char* home = std::getenv("HOME"))
        return fs::path(home) / ".config" / "touchflow";
    return "touchflow";
}

Config Config::load() {
    Config cfg;
    cfg.languages = {
        {"ru", "Русский", true, true},
        {"en", "English", true, false},
    };
    auto path = config_dir() / "config-cpp.toml";
    if (!fs::exists(path)) return cfg;
    std::ifstream in(path);
    std::string line, section;
    while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        if (line[0] == '[') { section = line; continue; }
        auto eq = line.find('=');
        if (eq == std::string::npos) continue;
        auto key = line.substr(0, eq);
        auto val = line.substr(eq + 1);
        while (!key.empty() && key.back() == ' ') key.pop_back();
        while (!val.empty() && val.front() == ' ') val.erase(val.begin());
        if (key == "auto_show") cfg.auto_show = val == "true";
        else if (key == "hide_on_external_keyboard") cfg.hide_on_external_keyboard = val == "true";
        else if (key == "show_quick_actions") cfg.show_quick_actions = val == "true";
        else if (key == "height_px") cfg.height_px = std::stoi(val);
        else if (key == "learning_threshold") cfg.learning_threshold = std::stof(val);
    }
    return cfg;
}

void Config::save() const {
    fs::create_directories(config_dir());
    std::ofstream out(config_dir() / "config-cpp.toml");
    out << "[behavior]\nauto_show = " << (auto_show ? "true" : "false") << "\n";
    out << "hide_on_external_keyboard = " << (hide_on_external_keyboard ? "true" : "false") << "\n";
    out << "[layout]\nheight_px = " << height_px << "\n";
}

std::string Config::default_language() const {
    for (const auto& l : languages)
        if (l.enabled && l.is_default) return l.code;
    for (const auto& l : languages)
        if (l.enabled) return l.code;
    return "en";
}

std::string Config::next_language(const std::string& current) const {
    std::vector<std::string> enabled;
    for (const auto& l : languages)
        if (l.enabled) enabled.push_back(l.code);
    if (enabled.empty()) return current;
    for (size_t i = 0; i < enabled.size(); ++i)
        if (enabled[i] == current)
            return enabled[(i + 1) % enabled.size()];
    return enabled[0];
}

}  // namespace touchflow
