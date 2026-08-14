#include "layouts.hpp"

namespace touchflow {

static KeyRow row(std::initializer_list<KeyDef> keys) { return KeyRow(keys); }

LayoutData layout_for(const std::string& lang) {
    LayoutData d;
    if (lang == "ru") {
        d.rows.push_back(row({{"й","й"},{ "ц","ц"},{ "у","у"},{ "к","к"},{ "е","е"},{ "н","н"},
            {"г","г"},{ "ш","ш"},{ "щ","щ"},{ "з","з"},{ "х","х"},{ "ъ","ъ"}}));
        d.rows.push_back(row({{"Tab","KEY_TAB",1.5},{"ф","ф"},{"ы","ы"},{"в","в"},{"а","а"},
            {"п","п"},{"р","р"},{"о","о"},{"л","л"},{"д","д"},{"ж","ж"},{"э","э"},{"Enter","KEY_ENTER",1.5}}));
        d.rows.push_back(row({{"⇧","MOD_SHIFT",2},{"я","я"},{"ч","ч"},{"с","с"},{"м","м"},
            {"и","и"},{"т","т"},{"ь","ь"},{"б","б"},{"ю","ю"},{"ё","ё"},{"⇧","MOD_SHIFT",2}}));
    } else {
        d.rows.push_back(row({{"q","q"},{"w","w"},{"e","e"},{"r","r"},{"t","t"},{"y","y"},
            {"u","u"},{"i","i"},{"o","o"},{"p","p"}}));
        d.rows.push_back(row({{"Tab","KEY_TAB",1.5},{"a","a"},{"s","s"},{"d","d"},{"f","f"},
            {"g","g"},{"h","h"},{"i","i"},{"j","j"},{"k","k"},{"l","l"},{"Enter","KEY_ENTER",1.5}}));
        d.rows.push_back(row({{"⇧","MOD_SHIFT",2},{"z","z"},{"x","x"},{"c","c"},{"v","v"},
            {"b","b"},{"n","n"},{"m","m"},{",","KEY_COMMA"},{".","KEY_DOT"},{"⇧","MOD_SHIFT",2}}));
    }
    return d;
}

std::vector<KeyDef> quick_actions() {
    return {{"Копир.","ACTION_COPY",1.3},{"Встав.","ACTION_PASTE",1.3},{"Вырез.","ACTION_CUT",1.2},
            {"Всё","ACTION_SELECT_ALL",1.0},{"Отмена","ACTION_UNDO",1.2},{"Повт.","ACTION_REDO",1.1}};
}

std::vector<KeyDef> function_row() {
    return {{"Esc","KEY_ESC"},{"F1","KEY_F1"},{"F2","KEY_F2"},{"F3","KEY_F3"},{"F4","KEY_F4"},
            {"F5","KEY_F5"},{"F6","KEY_F6"},{"F7","KEY_F7"},{"F8","KEY_F8"},
            {"F9","KEY_F9"},{"F10","KEY_F10"},{"F11","KEY_F11"},{"F12","KEY_F12"}};
}

std::vector<KeyDef> number_row() {
    return {{"1","1"},{"2","2"},{"3","3"},{"4","4"},{"5","5"},{"6","6"},{"7","7"},{"8","8"},{"9","9"},{"0","0"},
            {"-","KEY_MINUS"},{"=","KEY_EQUAL"},{"⌫","KEY_BACKSPACE",2.0}};
}

std::vector<KeyDef> arrow_row() {
    return {{"","",8.0},{"◀","KEY_LEFT"},{"▲","KEY_UP"},{"▼","KEY_DOWN"},{"▶","KEY_RIGHT"}};
}

std::vector<KeyDef> bottom_row(const std::string& lang_label) {
    return {{lang_label,"SWITCH_LANG",1.5},{"Ctrl","MOD_CTRL",1.2},{"Alt","MOD_ALT",1.2},
            {" ","KEY_SPACE",5.0},{"✕","HIDE",1.2}};
}

}  // namespace touchflow
