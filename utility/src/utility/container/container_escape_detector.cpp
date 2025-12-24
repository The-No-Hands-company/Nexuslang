#include <voltron/utility/container/container_escape_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

ContainerEscapeDetector& ContainerEscapeDetector::instance() {
    static ContainerEscapeDetector instance;
    return instance;
}

void ContainerEscapeDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ContainerEscapeDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ContainerEscapeDetector::shutdown() {
    enabled_ = false;
    std::cout << "[ContainerEscapeDetector] Shutdown\n";
}

bool ContainerEscapeDetector::isEnabled() const {
    return enabled_;
}

void ContainerEscapeDetector::enable() {
    enabled_ = true;
}

void ContainerEscapeDetector::disable() {
    enabled_ = false;
}

std::string ContainerEscapeDetector::getStatus() const {
    std::ostringstream oss;
    oss << "ContainerEscapeDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ContainerEscapeDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
