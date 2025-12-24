#include <voltron/utility/types/range_validator.h>
#include <iostream>

namespace voltron::utility::types {

RangeValidator& RangeValidator::instance() {
    static RangeValidator instance;
    return instance;
}

void RangeValidator::initialize() {
    enabled_ = true;
    std::cout << "[RangeValidator] Initialized\n";
}

void RangeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[RangeValidator] Shutdown\n";
}

bool RangeValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::types
