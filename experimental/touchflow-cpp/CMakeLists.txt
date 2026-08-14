cmake_minimum_required(VERSION 3.16)
project(touchflow-cpp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GTK4 REQUIRED gtk4)
pkg_check_modules(ADW REQUIRED libadwaita-1)
pkg_check_modules(EVDEV REQUIRED libevdev)
pkg_check_modules(ATSPI REQUIRED atspi-2 dbus-1)

set(DAEMON_SOURCES
    src/main.cpp
    src/config.cpp
    src/layouts.cpp
    src/key_injector.cpp
    src/keyboard_view.cpp
    src/focus_watcher.cpp
    src/external_kb.cpp
    src/learning.cpp
    src/daemon.cpp
)

set(SETTINGS_SOURCES
    src/settings_main.cpp
    src/settings_app.cpp
    src/config.cpp
)

add_executable(touchflowd-cpp ${DAEMON_SOURCES})
add_executable(touchflow-settings-cpp ${SETTINGS_SOURCES})

foreach(target touchflowd-cpp touchflow-settings-cpp)
    target_include_directories(${target} PRIVATE src ${GTK4_INCLUDE_DIRS} ${ADW_INCLUDE_DIRS} ${ATSPI_INCLUDE_DIRS})
    target_link_libraries(${target}
        ${GTK4_LIBRARIES} ${ADW_LIBRARIES} ${EVDEV_LIBRARIES} ${ATSPI_LIBRARIES}
        pthread
    )
    target_compile_options(${target} PRIVATE -Wall -Wextra)
endforeach()

install(TARGETS touchflowd-cpp touchflow-settings-cpp DESTINATION bin)
install(FILES data/com.touchflow.Keyboard.Virtual.desktop DESTINATION share/applications)
install(FILES data/com.touchflow.Keyboard.Cpp.desktop DESTINATION share/applications)
install(FILES data/com.touchflow.Settings.Cpp.desktop DESTINATION share/applications)
