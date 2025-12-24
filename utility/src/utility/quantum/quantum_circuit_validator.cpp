#include <voltron/utility/quantum/quantum_circuit_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::quantum {

QuantumCircuitValidator& QuantumCircuitValidator::instance() {
    static QuantumCircuitValidator instance;
    return instance;
}

void QuantumCircuitValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[QuantumCircuitValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void QuantumCircuitValidator::shutdown() {
    enabled_ = false;
    std::cout << "[QuantumCircuitValidator] Shutdown\n";
}

bool QuantumCircuitValidator::isEnabled() const {
    return enabled_;
}

void QuantumCircuitValidator::enable() {
    enabled_ = true;
}

void QuantumCircuitValidator::disable() {
    enabled_ = false;
}

std::string QuantumCircuitValidator::getStatus() const {
    std::ostringstream oss;
    oss << "QuantumCircuitValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void QuantumCircuitValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::quantum
