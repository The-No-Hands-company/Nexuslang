#include <voltron/utility/security/sql_injection_detector.h>
#include <iostream>

namespace voltron::utility::security {

SqlInjectionDetector& SqlInjectionDetector::instance() {
    static SqlInjectionDetector instance;
    return instance;
}

void SqlInjectionDetector::initialize() {
    enabled_ = true;
    std::cout << "[SqlInjectionDetector] Initialized\n";
}

void SqlInjectionDetector::shutdown() {
    enabled_ = false;
    std::cout << "[SqlInjectionDetector] Shutdown\n";
}

bool SqlInjectionDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
