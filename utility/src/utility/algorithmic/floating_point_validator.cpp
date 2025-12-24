#include <voltron/utility/algorithmic/floating_point_validator.h>
#include <iostream>

namespace voltron::utility::algorithmic {

FloatingPointValidator& FloatingPointValidator::instance() {
    static FloatingPointValidator instance;
    return instance;
}

void FloatingPointValidator::initialize() {
    enabled_ = true;
}

void FloatingPointValidator::shutdown() {
    enabled_ = false;
}

bool FloatingPointValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
