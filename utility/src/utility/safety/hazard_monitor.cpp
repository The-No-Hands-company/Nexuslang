#include <voltron/utility/safety/hazard_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

HazardMonitor& HazardMonitor::instance() {
    static HazardMonitor instance;
    return instance;
}

void HazardMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HazardMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HazardMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[HazardMonitor] Shutdown\n";
}

bool HazardMonitor::isEnabled() const {
    return enabled_;
}

void HazardMonitor::enable() {
    enabled_ = true;
}

void HazardMonitor::disable() {
    enabled_ = false;
}

std::string HazardMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "HazardMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HazardMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
