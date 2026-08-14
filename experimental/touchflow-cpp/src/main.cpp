#include "daemon.hpp"
#include <iostream>
#include <cstring>

static const char* VERSION = "1.0.0";

int main(int argc, char* argv[]) {
    bool virtual_kb = false;
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--virtual-keyboard") == 0)
            virtual_kb = true;
        else if (std::strcmp(argv[i], "--version") == 0) {
            std::cout << "touchflowd-cpp " << VERSION << " (experimental C++)\n";
            return 0;
        }
    }
    touchflow::Daemon daemon;
    return daemon.run(argc, argv, virtual_kb);
}
