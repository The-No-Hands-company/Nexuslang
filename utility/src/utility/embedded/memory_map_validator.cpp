#include <voltron/utility/embedded/memory_map_validator.h>
#include <iostream>

namespace voltron::utility::embedded {

MemoryMapValidator& MemoryMapValidator::instance() {
    static MemoryMapValidator instance;
    return instance;
}

void MemoryMapValidator::initialize() {
    enabled_ = true;
}

void MemoryMapValidator::shutdown() {
    enabled_ = false;
}

bool MemoryMapValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
