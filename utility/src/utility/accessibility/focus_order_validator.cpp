#include <voltron/utility/accessibility/focus_order_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

FocusOrderValidator& FocusOrderValidator::instance() {
    static FocusOrderValidator instance;
    return instance;
}

void FocusOrderValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FocusOrderValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FocusOrderValidator::shutdown() {
    enabled_ = false;
    std::cout << "[FocusOrderValidator] Shutdown\n";
}

bool FocusOrderValidator::isEnabled() const {
    return enabled_;
}

void FocusOrderValidator::enable() {
    enabled_ = true;
}

void FocusOrderValidator::disable() {
    enabled_ = false;
}

std::string FocusOrderValidator::getStatus() const {
    std::ostringstream oss;
    oss << "FocusOrderValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FocusOrderValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
