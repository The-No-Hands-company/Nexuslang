#include <voltron/utility/string/normalization_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

NormalizationValidator& NormalizationValidator::instance() {
    static NormalizationValidator instance;
    return instance;
}

void NormalizationValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NormalizationValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NormalizationValidator::shutdown() {
    enabled_ = false;
    std::cout << "[NormalizationValidator] Shutdown\n";
}

bool NormalizationValidator::isEnabled() const {
    return enabled_;
}

void NormalizationValidator::enable() {
    enabled_ = true;
}

void NormalizationValidator::disable() {
    enabled_ = false;
}

std::string NormalizationValidator::getStatus() const {
    std::ostringstream oss;
    oss << "NormalizationValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NormalizationValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
