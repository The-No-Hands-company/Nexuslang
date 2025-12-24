#include <voltron/utility/scientific/simulation_stability_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

SimulationStabilityMonitor& SimulationStabilityMonitor::instance() {
    static SimulationStabilityMonitor instance;
    return instance;
}

void SimulationStabilityMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SimulationStabilityMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SimulationStabilityMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[SimulationStabilityMonitor] Shutdown\n";
}

bool SimulationStabilityMonitor::isEnabled() const {
    return enabled_;
}

void SimulationStabilityMonitor::enable() {
    enabled_ = true;
}

void SimulationStabilityMonitor::disable() {
    enabled_ = false;
}

std::string SimulationStabilityMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "SimulationStabilityMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SimulationStabilityMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
