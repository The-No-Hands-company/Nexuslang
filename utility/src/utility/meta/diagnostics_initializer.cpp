#include <voltron/utility/meta/diagnostics_initializer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

DiagnosticsInitializer& DiagnosticsInitializer::instance() {
    static DiagnosticsInitializer instance;
    return instance;
}

void DiagnosticsInitializer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiagnosticsInitializer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiagnosticsInitializer::shutdown() {
    enabled_ = false;
    std::cout << "[DiagnosticsInitializer] Shutdown\n";
}

bool DiagnosticsInitializer::isEnabled() const {
    return enabled_;
}

void DiagnosticsInitializer::enable() {
    enabled_ = true;
}

void DiagnosticsInitializer::disable() {
    enabled_ = false;
}

std::string DiagnosticsInitializer::getStatus() const {
    std::ostringstream oss;
    oss << "DiagnosticsInitializer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiagnosticsInitializer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
