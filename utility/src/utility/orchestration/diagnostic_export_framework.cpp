#include <voltron/utility/orchestration/diagnostic_export_framework.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

DiagnosticExportFramework& DiagnosticExportFramework::instance() {
    static DiagnosticExportFramework instance;
    return instance;
}

void DiagnosticExportFramework::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiagnosticExportFramework] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiagnosticExportFramework::shutdown() {
    enabled_ = false;
    std::cout << "[DiagnosticExportFramework] Shutdown\n";
}

bool DiagnosticExportFramework::isEnabled() const {
    return enabled_;
}

void DiagnosticExportFramework::enable() {
    enabled_ = true;
}

void DiagnosticExportFramework::disable() {
    enabled_ = false;
}

std::string DiagnosticExportFramework::getStatus() const {
    std::ostringstream oss;
    oss << "DiagnosticExportFramework - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiagnosticExportFramework::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
