#include <voltron/utility/security/secret_leak_detector.h>
#include <iostream>

namespace voltron::utility::security {

SecretLeakDetector& SecretLeakDetector::instance() {
    static SecretLeakDetector instance;
    return instance;
}

void SecretLeakDetector::initialize() {
    enabled_ = true;
    std::cout << "[SecretLeakDetector] Initialized\n";
}

void SecretLeakDetector::shutdown() {
    enabled_ = false;
    std::cout << "[SecretLeakDetector] Shutdown\n";
}

bool SecretLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
