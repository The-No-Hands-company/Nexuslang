#include <voltron/utility/accessibility/keyboard_navigation_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

KeyboardNavigationValidator& KeyboardNavigationValidator::instance() {
    static KeyboardNavigationValidator instance;
    return instance;
}

void KeyboardNavigationValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[KeyboardNavigationValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void KeyboardNavigationValidator::shutdown() {
    enabled_ = false;
    std::cout << "[KeyboardNavigationValidator] Shutdown\n";
}

bool KeyboardNavigationValidator::isEnabled() const {
    return enabled_;
}

void KeyboardNavigationValidator::enable() {
    enabled_ = true;
}

void KeyboardNavigationValidator::disable() {
    enabled_ = false;
}

std::string KeyboardNavigationValidator::getStatus() const {
    std::ostringstream oss;
    oss << "KeyboardNavigationValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void KeyboardNavigationValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
