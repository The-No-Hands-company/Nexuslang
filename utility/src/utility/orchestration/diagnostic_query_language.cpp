#include <voltron/utility/orchestration/diagnostic_query_language.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

DiagnosticQueryLanguage& DiagnosticQueryLanguage::instance() {
    static DiagnosticQueryLanguage instance;
    return instance;
}

void DiagnosticQueryLanguage::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DiagnosticQueryLanguage] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DiagnosticQueryLanguage::shutdown() {
    enabled_ = false;
    std::cout << "[DiagnosticQueryLanguage] Shutdown\n";
}

bool DiagnosticQueryLanguage::isEnabled() const {
    return enabled_;
}

void DiagnosticQueryLanguage::enable() {
    enabled_ = true;
}

void DiagnosticQueryLanguage::disable() {
    enabled_ = false;
}

std::string DiagnosticQueryLanguage::getStatus() const {
    std::ostringstream oss;
    oss << "DiagnosticQueryLanguage - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DiagnosticQueryLanguage::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
