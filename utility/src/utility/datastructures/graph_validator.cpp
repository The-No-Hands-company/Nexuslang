#include <voltron/utility/datastructures/graph_validator.h>
#include <iostream>

namespace voltron::utility::datastructures {

GraphValidator& GraphValidator::instance() {
    static GraphValidator instance;
    return instance;
}

void GraphValidator::initialize() {
    enabled_ = true;
    std::cout << "[GraphValidator] Initialized\n";
}

void GraphValidator::shutdown() {
    enabled_ = false;
    std::cout << "[GraphValidator] Shutdown\n";
}

bool GraphValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::datastructures
