#include <voltron/utility/cloud/cloud_cost_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

CloudCostTracker& CloudCostTracker::instance() {
    static CloudCostTracker instance;
    return instance;
}

void CloudCostTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CloudCostTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CloudCostTracker::shutdown() {
    enabled_ = false;
    std::cout << "[CloudCostTracker] Shutdown\n";
}

bool CloudCostTracker::isEnabled() const {
    return enabled_;
}

void CloudCostTracker::enable() {
    enabled_ = true;
}

void CloudCostTracker::disable() {
    enabled_ = false;
}

std::string CloudCostTracker::getStatus() const {
    std::ostringstream oss;
    oss << "CloudCostTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CloudCostTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
