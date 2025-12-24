#include <voltron/utility/statistics/correlation_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

CorrelationTracker& CorrelationTracker::instance() {
    static CorrelationTracker instance;
    return instance;
}

void CorrelationTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CorrelationTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CorrelationTracker::shutdown() {
    enabled_ = false;
    std::cout << "[CorrelationTracker] Shutdown\n";
}

bool CorrelationTracker::isEnabled() const {
    return enabled_;
}

void CorrelationTracker::enable() {
    enabled_ = true;
}

void CorrelationTracker::disable() {
    enabled_ = false;
}

std::string CorrelationTracker::getStatus() const {
    std::ostringstream oss;
    oss << "CorrelationTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CorrelationTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
