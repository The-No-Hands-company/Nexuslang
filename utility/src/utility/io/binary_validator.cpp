#include <voltron/utility/io/binary_validator.h>
#include <iostream>

namespace voltron::utility::io {

BinaryValidator& BinaryValidator::instance() {
    static BinaryValidator instance;
    return instance;
}

void BinaryValidator::initialize() {
    enabled_ = true;
    std::cout << "[BinaryValidator] Initialized\n";
}

void BinaryValidator::shutdown() {
    enabled_ = false;
    std::cout << "[BinaryValidator] Shutdown\n";
}

bool BinaryValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
