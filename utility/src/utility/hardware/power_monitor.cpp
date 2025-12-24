#include <voltron/utility/hardware/power_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

PowerMonitor& PowerMonitor::instance() {
    static PowerMonitor instance;
    return instance;
}

void PowerMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PowerMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PowerMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[PowerMonitor] Shutdown\n";
}

bool PowerMonitor::isEnabled() const {
    return enabled_;
}

void PowerMonitor::enable() {
    enabled_ = true;
}

void PowerMonitor::disable() {
    enabled_ = false;
}

std::string PowerMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "PowerMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PowerMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
