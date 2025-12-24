#include <voltron/utility/quantum/quantum_error_corrector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::quantum {

QuantumErrorCorrector& QuantumErrorCorrector::instance() {
    static QuantumErrorCorrector instance;
    return instance;
}

void QuantumErrorCorrector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[QuantumErrorCorrector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void QuantumErrorCorrector::shutdown() {
    enabled_ = false;
    std::cout << "[QuantumErrorCorrector] Shutdown\n";
}

bool QuantumErrorCorrector::isEnabled() const {
    return enabled_;
}

void QuantumErrorCorrector::enable() {
    enabled_ = true;
}

void QuantumErrorCorrector::disable() {
    enabled_ = false;
}

std::string QuantumErrorCorrector::getStatus() const {
    std::ostringstream oss;
    oss << "QuantumErrorCorrector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void QuantumErrorCorrector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::quantum
