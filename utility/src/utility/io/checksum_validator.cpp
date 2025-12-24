#include <voltron/utility/io/checksum_validator.h>
#include <iostream>

namespace voltron::utility::io {

ChecksumValidator& ChecksumValidator::instance() {
    static ChecksumValidator instance;
    return instance;
}

void ChecksumValidator::initialize() {
    enabled_ = true;
    std::cout << "[ChecksumValidator] Initialized\n";
}

void ChecksumValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ChecksumValidator] Shutdown\n";
}

bool ChecksumValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
