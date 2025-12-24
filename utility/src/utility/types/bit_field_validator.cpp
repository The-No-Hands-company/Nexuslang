#include <voltron/utility/types/bit_field_validator.h>
#include <iostream>

namespace voltron::utility::types {

BitFieldValidator& BitFieldValidator::instance() {
    static BitFieldValidator instance;
    return instance;
}

void BitFieldValidator::initialize() {
    enabled_ = true;
    std::cout << "[BitFieldValidator] Initialized\n";
}

void BitFieldValidator::shutdown() {
    enabled_ = false;
    std::cout << "[BitFieldValidator] Shutdown\n";
}

bool BitFieldValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::types
