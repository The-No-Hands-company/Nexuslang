#include <voltron/utility/safety/traceability_matrix_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

TraceabilityMatrixGenerator& TraceabilityMatrixGenerator::instance() {
    static TraceabilityMatrixGenerator instance;
    return instance;
}

void TraceabilityMatrixGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TraceabilityMatrixGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TraceabilityMatrixGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[TraceabilityMatrixGenerator] Shutdown\n";
}

bool TraceabilityMatrixGenerator::isEnabled() const {
    return enabled_;
}

void TraceabilityMatrixGenerator::enable() {
    enabled_ = true;
}

void TraceabilityMatrixGenerator::disable() {
    enabled_ = false;
}

std::string TraceabilityMatrixGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "TraceabilityMatrixGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TraceabilityMatrixGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
