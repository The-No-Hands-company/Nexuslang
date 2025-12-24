#include <voltron/utility/legacy/legacy_api_adapter_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::legacy {

LegacyApiAdapterDebug& LegacyApiAdapterDebug::instance() {
    static LegacyApiAdapterDebug instance;
    return instance;
}

void LegacyApiAdapterDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LegacyApiAdapterDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LegacyApiAdapterDebug::shutdown() {
    enabled_ = false;
    std::cout << "[LegacyApiAdapterDebug] Shutdown\n";
}

bool LegacyApiAdapterDebug::isEnabled() const {
    return enabled_;
}

void LegacyApiAdapterDebug::enable() {
    enabled_ = true;
}

void LegacyApiAdapterDebug::disable() {
    enabled_ = false;
}

std::string LegacyApiAdapterDebug::getStatus() const {
    std::ostringstream oss;
    oss << "LegacyApiAdapterDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LegacyApiAdapterDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::legacy
