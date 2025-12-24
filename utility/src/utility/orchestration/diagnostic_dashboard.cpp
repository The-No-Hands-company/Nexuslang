#include <voltron/utility/orchestration/diagnostic_dashboard.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

DiagnosticDashboard& DiagnosticDashboard::instance() {
    static DiagnosticDashboard instance;
    return instance;
}

void DiagnosticDashboard::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiagnosticDashboard] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiagnosticDashboard::shutdown() {
    enabled_ = false;
    std::cout << "[DiagnosticDashboard] Shutdown\n";
}

bool DiagnosticDashboard::isEnabled() const {
    return enabled_;
}

void DiagnosticDashboard::enable() {
    enabled_ = true;
}

void DiagnosticDashboard::disable() {
    enabled_ = false;
}

std::string DiagnosticDashboard::getStatus() const {
    std::ostringstream oss;
    oss << "DiagnosticDashboard - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiagnosticDashboard::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
