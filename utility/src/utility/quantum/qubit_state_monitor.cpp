#include <voltron/utility/quantum/qubit_state_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::quantum {

QubitStateMonitor& QubitStateMonitor::instance() {
    static QubitStateMonitor instance;
    return instance;
}

void QubitStateMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[QubitStateMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void QubitStateMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[QubitStateMonitor] Shutdown\n";
}

bool QubitStateMonitor::isEnabled() const {
    return enabled_;
}

void QubitStateMonitor::enable() {
    enabled_ = true;
}

void QubitStateMonitor::disable() {
    enabled_ = false;
}

std::string QubitStateMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "QubitStateMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void QubitStateMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::quantum
