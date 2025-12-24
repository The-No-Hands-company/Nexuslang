#include <voltron/utility/string/small_string_optimizer_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

SmallStringOptimizerDebug& SmallStringOptimizerDebug::instance() {
    static SmallStringOptimizerDebug instance;
    return instance;
}

void SmallStringOptimizerDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SmallStringOptimizerDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SmallStringOptimizerDebug::shutdown() {
    enabled_ = false;
    std::cout << "[SmallStringOptimizerDebug] Shutdown\n";
}

bool SmallStringOptimizerDebug::isEnabled() const {
    return enabled_;
}

void SmallStringOptimizerDebug::enable() {
    enabled_ = true;
}

void SmallStringOptimizerDebug::disable() {
    enabled_ = false;
}

std::string SmallStringOptimizerDebug::getStatus() const {
    std::ostringstream oss;
    oss << "SmallStringOptimizerDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SmallStringOptimizerDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
