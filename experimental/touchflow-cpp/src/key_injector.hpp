#pragma once

#include <string>

class KeyInjector {
public:
    KeyInjector();
    ~KeyInjector();
    KeyInjector(const KeyInjector&) = delete;
    KeyInjector& operator=(const KeyInjector&) = delete;

    bool available() const;
    void set_layout(const std::string& lang);

    void tap_key(const std::string& key_name);
    void type_text(const std::string& text);
    void chord(const std::string& modifier, const std::string& key);
    void toggle_modifier(const std::string& mod, bool active);

    void copy();
    void paste();
    void cut();
    void select_all();
    void undo();
    void redo();
    void find();

private:
    struct Impl;
    Impl* impl_;
};
