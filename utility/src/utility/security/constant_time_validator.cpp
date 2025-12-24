#include <voltron/utility/security/constant_time_validator.h>
#include <iostream>

namespace voltron::utility::security {

ConstantTimeValidator& ConstantTimeValidator::instance() {
    static ConstantTimeValidator instance;
    return instance;
}

void ConstantTimeValidator::initialize() {
    enabled_ = true;
    std::cout << "[ConstantTimeValidator] Initialized\n";
}

void ConstantTimeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ConstantTimeValidator] Shutdown\n";
}

bool ConstantTimeValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
