#include <voltron/utility/license/license_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

LicenseValidator& LicenseValidator::instance() {
    static LicenseValidator instance;
    return instance;
}

void LicenseValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LicenseValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LicenseValidator::shutdown() {
    enabled_ = false;
    std::cout << "[LicenseValidator] Shutdown\n";
}

bool LicenseValidator::isEnabled() const {
    return enabled_;
}

void LicenseValidator::enable() {
    enabled_ = true;
}

void LicenseValidator::disable() {
    enabled_ = false;
}

std::string LicenseValidator::getStatus() const {
    std::ostringstream oss;
    oss << "LicenseValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LicenseValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
