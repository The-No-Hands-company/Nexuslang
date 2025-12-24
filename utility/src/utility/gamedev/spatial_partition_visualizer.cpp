#include <voltron/utility/gamedev/spatial_partition_visualizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

SpatialPartitionVisualizer& SpatialPartitionVisualizer::instance() {
    static SpatialPartitionVisualizer instance;
    return instance;
}

void SpatialPartitionVisualizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SpatialPartitionVisualizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SpatialPartitionVisualizer::shutdown() {
    enabled_ = false;
    std::cout << "[SpatialPartitionVisualizer] Shutdown\n";
}

bool SpatialPartitionVisualizer::isEnabled() const {
    return enabled_;
}

void SpatialPartitionVisualizer::enable() {
    enabled_ = true;
}

void SpatialPartitionVisualizer::disable() {
    enabled_ = false;
}

std::string SpatialPartitionVisualizer::getStatus() const {
    std::ostringstream oss;
    oss << "SpatialPartitionVisualizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SpatialPartitionVisualizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
