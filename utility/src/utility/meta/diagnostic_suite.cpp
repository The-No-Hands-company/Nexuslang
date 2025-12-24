#include <voltron/utility/meta/diagnostic_suite.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

DiagnosticSuite& DiagnosticSuite::instance() {
    static DiagnosticSuite instance;
    return instance;
}

void DiagnosticSuite::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiagnosticSuite] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiagnosticSuite::shutdown() {
    enabled_ = false;
    std::cout << "[DiagnosticSuite] Shutdown\n";
}

bool DiagnosticSuite::isEnabled() const {
    return enabled_;
}

void DiagnosticSuite::enable() {
    enabled_ = true;
}

void DiagnosticSuite::disable() {
    enabled_ = false;
}

std::string DiagnosticSuite::getStatus() const {
    std::ostringstream oss;
    oss << "DiagnosticSuite - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiagnosticSuite::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
