cmake_minimum_required(VERSION 3.16)
project(touchflow-cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GTK4 REQUIRED gtk4)
pkg_check_modules(ADW REQUIRED libadwaita-1)
pkg_check_modules(EVDEV REQUIRED libevdev)

add_executable(touchflowd
    src/main.cpp
    src/keyboard_window.cpp
    src/key_injector.cpp
)

target_include_directories(touchflowd PRIVATE ${GTK4_INCLUDE_DIRS} ${ADW_INCLUDE_DIRS} ${EVDEV_INCLUDE_DIRS})
target_link_libraries(touchflowd ${GTK4_LIBRARIES} ${ADW_LIBRARIES} ${EVDEV_LIBRARIES})
target_compile_options(touchflowd PRIVATE -Wall -Wextra)

install(TARGETS touchflowd DESTINATION bin)
