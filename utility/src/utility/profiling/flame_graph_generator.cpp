#include <voltron/utility/profiling/flame_graph_generator.h>
#include <iostream>

namespace voltron::utility::profiling {

FlameGraphGenerator& FlameGraphGenerator::instance() {
    static FlameGraphGenerator instance;
    return instance;
}

void FlameGraphGenerator::initialize() {
    enabled_ = true;
    std::cout << "[FlameGraphGenerator] Initialized\n";
}

void FlameGraphGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[FlameGraphGenerator] Shutdown\n";
}

bool FlameGraphGenerator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
