#include <voltron/utility/accessibility/aria_attribute_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

AriaAttributeValidator& AriaAttributeValidator::instance() {
    static AriaAttributeValidator instance;
    return instance;
}

void AriaAttributeValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AriaAttributeValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AriaAttributeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[AriaAttributeValidator] Shutdown\n";
}

bool AriaAttributeValidator::isEnabled() const {
    return enabled_;
}

void AriaAttributeValidator::enable() {
    enabled_ = true;
}

void AriaAttributeValidator::disable() {
    enabled_ = false;
}

std::string AriaAttributeValidator::getStatus() const {
    std::ostringstream oss;
    oss << "AriaAttributeValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AriaAttributeValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
