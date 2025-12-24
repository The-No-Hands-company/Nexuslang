#include <voltron/utility/apivalidation/parameter_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

ParameterValidator& ParameterValidator::instance() {
    static ParameterValidator instance;
    return instance;
}

void ParameterValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ParameterValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ParameterValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ParameterValidator] Shutdown\n";
}

bool ParameterValidator::isEnabled() const {
    return enabled_;
}

void ParameterValidator::enable() {
    enabled_ = true;
}

void ParameterValidator::disable() {
    enabled_ = false;
}

std::string ParameterValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ParameterValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ParameterValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
