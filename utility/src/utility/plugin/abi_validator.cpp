#include <voltron/utility/plugin/abi_validator.h>
#include <iostream>

namespace voltron::utility::plugin {

AbiValidator& AbiValidator::instance() {
    static AbiValidator instance;
    return instance;
}

void AbiValidator::initialize() {
    enabled_ = true;
}

void AbiValidator::shutdown() {
    enabled_ = false;
}

bool AbiValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
