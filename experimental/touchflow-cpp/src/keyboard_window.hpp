#pragma once

#include <gtk/gtk.h>
#include "key_injector.hpp"

GtkWidget* touchflow_keyboard_window_new(KeyInjector* injector);
