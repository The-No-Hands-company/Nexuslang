#include <voltron/utility/orchestration/cross_system_correlator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

CrossSystemCorrelator& CrossSystemCorrelator::instance() {
    static CrossSystemCorrelator instance;
    return instance;
}

void CrossSystemCorrelator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CrossSystemCorrelator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CrossSystemCorrelator::shutdown() {
    enabled_ = false;
    std::cout << "[CrossSystemCorrelator] Shutdown\n";
}

bool CrossSystemCorrelator::isEnabled() const {
    return enabled_;
}

void CrossSystemCorrelator::enable() {
    enabled_ = true;
}

void CrossSystemCorrelator::disable() {
    enabled_ = false;
}

std::string CrossSystemCorrelator::getStatus() const {
    std::ostringstream oss;
    oss << "CrossSystemCorrelator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CrossSystemCorrelator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
