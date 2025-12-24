#include <voltron/utility/assertions/postcondition.h>
#include <iostream>

namespace voltron::utility::assertions {

Postcondition& Postcondition::instance() {
    static Postcondition instance;
    return instance;
}

void Postcondition::initialize() {
    enabled_ = true;
    std::cout << "[Postcondition] Initialized\n";
}

void Postcondition::shutdown() {
    enabled_ = false;
    std::cout << "[Postcondition] Shutdown\n";
}

bool Postcondition::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::assertions
