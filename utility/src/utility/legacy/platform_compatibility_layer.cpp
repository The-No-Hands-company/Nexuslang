#include <voltron/utility/legacy/platform_compatibility_layer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::legacy {

PlatformCompatibilityLayer& PlatformCompatibilityLayer::instance() {
    static PlatformCompatibilityLayer instance;
    return instance;
}

void PlatformCompatibilityLayer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PlatformCompatibilityLayer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PlatformCompatibilityLayer::shutdown() {
    enabled_ = false;
    std::cout << "[PlatformCompatibilityLayer] Shutdown\n";
}

bool PlatformCompatibilityLayer::isEnabled() const {
    return enabled_;
}

void PlatformCompatibilityLayer::enable() {
    enabled_ = true;
}

void PlatformCompatibilityLayer::disable() {
    enabled_ = false;
}

std::string PlatformCompatibilityLayer::getStatus() const {
    std::ostringstream oss;
    oss << "PlatformCompatibilityLayer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PlatformCompatibilityLayer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::legacy
