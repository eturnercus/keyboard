#pragma once

#include <string>

class KeyInjector {
public:
    KeyInjector();
    ~KeyInjector();
    bool available() const;
    void tap_key(const std::string& key_name);
    void copy_clipboard();
    void paste_clipboard();

private:
    struct Impl;
    Impl* impl_;
};
