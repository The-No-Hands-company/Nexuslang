#include <voltron/utility/security/code_injection_detector.h>
#include <iostream>

namespace voltron::utility::security {

CodeInjectionDetector& CodeInjectionDetector::instance() {
    static CodeInjectionDetector instance;
    return instance;
}

void CodeInjectionDetector::initialize() {
    enabled_ = true;
    std::cout << "[CodeInjectionDetector] Initialized\n";
}

void CodeInjectionDetector::shutdown() {
    enabled_ = false;
    std::cout << "[CodeInjectionDetector] Shutdown\n";
}

bool CodeInjectionDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
