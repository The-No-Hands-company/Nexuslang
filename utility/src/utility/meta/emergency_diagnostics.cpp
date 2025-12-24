#include <voltron/utility/meta/emergency_diagnostics.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

EmergencyDiagnostics& EmergencyDiagnostics::instance() {
    static EmergencyDiagnostics instance;
    return instance;
}

void EmergencyDiagnostics::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EmergencyDiagnostics] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EmergencyDiagnostics::shutdown() {
    enabled_ = false;
    std::cout << "[EmergencyDiagnostics] Shutdown\n";
}

bool EmergencyDiagnostics::isEnabled() const {
    return enabled_;
}

void EmergencyDiagnostics::enable() {
    enabled_ = true;
}

void EmergencyDiagnostics::disable() {
    enabled_ = false;
}

std::string EmergencyDiagnostics::getStatus() const {
    std::ostringstream oss;
    oss << "EmergencyDiagnostics - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EmergencyDiagnostics::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
