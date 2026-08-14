#pragma once

#include <gtk/gtk.h>
#include <functional>
#include <string>
#include "config.hpp"
#include "key_injector.hpp"

namespace touchflow {

using KeyboardAction = std::function<void(const std::string& action, const std::string& detail)>;

GtkWidget* keyboard_view_new(const Config& cfg, KeyInjector* injector, KeyboardAction on_action);

}  // namespace touchflow
