#include <voltron/utility/security/input_sanitizer.h>
#include <iostream>

namespace voltron::utility::security {

InputSanitizer& InputSanitizer::instance() {
    static InputSanitizer instance;
    return instance;
}

void InputSanitizer::initialize() {
    enabled_ = true;
    std::cout << "[InputSanitizer] Initialized\n";
}

void InputSanitizer::shutdown() {
    enabled_ = false;
    std::cout << "[InputSanitizer] Shutdown\n";
}

bool InputSanitizer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
