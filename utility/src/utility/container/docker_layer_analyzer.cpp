#include <voltron/utility/container/docker_layer_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

DockerLayerAnalyzer& DockerLayerAnalyzer::instance() {
    static DockerLayerAnalyzer instance;
    return instance;
}

void DockerLayerAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DockerLayerAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DockerLayerAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[DockerLayerAnalyzer] Shutdown\n";
}

bool DockerLayerAnalyzer::isEnabled() const {
    return enabled_;
}

void DockerLayerAnalyzer::enable() {
    enabled_ = true;
}

void DockerLayerAnalyzer::disable() {
    enabled_ = false;
}

std::string DockerLayerAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "DockerLayerAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DockerLayerAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
