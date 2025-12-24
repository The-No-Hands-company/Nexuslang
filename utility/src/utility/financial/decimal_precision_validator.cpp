#include <voltron/utility/financial/decimal_precision_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

DecimalPrecisionValidator& DecimalPrecisionValidator::instance() {
    static DecimalPrecisionValidator instance;
    return instance;
}

void DecimalPrecisionValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DecimalPrecisionValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DecimalPrecisionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[DecimalPrecisionValidator] Shutdown\n";
}

bool DecimalPrecisionValidator::isEnabled() const {
    return enabled_;
}

void DecimalPrecisionValidator::enable() {
    enabled_ = true;
}

void DecimalPrecisionValidator::disable() {
    enabled_ = false;
}

std::string DecimalPrecisionValidator::getStatus() const {
    std::ostringstream oss;
    oss << "DecimalPrecisionValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DecimalPrecisionValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
