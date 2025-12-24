#include <voltron/utility/financial/audit_trail_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

AuditTrailGenerator& AuditTrailGenerator::instance() {
    static AuditTrailGenerator instance;
    return instance;
}

void AuditTrailGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AuditTrailGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AuditTrailGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[AuditTrailGenerator] Shutdown\n";
}

bool AuditTrailGenerator::isEnabled() const {
    return enabled_;
}

void AuditTrailGenerator::enable() {
    enabled_ = true;
}

void AuditTrailGenerator::disable() {
    enabled_ = false;
}

std::string AuditTrailGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "AuditTrailGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AuditTrailGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
