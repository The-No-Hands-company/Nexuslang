#include <voltron/utility/cloud/azure_diagnostics_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

AzureDiagnosticsHelper& AzureDiagnosticsHelper::instance() {
    static AzureDiagnosticsHelper instance;
    return instance;
}

void AzureDiagnosticsHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AzureDiagnosticsHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AzureDiagnosticsHelper::shutdown() {
    enabled_ = false;
    std::cout << "[AzureDiagnosticsHelper] Shutdown\n";
}

bool AzureDiagnosticsHelper::isEnabled() const {
    return enabled_;
}

void AzureDiagnosticsHelper::enable() {
    enabled_ = true;
}

void AzureDiagnosticsHelper::disable() {
    enabled_ = false;
}

std::string AzureDiagnosticsHelper::getStatus() const {
    std::ostringstream oss;
    oss << "AzureDiagnosticsHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AzureDiagnosticsHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
