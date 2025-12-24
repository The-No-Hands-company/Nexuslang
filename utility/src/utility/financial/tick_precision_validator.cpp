#include <voltron/utility/financial/tick_precision_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

TickPrecisionValidator& TickPrecisionValidator::instance() {
    static TickPrecisionValidator instance;
    return instance;
}

void TickPrecisionValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TickPrecisionValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TickPrecisionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[TickPrecisionValidator] Shutdown\n";
}

bool TickPrecisionValidator::isEnabled() const {
    return enabled_;
}

void TickPrecisionValidator::enable() {
    enabled_ = true;
}

void TickPrecisionValidator::disable() {
    enabled_ = false;
}

std::string TickPrecisionValidator::getStatus() const {
    std::ostringstream oss;
    oss << "TickPrecisionValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TickPrecisionValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
