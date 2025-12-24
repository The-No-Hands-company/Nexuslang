#include <voltron/utility/embedded/determinism_validator.h>
#include <iostream>

namespace voltron::utility::embedded {

DeterminismValidator& DeterminismValidator::instance() {
    static DeterminismValidator instance;
    return instance;
}

void DeterminismValidator::initialize() {
    enabled_ = true;
}

void DeterminismValidator::shutdown() {
    enabled_ = false;
}

bool DeterminismValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
