#include <voltron/utility/i18n/plural_form_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

PluralFormValidator& PluralFormValidator::instance() {
    static PluralFormValidator instance;
    return instance;
}

void PluralFormValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PluralFormValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PluralFormValidator::shutdown() {
    enabled_ = false;
    std::cout << "[PluralFormValidator] Shutdown\n";
}

bool PluralFormValidator::isEnabled() const {
    return enabled_;
}

void PluralFormValidator::enable() {
    enabled_ = true;
}

void PluralFormValidator::disable() {
    enabled_ = false;
}

std::string PluralFormValidator::getStatus() const {
    std::ostringstream oss;
    oss << "PluralFormValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PluralFormValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
