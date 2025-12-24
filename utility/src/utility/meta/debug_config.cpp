#include <voltron/utility/meta/debug_config.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

DebugConfig& DebugConfig::instance() {
    static DebugConfig instance;
    return instance;
}

void DebugConfig::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DebugConfig] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DebugConfig::shutdown() {
    enabled_ = false;
    std::cout << "[DebugConfig] Shutdown\n";
}

bool DebugConfig::isEnabled() const {
    return enabled_;
}

void DebugConfig::enable() {
    enabled_ = true;
}

void DebugConfig::disable() {
    enabled_ = false;
}

std::string DebugConfig::getStatus() const {
    std::ostringstream oss;
    oss << "DebugConfig - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DebugConfig::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
