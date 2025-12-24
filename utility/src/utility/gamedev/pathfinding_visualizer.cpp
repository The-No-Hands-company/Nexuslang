#include <voltron/utility/gamedev/pathfinding_visualizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

PathfindingVisualizer& PathfindingVisualizer::instance() {
    static PathfindingVisualizer instance;
    return instance;
}

void PathfindingVisualizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PathfindingVisualizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PathfindingVisualizer::shutdown() {
    enabled_ = false;
    std::cout << "[PathfindingVisualizer] Shutdown\n";
}

bool PathfindingVisualizer::isEnabled() const {
    return enabled_;
}

void PathfindingVisualizer::enable() {
    enabled_ = true;
}

void PathfindingVisualizer::disable() {
    enabled_ = false;
}

std::string PathfindingVisualizer::getStatus() const {
    std::ostringstream oss;
    oss << "PathfindingVisualizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PathfindingVisualizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
