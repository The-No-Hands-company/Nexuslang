#include <voltron/utility/chaos/memory_pressure_simulator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

MemoryPressureSimulator& MemoryPressureSimulator::instance() {
    static MemoryPressureSimulator instance;
    return instance;
}

void MemoryPressureSimulator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MemoryPressureSimulator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MemoryPressureSimulator::shutdown() {
    enabled_ = false;
    std::cout << "[MemoryPressureSimulator] Shutdown\n";
}

bool MemoryPressureSimulator::isEnabled() const {
    return enabled_;
}

void MemoryPressureSimulator::enable() {
    enabled_ = true;
}

void MemoryPressureSimulator::disable() {
    enabled_ = false;
}

std::string MemoryPressureSimulator::getStatus() const {
    std::ostringstream oss;
    oss << "MemoryPressureSimulator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MemoryPressureSimulator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
