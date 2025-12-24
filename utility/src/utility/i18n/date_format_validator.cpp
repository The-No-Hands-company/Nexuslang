#include <voltron/utility/i18n/date_format_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

DateFormatValidator& DateFormatValidator::instance() {
    static DateFormatValidator instance;
    return instance;
}

void DateFormatValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DateFormatValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DateFormatValidator::shutdown() {
    enabled_ = false;
    std::cout << "[DateFormatValidator] Shutdown\n";
}

bool DateFormatValidator::isEnabled() const {
    return enabled_;
}

void DateFormatValidator::enable() {
    enabled_ = true;
}

void DateFormatValidator::disable() {
    enabled_ = false;
}

std::string DateFormatValidator::getStatus() const {
    std::ostringstream oss;
    oss << "DateFormatValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DateFormatValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
