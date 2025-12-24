#include <voltron/utility/meta/feature_flags.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

FeatureFlags& FeatureFlags::instance() {
    static FeatureFlags instance;
    return instance;
}

void FeatureFlags::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FeatureFlags] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FeatureFlags::shutdown() {
    enabled_ = false;
    std::cout << "[FeatureFlags] Shutdown\n";
}

bool FeatureFlags::isEnabled() const {
    return enabled_;
}

void FeatureFlags::enable() {
    enabled_ = true;
}

void FeatureFlags::disable() {
    enabled_ = false;
}

std::string FeatureFlags::getStatus() const {
    std::ostringstream oss;
    oss << "FeatureFlags - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FeatureFlags::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
