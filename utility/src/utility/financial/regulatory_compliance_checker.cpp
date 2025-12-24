#include <voltron/utility/financial/regulatory_compliance_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

RegulatoryComplianceChecker& RegulatoryComplianceChecker::instance() {
    static RegulatoryComplianceChecker instance;
    return instance;
}

void RegulatoryComplianceChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RegulatoryComplianceChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RegulatoryComplianceChecker::shutdown() {
    enabled_ = false;
    std::cout << "[RegulatoryComplianceChecker] Shutdown\n";
}

bool RegulatoryComplianceChecker::isEnabled() const {
    return enabled_;
}

void RegulatoryComplianceChecker::enable() {
    enabled_ = true;
}

void RegulatoryComplianceChecker::disable() {
    enabled_ = false;
}

std::string RegulatoryComplianceChecker::getStatus() const {
    std::ostringstream oss;
    oss << "RegulatoryComplianceChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RegulatoryComplianceChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
