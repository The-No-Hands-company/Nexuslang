#include <voltron/utility/i18n/unicode_normalization_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

UnicodeNormalizationChecker& UnicodeNormalizationChecker::instance() {
    static UnicodeNormalizationChecker instance;
    return instance;
}

void UnicodeNormalizationChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[UnicodeNormalizationChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void UnicodeNormalizationChecker::shutdown() {
    enabled_ = false;
    std::cout << "[UnicodeNormalizationChecker] Shutdown\n";
}

bool UnicodeNormalizationChecker::isEnabled() const {
    return enabled_;
}

void UnicodeNormalizationChecker::enable() {
    enabled_ = true;
}

void UnicodeNormalizationChecker::disable() {
    enabled_ = false;
}

std::string UnicodeNormalizationChecker::getStatus() const {
    std::ostringstream oss;
    oss << "UnicodeNormalizationChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void UnicodeNormalizationChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
