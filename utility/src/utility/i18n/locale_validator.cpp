#include <voltron/utility/i18n/locale_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

LocaleValidator& LocaleValidator::instance() {
    static LocaleValidator instance;
    return instance;
}

void LocaleValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LocaleValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LocaleValidator::shutdown() {
    enabled_ = false;
    std::cout << "[LocaleValidator] Shutdown\n";
}

bool LocaleValidator::isEnabled() const {
    return enabled_;
}

void LocaleValidator::enable() {
    enabled_ = true;
}

void LocaleValidator::disable() {
    enabled_ = false;
}

std::string LocaleValidator::getStatus() const {
    std::ostringstream oss;
    oss << "LocaleValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LocaleValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
