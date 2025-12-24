#include <voltron/utility/apivalidation/string_format_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

StringFormatValidator& StringFormatValidator::instance() {
    static StringFormatValidator instance;
    return instance;
}

void StringFormatValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StringFormatValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StringFormatValidator::shutdown() {
    enabled_ = false;
    std::cout << "[StringFormatValidator] Shutdown\n";
}

bool StringFormatValidator::isEnabled() const {
    return enabled_;
}

void StringFormatValidator::enable() {
    enabled_ = true;
}

void StringFormatValidator::disable() {
    enabled_ = false;
}

std::string StringFormatValidator::getStatus() const {
    std::ostringstream oss;
    oss << "StringFormatValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StringFormatValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
