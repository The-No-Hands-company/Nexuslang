#include <voltron/utility/reflection/reflection_validator.h>
#include <iostream>

namespace voltron::utility::reflection {

ReflectionValidator& ReflectionValidator::instance() {
    static ReflectionValidator instance;
    return instance;
}

void ReflectionValidator::initialize() {
    enabled_ = true;
    std::cout << "[ReflectionValidator] Initialized\n";
}

void ReflectionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ReflectionValidator] Shutdown\n";
}

bool ReflectionValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
