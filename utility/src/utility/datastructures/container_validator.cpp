#include <voltron/utility/datastructures/container_validator.h>
#include <iostream>

namespace voltron::utility::datastructures {

ContainerValidator& ContainerValidator::instance() {
    static ContainerValidator instance;
    return instance;
}

void ContainerValidator::initialize() {
    enabled_ = true;
    std::cout << "[ContainerValidator] Initialized\n";
}

void ContainerValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ContainerValidator] Shutdown\n";
}

bool ContainerValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::datastructures
