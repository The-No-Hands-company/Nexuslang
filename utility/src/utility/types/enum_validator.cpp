#include <voltron/utility/types/enum_validator.h>
#include <iostream>

namespace voltron::utility::types {

EnumValidator& EnumValidator::instance() {
    static EnumValidator instance;
    return instance;
}

void EnumValidator::initialize() {
    enabled_ = true;
    std::cout << "[EnumValidator] Initialized\n";
}

void EnumValidator::shutdown() {
    enabled_ = false;
    std::cout << "[EnumValidator] Shutdown\n";
}

bool EnumValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::types
