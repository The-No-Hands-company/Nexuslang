#include <voltron/utility/algorithmic/sorting_validator.h>
#include <iostream>

namespace voltron::utility::algorithmic {

SortingValidator& SortingValidator::instance() {
    static SortingValidator instance;
    return instance;
}

void SortingValidator::initialize() {
    enabled_ = true;
}

void SortingValidator::shutdown() {
    enabled_ = false;
}

bool SortingValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
