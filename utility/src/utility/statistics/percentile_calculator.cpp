#include <voltron/utility/statistics/percentile_calculator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

PercentileCalculator& PercentileCalculator::instance() {
    static PercentileCalculator instance;
    return instance;
}

void PercentileCalculator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PercentileCalculator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PercentileCalculator::shutdown() {
    enabled_ = false;
    std::cout << "[PercentileCalculator] Shutdown\n";
}

bool PercentileCalculator::isEnabled() const {
    return enabled_;
}

void PercentileCalculator::enable() {
    enabled_ = true;
}

void PercentileCalculator::disable() {
    enabled_ = false;
}

std::string PercentileCalculator::getStatus() const {
    std::ostringstream oss;
    oss << "PercentileCalculator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PercentileCalculator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
