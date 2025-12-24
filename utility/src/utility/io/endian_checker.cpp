#include <voltron/utility/io/endian_checker.h>
#include <iostream>

namespace voltron::utility::io {

EndianChecker& EndianChecker::instance() {
    static EndianChecker instance;
    return instance;
}

void EndianChecker::initialize() {
    enabled_ = true;
    std::cout << "[EndianChecker] Initialized\n";
}

void EndianChecker::shutdown() {
    enabled_ = false;
    std::cout << "[EndianChecker] Shutdown\n";
}

bool EndianChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
