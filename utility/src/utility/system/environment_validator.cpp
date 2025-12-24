#include <voltron/utility/system/environment_validator.h>
#include <iostream>

namespace voltron::utility::system {

EnvironmentValidator& EnvironmentValidator::instance() {
    static EnvironmentValidator instance;
    return instance;
}

void EnvironmentValidator::initialize() {
    enabled_ = true;
    std::cout << "[EnvironmentValidator] Initialized\n";
}

void EnvironmentValidator::shutdown() {
    enabled_ = false;
    std::cout << "[EnvironmentValidator] Shutdown\n";
}

bool EnvironmentValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
