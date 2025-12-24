#include <voltron/utility/security/secure_wipe.h>
#include <iostream>

namespace voltron::utility::security {

SecureWipe& SecureWipe::instance() {
    static SecureWipe instance;
    return instance;
}

void SecureWipe::initialize() {
    enabled_ = true;
    std::cout << "[SecureWipe] Initialized\n";
}

void SecureWipe::shutdown() {
    enabled_ = false;
    std::cout << "[SecureWipe] Shutdown\n";
}

bool SecureWipe::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
