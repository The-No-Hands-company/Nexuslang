#include <voltron/utility/sanitizer/asan_interface.h>
#include <iostream>

namespace voltron::utility::sanitizer {

AsanInterface& AsanInterface::instance() {
    static AsanInterface instance;
    return instance;
}

void AsanInterface::initialize() {
    enabled_ = true;
    std::cout << "[AsanInterface] Initialized\n";
}

void AsanInterface::shutdown() {
    enabled_ = false;
    std::cout << "[AsanInterface] Shutdown\n";
}

bool AsanInterface::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::sanitizer
