#include <voltron/utility/hardware/ecc_error_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

EccErrorMonitor& EccErrorMonitor::instance() {
    static EccErrorMonitor instance;
    return instance;
}

void EccErrorMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EccErrorMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EccErrorMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[EccErrorMonitor] Shutdown\n";
}

bool EccErrorMonitor::isEnabled() const {
    return enabled_;
}

void EccErrorMonitor::enable() {
    enabled_ = true;
}

void EccErrorMonitor::disable() {
    enabled_ = false;
}

std::string EccErrorMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "EccErrorMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EccErrorMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
