#include <voltron/utility/chaos/dependency_failure_simulator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

DependencyFailureSimulator& DependencyFailureSimulator::instance() {
    static DependencyFailureSimulator instance;
    return instance;
}

void DependencyFailureSimulator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DependencyFailureSimulator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DependencyFailureSimulator::shutdown() {
    enabled_ = false;
    std::cout << "[DependencyFailureSimulator] Shutdown\n";
}

bool DependencyFailureSimulator::isEnabled() const {
    return enabled_;
}

void DependencyFailureSimulator::enable() {
    enabled_ = true;
}

void DependencyFailureSimulator::disable() {
    enabled_ = false;
}

std::string DependencyFailureSimulator::getStatus() const {
    std::ostringstream oss;
    oss << "DependencyFailureSimulator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DependencyFailureSimulator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
