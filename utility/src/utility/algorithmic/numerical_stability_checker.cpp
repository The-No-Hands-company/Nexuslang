#include <voltron/utility/algorithmic/numerical_stability_checker.h>
#include <iostream>

namespace voltron::utility::algorithmic {

NumericalStabilityChecker& NumericalStabilityChecker::instance() {
    static NumericalStabilityChecker instance;
    return instance;
}

void NumericalStabilityChecker::initialize() {
    enabled_ = true;
}

void NumericalStabilityChecker::shutdown() {
    enabled_ = false;
}

bool NumericalStabilityChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
