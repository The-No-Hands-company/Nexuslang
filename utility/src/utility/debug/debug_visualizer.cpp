#include <voltron/utility/debug/debug_visualizer.h>
#include <iostream>

namespace voltron::utility::debug {

DebugVisualizer& DebugVisualizer::instance() {
    static DebugVisualizer instance;
    return instance;
}

void DebugVisualizer::initialize() {
    enabled_ = true;
    std::cout << "[DebugVisualizer] Initialized\n";
}

void DebugVisualizer::shutdown() {
    enabled_ = false;
    std::cout << "[DebugVisualizer] Shutdown\n";
}

bool DebugVisualizer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::debug
