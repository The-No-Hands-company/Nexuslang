#include <voltron/utility/license/license_header_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

LicenseHeaderValidator& LicenseHeaderValidator::instance() {
    static LicenseHeaderValidator instance;
    return instance;
}

void LicenseHeaderValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LicenseHeaderValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LicenseHeaderValidator::shutdown() {
    enabled_ = false;
    std::cout << "[LicenseHeaderValidator] Shutdown\n";
}

bool LicenseHeaderValidator::isEnabled() const {
    return enabled_;
}

void LicenseHeaderValidator::enable() {
    enabled_ = true;
}

void LicenseHeaderValidator::disable() {
    enabled_ = false;
}

std::string LicenseHeaderValidator::getStatus() const {
    std::ostringstream oss;
    oss << "LicenseHeaderValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LicenseHeaderValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
