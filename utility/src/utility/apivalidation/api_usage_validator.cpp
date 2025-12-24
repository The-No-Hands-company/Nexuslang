#include <voltron/utility/apivalidation/api_usage_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

ApiUsageValidator& ApiUsageValidator::instance() {
    static ApiUsageValidator instance;
    return instance;
}

void ApiUsageValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ApiUsageValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ApiUsageValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ApiUsageValidator] Shutdown\n";
}

bool ApiUsageValidator::isEnabled() const {
    return enabled_;
}

void ApiUsageValidator::enable() {
    enabled_ = true;
}

void ApiUsageValidator::disable() {
    enabled_ = false;
}

std::string ApiUsageValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ApiUsageValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ApiUsageValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
