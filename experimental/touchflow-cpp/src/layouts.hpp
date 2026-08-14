#pragma once
#include <string>
#include <vector>

namespace touchflow {

struct KeyDef {
    std::string label;
    std::string action;
    double width = 1.0;
};

using KeyRow = std::vector<KeyDef>;

struct LayoutData {
    std::vector<KeyRow> rows;
};

LayoutData layout_for(const std::string& lang_code);
std::vector<KeyDef> quick_actions();
std::vector<KeyDef> function_row();
std::vector<KeyDef> number_row();
std::vector<KeyDef> arrow_row();
std::vector<KeyDef> bottom_row(const std::string& lang_label);

}  // namespace touchflow
